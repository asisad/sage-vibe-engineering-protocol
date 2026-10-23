#!/usr/bin/env python3
"""Offline ECC discovery and source-packet adapter. Never executes source content.

Catalog records describe capabilities; they grant no execution authority. This
module intentionally uses only the Python standard library and never installs
native agents, hooks, dependencies or provider settings.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import unicodedata
from urllib.parse import unquote, urlparse


SCHEMA = "sage-ecc/0.1"
MAX_FILE_BYTES = 16 * 1024 * 1024
MAX_PACKET_BYTES = 128 * 1024 * 1024
MAX_SELECTED = 32
MAX_RESOURCES = 512
DECISIONS = {"ADD", "ENHANCE", "REFERENCE_ONLY", "KEEP"}
EXECUTION_CLASSES = {"read_only", "local_change", "external_action", "orchestration", "host_configuration"}
CORE_NAMES = ("sage-intake", "sage-discover", "sage-plan", "sage-implement", "sage-verify")
ID_PATTERN = re.compile(r"^(ecc|sage)\.(skill|agent)\.[a-z0-9][a-z0-9._-]*$")
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class IntegrationError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise IntegrationError(code, message)


def relative_parts(value: str) -> tuple[str, ...]:
    require(isinstance(value, str) and bool(value), "INVALID_PATH", "A non-empty repository-relative path is required.")
    require("\\" not in value and ":" not in value and "\x00" not in value, "INVALID_PATH", f"Unsafe path: {value!r}")
    parts = value.split("/")
    require(not PurePosixPath(value).is_absolute() and all(p not in ("", ".", "..") for p in parts), "INVALID_PATH", f"Unsafe path: {value!r}")
    return tuple(parts)


def repository_slug(value: str) -> str:
    require(isinstance(value, str), "INVALID_PROVENANCE", "Repository provenance must be a string.")
    if value.startswith("https://github.com/"):
        value = value[len("https://github.com/"):].rstrip("/")
    if value.endswith(".git"):
        value = value[:-4]
    require(re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", value) is not None, "INVALID_PROVENANCE", "Repository provenance must name an owner/repository.")
    return value.lower()


def reject_symlinks(path: Path) -> None:
    """Reject existing symlink components, including a dangling final symlink."""
    for component in (path, *path.parents):
        try:
            info = component.lstat()
        except FileNotFoundError:
            continue
        reparse_point = getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        require(not stat.S_ISLNK(info.st_mode) and not reparse_point, "SYMLINK_DENIED", f"Symlink/reparse paths are not accepted: {component}")


def read_bounded(path: Path, remaining_bytes: int | None = None) -> bytes:
    reject_symlinks(path)
    try:
        info = path.stat()
        require(stat.S_ISREG(info.st_mode), "INVALID_SOURCE", f"Source is not a regular file: {path}")
        require(info.st_size <= MAX_FILE_BYTES, "LIMIT_EXCEEDED", f"Source exceeds the file-size limit: {path}")
        require(remaining_bytes is None or info.st_size <= remaining_bytes, "LIMIT_EXCEEDED", "Selected packet exceeds the byte limit.")
        read_limit = MAX_FILE_BYTES if remaining_bytes is None else min(MAX_FILE_BYTES, remaining_bytes)
        with path.open("rb") as handle:
            content = handle.read(read_limit + 1)
        require(len(content) <= MAX_FILE_BYTES, "LIMIT_EXCEEDED", f"Source exceeds the file-size limit: {path}")
        require(remaining_bytes is None or len(content) <= remaining_bytes, "LIMIT_EXCEEDED", "Selected packet exceeds the byte limit.")
        return content
    except OSError as exc:
        raise IntegrationError("SOURCE_UNAVAILABLE", f"Cannot read source {path}: {exc.strerror}") from exc


def json_object(content: bytes, label: str) -> dict:
    try:
        value = json.loads(content.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise IntegrationError("INVALID_JSON", f"Invalid UTF-8 JSON in {label}.") from exc
    require(isinstance(value, dict), "INVALID_JSON", f"{label} must be a JSON object.")
    return value


def flatten(value) -> str:
    if isinstance(value, dict):
        return " ".join(flatten(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(flatten(v) for v in value)
    return value if isinstance(value, str) else ""


STOPWORDS = set("a an and are as at be build by can code create do engineering for from in is it make me of on or please project task the this to use using want with write i we my our help add implement improve fix review برای یک با این را می کن بکن ساخت پروژه ایجاد کد در به از و یا آن من ما لطفا میخواهم می‌خواهم مهندسی ها های کار انجام بده کنید کردن".split())
ALIASES = {
    "پایتون": ("python",), "تایپ‌اسکریپت": ("typescript",), "تایپاسکریپت": ("typescript",),
    "جاوااسکریپت": ("javascript",), "امنیت": ("security",), "امنیتی": ("security",),
    "تست": ("test", "testing"), "آزمون": ("test", "testing"), "آزمایش": ("test", "testing"),
    "دیتابیس": ("database", "sql"), "وب": ("web",), "فرانت": ("frontend",),
    "بکاند": ("backend",), "داکر": ("docker",), "رندر": ("rendering",),
}


def normalized_words(text: str) -> list[str]:
    normalized = unicodedata.normalize("NFKC", text).lower().replace("ي", "ی").replace("ك", "ک").replace("\u200c", " ")
    return re.findall(r"[\w+#]+", normalized.replace("_", " "))


NORMALIZED_ALIASES = {" ".join(normalized_words(alias)): values for alias, values in ALIASES.items()}


def tokens(text: str) -> set[str]:
    words = normalized_words(text)
    result = {t for t in words if t not in STOPWORDS and (len(t) > 1 or t in ("c", "r"))}
    phrases = " " + " ".join(words) + " "
    for alias, values in NORMALIZED_ALIASES.items():
        if " " + alias + " " in phrases:
            result.update(values)
    return result


def assumptions(content: str) -> dict[str, str]:
    """Expose declarations as text, never interpret YAML or grant permissions."""
    if not content.startswith("---\n"):
        return {}
    frontmatter = content[4:].split("\n---", 1)[0]
    result = {}
    for line in frontmatter.splitlines():
        match = re.match(r"^(model|tools|permissionMode|mcpServers|skills):\s*(.*)$", line)
        if match:
            result[match.group(1)] = match.group(2) or "Declared as a multiline value; inspect source."
    return result


class Catalog:
    def __init__(self, repo_root: Path | str | None = None, catalog_path: Path | str | None = None):
        root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[2]
        reject_symlinks(root.absolute())
        self.root = root.resolve()
        self.managed_roots = {self.root, Path(__file__).resolve().parents[2]}
        require(self.root.is_dir(), "INVALID_ROOT", "The repository root must exist.")
        path = Path(catalog_path) if catalog_path is not None else self.root / "extensions/ecc/catalog.json"
        if not path.is_absolute():
            path = self.root / path
        reject_symlinks(path.absolute())
        self.path = path.resolve()
        require(self.path.is_relative_to(self.root), "INVALID_PATH", "The catalog must be inside the supplied repository root.")
        self.document = json_object(read_bounded(self.path), "catalog")
        require(self.document.get("schema_version") == SCHEMA, "INVALID_CATALOG", f"Expected schema_version {SCHEMA}.")
        sources = self.document.get("sources")
        require(isinstance(sources, dict) and bool(sources), "INVALID_PROVENANCE", "Catalog source pins are missing.")
        self.pins = {}
        for source in sources.values():
            require(isinstance(source, dict), "INVALID_PROVENANCE", "Each source pin must be an object.")
            slug = repository_slug(source.get("repository"))
            commit = source.get("commit", "")
            require(isinstance(commit, str) and bool(COMMIT_PATTERN.fullmatch(commit)), "INVALID_PROVENANCE", "Source pins require a full lowercase commit SHA.")
            require(slug not in self.pins or self.pins[slug] == commit, "INVALID_PROVENANCE", f"Conflicting pins for {slug}.")
            self.pins[slug] = commit
        entries = self.document.get("entries")
        require(isinstance(entries, list), "INVALID_CATALOG", "Catalog entries must be an array.")
        self.entries = {}
        for entry in entries:
            self._validate_entry(entry)
            require(entry["id"] not in self.entries, "INVALID_CATALOG", f"Duplicate entry ID: {entry['id']}")
            self.entries[entry["id"]] = entry
        self.notices = self.document.get("notices", [])
        require(isinstance(self.notices, list), "INVALID_CATALOG", "Catalog notices must be an array.")
        notice_paths = set()
        for notice in self.notices:
            require(isinstance(notice, dict), "INVALID_CATALOG", "Each notice must be an object.")
            relative_parts(notice.get("local_path"))
            require(isinstance(notice.get("origin"), str) and notice["origin"] in ("ECC", "SAGE", "ALL"), "INVALID_CATALOG", "Notice origin must be ECC, SAGE or ALL.")
            require(notice.get("license") is None or isinstance(notice["license"], str), "INVALID_CATALOG", "Notice license must be a string when present.")
            require(isinstance(notice.get("sha256"), str) and bool(HASH_PATTERN.fullmatch(notice["sha256"])), "INVALID_PROVENANCE", "Each notice must declare its content hash.")
            require(notice["local_path"] not in notice_paths, "INVALID_CATALOG", "Duplicate notice path.")
            notice_paths.add(notice["local_path"])

    def _validate_entry(self, entry: dict) -> None:
        require(isinstance(entry, dict), "INVALID_CATALOG", "Catalog entries must be objects.")
        identifier = entry.get("id", "")
        require(isinstance(identifier, str) and bool(ID_PATTERN.fullmatch(identifier)), "INVALID_CATALOG", "Invalid namespaced entry ID.")
        require(isinstance(entry.get("kind"), str) and entry["kind"] in ("skill", "agent") and identifier.split(".")[1] == entry["kind"], "INVALID_CATALOG", f"Kind/ID mismatch: {identifier}")
        require(isinstance(entry.get("origin"), str) and entry["origin"] in ("ECC", "SAGE") and identifier.startswith(entry["origin"].lower() + "."), "INVALID_CATALOG", f"Origin/ID mismatch: {identifier}")
        require(isinstance(entry.get("decision"), str) and entry["decision"] in DECISIONS, "INVALID_CATALOG", f"Invalid disposition: {identifier}")
        require(isinstance(entry.get("execution_class"), str) and entry["execution_class"] in EXECUTION_CLASSES, "INVALID_CATALOG", f"Invalid execution class: {identifier}")
        require(isinstance(entry.get("name"), str) and bool(entry["name"]) and isinstance(entry.get("description"), str), "INVALID_CATALOG", f"Missing name or description: {identifier}")
        targets = entry.get("sage_targets", [])
        require(isinstance(targets, list) and all(isinstance(target, str) and bool(target) for target in targets), "INVALID_CATALOG", f"SAGE targets must be an array of skill names: {identifier}")
        require(len(set(targets)) == len(targets), "INVALID_CATALOG", f"Duplicate SAGE targets: {identifier}")
        review = entry.get("review", {})
        require(isinstance(review, dict) and review.get("method") == "STATIC" and review.get("execution_verified") is False, "INVALID_CATALOG", f"Catalog must disclose static, unexecuted review: {identifier}")
        source = entry.get("source")
        require(isinstance(source, dict), "INVALID_PROVENANCE", f"Missing source: {identifier}")
        slug = repository_slug(source.get("repository"))
        commit = source.get("commit")
        require(slug in self.pins and commit == self.pins[slug], "INVALID_PROVENANCE", f"Commit does not match the pinned source: {identifier}")
        require(isinstance(source.get("sha256"), str) and bool(HASH_PATTERN.fullmatch(source["sha256"])), "INVALID_PROVENANCE", f"Missing source SHA256: {identifier}")
        relative_parts(source.get("path"))
        relative_parts(entry.get("local_path"))
        require(isinstance(source.get("url"), str), "INVALID_PROVENANCE", f"Missing source URL: {identifier}")
        try:
            url = urlparse(source["url"])
        except ValueError as exc:
            raise IntegrationError("INVALID_PROVENANCE", f"Invalid source URL: {identifier}") from exc
        actual = unquote(url.path).split("/", 5)
        pinned_path = len(actual) == 6 and (actual[1] + "/" + actual[2]).lower() == slug and actual[3] == "blob" and actual[4] == commit and actual[5] == source["path"]
        require(url.scheme == "https" and url.netloc == "github.com" and pinned_path and not url.query and not url.fragment, "INVALID_PROVENANCE", f"Source URL must identify the exact pinned file: {identifier}")
        resources = entry.get("resources", [])
        require(isinstance(resources, list) and len(resources) <= MAX_RESOURCES, "INVALID_CATALOG", f"Invalid or excessive resource list: {identifier}")
        skill_parent = PurePosixPath(source["path"]).parent
        resource_paths = set()
        for resource in resources:
            require(isinstance(resource, dict), "INVALID_CATALOG", f"Invalid resource: {identifier}")
            relative_parts(resource.get("local_path"))
            relative_parts(resource.get("source_path"))
            resource_path = PurePosixPath(resource["source_path"])
            require(entry["kind"] == "skill" and skill_parent != PurePosixPath(".") and resource_path.is_relative_to(skill_parent) and resource_path != PurePosixPath(source["path"]), "INVALID_PATH", f"Resource must be within its selected skill folder: {identifier}")
            require(resource["source_path"] not in resource_paths, "INVALID_CATALOG", f"Duplicate resource path: {identifier}")
            resource_paths.add(resource["source_path"])
            require(isinstance(resource.get("sha256"), str) and bool(HASH_PATTERN.fullmatch(resource["sha256"])), "INVALID_PROVENANCE", f"Missing resource SHA256: {identifier}")

    def get(self, identifier: str, active: bool = False) -> dict:
        require(isinstance(identifier, str), "INVALID_INPUT", "A catalog ID must be a string.")
        require(identifier in self.entries, "UNKNOWN_ID", f"Unknown catalog ID: {identifier}")
        entry = self.entries[identifier]
        require(not active or entry["decision"] != "REFERENCE_ONLY", "REFERENCE_ONLY", f"Reference-only entry cannot enter an active packet: {identifier}")
        return entry

    def _content(self, local_path: str, expected_hash: str, remaining_bytes: int | None = None) -> bytes:
        path = self.root.joinpath(*relative_parts(local_path))
        reject_symlinks(path)
        require(path.resolve().is_relative_to(self.root), "INVALID_PATH", "Source escaped the repository root.")
        content = read_bounded(path, remaining_bytes)
        actual = hashlib.sha256(content).hexdigest()
        require(actual == expected_hash, "HASH_MISMATCH", f"SHA256 mismatch for {local_path}.")
        return content

    def verified_source(self, entry: dict, remaining_bytes: int | None = None) -> tuple[bytes, str]:
        is_profile = entry["origin"] == "SAGE" and entry["kind"] == "agent" and entry["source"]["path"].endswith(".json")
        # A profile packet contains only its projection; the full source document
        # is independently bounded by MAX_FILE_BYTES while its hash is verified.
        if is_profile:
            require(remaining_bytes is None or remaining_bytes > 0, "LIMIT_EXCEEDED", "Selected packet exceeds the byte limit.")
        content = self._content(entry["local_path"], entry["source"]["sha256"], None if is_profile else remaining_bytes)
        try:
            content.decode("utf-8")
        except UnicodeError as exc:
            raise IntegrationError("INVALID_SOURCE", f"Entrypoint is not UTF-8 text: {entry['id']}") from exc
        representation = "verbatim_source"
        if is_profile:
            document = json_object(content, entry["id"])
            profiles = document.get("profiles", [])
            require(isinstance(profiles, list), "INVALID_SOURCE", "Native specialist profiles must be an array.")
            matches = [p for p in profiles if isinstance(p, dict) and p.get("profile_id") == entry["name"]]
            require(len(matches) == 1, "INVALID_SOURCE", f"Expected one matching native specialist profile: {entry['id']}")
            if remaining_bytes is None:
                content = (json.dumps(matches[0], ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            else:
                projection = bytearray()
                for chunk in json.JSONEncoder(ensure_ascii=False, indent=2).iterencode(matches[0]):
                    encoded = chunk.encode("utf-8")
                    require(len(projection) + len(encoded) + 1 <= remaining_bytes, "LIMIT_EXCEEDED", "Selected packet exceeds the byte limit.")
                    projection.extend(encoded)
                projection.extend(b"\n")
                content = bytes(projection)
            representation = "selected_profile_projection"
        require(remaining_bytes is None or len(content) <= remaining_bytes, "LIMIT_EXCEEDED", "Selected packet exceeds the byte limit.")
        return content, representation

    @staticmethod
    def summary(entry: dict) -> dict:
        keys = ("id", "kind", "name", "description", "origin", "domain", "profile", "decision", "sage_targets", "rationale_fa", "improvement_fa", "execution_class", "boundaries", "source", "local_path", "review", "dependency_flags", "references", "license", "license_scope", "contract_ref")
        result = {key: entry[key] for key in keys if key in entry}
        result["resource_count"] = len(entry.get("resources", []))
        return result

    def list_entries(self, **filters) -> list[dict]:
        return [self.summary(e) for e in sorted(self.entries.values(), key=lambda row: row["id"]) if all(not value or e.get(key) == value for key, value in filters.items())]

    def search(self, query: str, limit: int = 20, active: bool = False) -> list[dict]:
        query_tokens = tokens(query)
        if not query_tokens:
            return []
        ranked = []
        for entry in self.entries.values():
            if active and (entry["decision"] == "REFERENCE_ONLY" or entry["name"] in CORE_NAMES):
                continue
            score = 0
            matched = set()
            for field, weight in (("name", 8), ("domain", 6), ("description", 3), ("rationale_fa", 1), ("improvement_fa", 1)):
                overlap = query_tokens & tokens(flatten(entry.get(field, "")))
                score += len(overlap) * weight
                matched.update(overlap)
            if score:
                ranked.append((score, entry["id"], sorted(matched), entry))
        ranked.sort(key=lambda item: (-item[0], item[1]))
        return [dict(self.summary(entry), score=score, matched_terms=matched) for score, _, matched, entry in ranked[:limit]]

    def show(self, identifier: str) -> dict:
        entry = self.get(identifier)
        content, representation = self.verified_source(entry)
        text = content.decode("utf-8")
        return dict(self.summary(entry), source_content=text, representation=representation, declared_native_assumptions=assumptions(text), source_integrity_verified=True, resources=entry.get("resources", []), resources_loaded=False)

    def plan(self, task: str, scope: str | None = None, risk: str | None = None, limit: int = 6) -> dict:
        require(bool(task.strip()), "INVALID_INPUT", "A non-empty task is required.")
        require(1 <= limit <= 12, "LIMIT_EXCEEDED", "Plans support between 1 and 12 candidates.")
        candidates = self.search(task, limit=limit, active=True)
        lifecycle = []
        missing = []
        verified_ids = set()
        for name in CORE_NAMES:
            identifier = "sage.skill." + name
            if identifier not in self.entries or self.entries[identifier]["decision"] == "REFERENCE_ONLY":
                missing.append(identifier)
            else:
                self.verified_source(self.entries[identifier])
                verified_ids.add(identifier)
                lifecycle.append({"id": identifier, "role": name.removeprefix("sage-"), "authority": "existing_sage_contract_only"})
        for candidate in candidates:
            self.verified_source(self.entries[candidate["id"]])
            verified_ids.add(candidate["id"])
            candidate["source_integrity_verified"] = True
        mapped_candidates = {}
        for candidate in candidates:
            if candidate["origin"] != "ECC":
                continue
            for target in candidate.get("sage_targets", []):
                identifier = target if target.startswith("sage.skill.") else "sage.skill." + target
                if identifier in missing:
                    continue
                target_entry = self.get(identifier, active=True)
                if identifier not in verified_ids:
                    self.verified_source(target_entry)
                    verified_ids.add(identifier)
                ids = mapped_candidates.setdefault(identifier, [])
                if candidate["id"] not in ids:
                    ids.append(candidate["id"])
        enhancements = [
            {"sage_skill_id": identifier, "ecc_candidate_ids": ids, "source": self.entries[identifier]["source"], "source_integrity_verified": True}
            for identifier, ids in sorted(mapped_candidates.items())
        ]
        status = "NEEDS_CLARIFICATION" if not candidates else ("BLOCKED" if missing else "ADVISORY_PLAN")
        return {
            "status": status, "task": task, "scope": scope, "risk": risk,
            "risk_basis": "caller_supplied_unverified" if risk else "not_classified",
            "scope_basis": "caller_supplied_unverified" if scope else "not_supplied",
            "execution_authorized": False, "execution_performed": False,
            "routing_method": "deterministic_metadata_token_overlap", "candidate_limit": limit,
            "lifecycle": lifecycle, "missing_governance": missing, "candidates": candidates,
            "enhancements": enhancements,
            "evidence_role": "sage.skill.sage-verify",
            "independent_review_required": risk in ("R3", "R4"),
            "clarification": "Specify the technology, domain or concrete outcome; no capability matched." if not candidates else None,
            "limitations": ["Routing is advisory, not proof of capability or permission.", "Source hashes verify local integrity against pinned metadata, not upstream authenticity or runtime success.", "External actions and native provider execution require an independently authorized SAGE execution session."],
        }

    def bundle(self, identifiers: list[str], output: Path | str, provider: str = "generic", task: str | None = None, scope: str | None = None, risk: str | None = None) -> dict:
        require(isinstance(provider, str) and provider in ("generic", "codex", "claude"), "INVALID_INPUT", "Unsupported provider.")
        require(isinstance(identifiers, (list, tuple)) and all(isinstance(identifier, str) for identifier in identifiers), "INVALID_INPUT", "Select a list of catalog ID strings.")
        require(bool(identifiers) and len(identifiers) <= MAX_SELECTED, "LIMIT_EXCEEDED", f"Select between 1 and {MAX_SELECTED} explicit IDs.")
        require(len(set(identifiers)) == len(identifiers), "INVALID_INPUT", "Duplicate IDs are not accepted.")
        destination = self._destination(output)
        payloads = []
        selected = []
        total = 0

        def retain_payload(path: str, content: bytes) -> None:
            nonlocal total
            require(len(content) <= MAX_PACKET_BYTES - total, "LIMIT_EXCEEDED", "Selected packet exceeds the byte limit.")
            payloads.append((path, content))
            total += len(content)

        for identifier in identifiers:
            entry = self.get(identifier, active=True)
            content, representation = self.verified_source(entry, MAX_PACKET_BYTES - total)
            subdir = ("skills" if entry["kind"] == "skill" else "agents") + "/" + identifier
            filename = "profile.json" if representation == "selected_profile_projection" else PurePosixPath(entry["source"]["path"]).name
            target = subdir + "/" + filename
            retain_payload(target, content)
            copied_resources = []
            for resource in entry.get("resources", []):
                resource_content = self._content(resource["local_path"], resource["sha256"], MAX_PACKET_BYTES - total)
                suffix = str(PurePosixPath(resource["source_path"]).relative_to(PurePosixPath(entry["source"]["path"]).parent))
                resource_target = subdir + "/" + suffix
                require(resource_target != target, "INVALID_PATH", "Resource collides with the entrypoint.")
                retain_payload(resource_target, resource_content)
                copied_resources.append(dict(resource, packet_path=resource_target, treatment="data_only_not_executed"))
            selected.append(dict(self.summary(entry), packet_path=target, representation=representation, packet_sha256=hashlib.sha256(content).hexdigest(), declared_native_assumptions=assumptions(content.decode("utf-8")), resources=copied_resources, source_integrity_verified=True))
        selected_origins = {entry["origin"] for entry in selected}
        selected_licenses = " ".join(flatten(entry.get("license", "")) + " " + flatten(entry["source"].get("license", "")) for entry in selected)
        notices = [notice for notice in self.notices if (notice["origin"] in selected_origins or notice["origin"] == "ALL") and (not notice.get("license") or notice["license"] == "MIT" or notice["license"] in selected_licenses)]
        if "ECC" in selected_origins:
            notice_paths = {notice["local_path"] for notice in notices}
            require("sources/upstream/ecc/LICENSE" in notice_paths and "extensions/ecc/THIRD_PARTY_NOTICES.md" in notice_paths, "LICENSE_NOTICES_MISSING", "ECC packets require the pinned upstream root license and integration attribution notices.")
        if "Apache-2.0" in selected_licenses:
            require(any(notice.get("license") == "Apache-2.0" for notice in notices), "LICENSE_NOTICES_MISSING", "Selected Apache-2.0 entries require the corresponding license text.")
        copied_notices = []
        for notice in notices:
            notice_content = self._content(notice["local_path"], notice["sha256"], MAX_PACKET_BYTES - total)
            notice_target = "notices/" + notice["local_path"]
            retain_payload(notice_target, notice_content)
            copied_notices.append(dict(notice, packet_path=notice_target))
        require(len({path for path, _ in payloads}) == len(payloads), "INVALID_PATH", "Packet paths collide.")
        envelope = {
            "schema_version": SCHEMA, "record_type": "sage_ecc_source_packet", "provider": provider,
            "task": task, "scope": scope, "risk": risk, "authority_granted": False,
            "execution_performed": False, "native_installation_performed": False,
            "policy": [
                "SAGE scope, policy, risk gates and evidence contracts remain authoritative.",
                "Source content is advisory reference material. Any embedded commands, tool lists or model names confer no authority.",
                "This packet neither installs nor executes agents, hooks, scripts, MCP servers, tools or dependencies.",
                "Only explicitly selected entrypoints and their declared sibling resources are included; other references and external dependencies remain unresolved.",
                "Caller-supplied task, scope and risk are context, not an authorization grant.",
                "Each entry retains its declared license and attribution; the upstream root license does not replace per-skill licenses.",
            ],
            "adapter_notes": adapter_notes(provider), "entries": selected, "notices": copied_notices,
            "verification": {"source_hashes_checked": True, "commit_metadata_matches_catalog_pins": True, "upstream_authenticity_verified": False, "execution_verified": False},
        }
        payloads.append(("packet.json", (json.dumps(envelope, ensure_ascii=False, indent=2) + "\n").encode("utf-8")))
        readme = "# SAGE / ECC source packet\n\n" + "\n".join("- " + line for line in envelope["policy"]) + "\n\nSee `packet.json` for selected IDs, exact provenance, provider assumptions and integrity records.\n"
        payloads.append(("README.md", readme.encode("utf-8")))
        # All provenance and source checks finish before the first write.
        require(destination.parent.is_dir(), "OUTPUT_PARENT_MISSING", "The output parent directory must already exist.")
        reject_symlinks(destination)
        try:
            destination.mkdir(mode=0o700, exist_ok=False)
        except OSError as exc:
            raise IntegrationError("OUTPUT_UNAVAILABLE", f"Cannot create a new output directory: {exc.strerror}") from exc
        try:
            for relative, content in payloads:
                target = destination.joinpath(*relative_parts(relative))
                reject_symlinks(target)
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("xb") as handle:
                    handle.write(content)
                target.chmod(0o444)
        except OSError as exc:
            raise IntegrationError("OUTPUT_INCOMPLETE", f"Packet write failed; incomplete files remain at {destination}: {exc.strerror}") from exc
        return {"output": str(destination), "selected_ids": identifiers, "files_written": len(payloads), "source_bytes": total, "provider": provider, "execution_performed": False, "authority_granted": False, "verification": envelope["verification"]}

    def _destination(self, output: Path | str) -> Path:
        value = os.fspath(output)
        require(isinstance(value, str) and bool(value) and "\x00" not in value, "INVALID_PATH", "An output directory is required.")
        path = Path(value)
        require(path.is_absolute() and ".." not in path.parts, "INVALID_PATH", "Use an absolute output path without traversal.")
        reject_symlinks(path)
        resolved = path.resolve()
        require(all(not resolved.is_relative_to(root) and not root.is_relative_to(resolved) for root in self.managed_roots), "MANAGED_PATH_DENIED", "Export outside the managed repository tree.")
        require(not path.exists(), "OUTPUT_EXISTS", "The output directory must be new; existing paths are never overwritten.")
        return resolved


def adapter_notes(provider: str) -> list[str]:
    notes = ["A source packet is not a native provider installation.", "Declared model/tool values are retained as source assumptions and require mapping to actually available, authorized capabilities.", "No global configuration, hooks, AGENTS.md or CLAUDE.md is modified."]
    if provider == "codex":
        notes.append("Claude-specific model names, tool names and hook events are not Codex bindings; native Codex roles/skills require a separately reviewed adapter and SAGE metadata sidecar.")
    elif provider == "claude":
        notes.append("Claude frontmatter is preserved as reference text; no .claude directory, plugin, slash command, model or tool permission is installed or enabled.")
    else:
        notes.append("Generic execution requires an explicit provider adapter preserving SAGE scope, authority, result and evidence contracts.")
    return notes


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise IntegrationError("INVALID_ARGUMENTS", message)


def make_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", default=argparse.SUPPRESS)
    common.add_argument("--repo-root", default=argparse.SUPPRESS)
    common.add_argument("--catalog", default=argparse.SUPPRESS)
    parser = Parser(description=__doc__, parents=[common])
    commands = parser.add_subparsers(dest="command", required=True, parser_class=Parser)
    listing = commands.add_parser("list", parents=[common], help="List catalog metadata only.")
    listing.add_argument("--origin", choices=("ECC", "SAGE"))
    listing.add_argument("--kind", choices=("skill", "agent"))
    listing.add_argument("--decision", choices=sorted(DECISIONS))
    listing.add_argument("--profile", choices=("engineering", "domain", "operations", "meta"))
    search = commands.add_parser("search", parents=[common], help="Search metadata without loading source bodies.")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=20)
    show = commands.add_parser("show", parents=[common], help="Verify and display one source entry.")
    show.add_argument("id")
    plan = commands.add_parser("plan", parents=[common], help="Produce an advisory, bounded routing plan.")
    plan.add_argument("--task", required=True)
    plan.add_argument("--scope")
    plan.add_argument("--risk", choices=["R" + str(i) for i in range(5)])
    plan.add_argument("--limit", type=int, default=6)
    bundle = commands.add_parser("bundle", aliases=["export"], parents=[common], help="Export explicit IDs as inert reference files.")
    bundle.add_argument("--ids", nargs="+", required=True)
    bundle.add_argument("--output", required=True)
    bundle.add_argument("--provider", choices=("generic", "codex", "claude"), default="generic")
    bundle.add_argument("--task")
    bundle.add_argument("--scope")
    bundle.add_argument("--risk", choices=["R" + str(i) for i in range(5)])
    return parser


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    json_mode = "--json" in argv
    command = None
    try:
        args = make_parser().parse_args(argv)
        command = args.command
        catalog = Catalog(getattr(args, "repo_root", None), getattr(args, "catalog", None))
        if command == "list":
            data = {"entries": catalog.list_entries(origin=args.origin, kind=args.kind, decision=args.decision, profile=args.profile), "source_bodies_loaded": False}
        elif command == "search":
            require(1 <= args.limit <= 100, "LIMIT_EXCEEDED", "Search supports between 1 and 100 results.")
            data = {"query": args.query, "entries": catalog.search(args.query, args.limit), "source_bodies_loaded": False}
        elif command == "show":
            data = catalog.show(args.id)
        elif command == "plan":
            data = catalog.plan(args.task, args.scope, args.risk, args.limit)
        else:
            data = catalog.bundle(args.ids, args.output, args.provider, args.task, args.scope, args.risk)
        response = {"ok": True, "schema_version": SCHEMA, "command": command, "execution_authorized": False, "data": data}
        result = 2 if command == "plan" and data["status"] != "ADVISORY_PLAN" else 0
    except IntegrationError as exc:
        response = {"ok": False, "schema_version": SCHEMA, "command": command, "execution_authorized": False, "error": {"code": exc.code, "message": str(exc)}}
        result = 2
    except OSError as exc:
        response = {"ok": False, "schema_version": SCHEMA, "command": command, "execution_authorized": False, "error": {"code": "IO_ERROR", "message": str(exc)}}
        result = 2
    if json_mode:
        # Escaped JSON survives redirected stdout with non-UTF-8 encodings.
        print(json.dumps(response, ensure_ascii=True))
    elif response["ok"]:
        print(json.dumps(response["data"], ensure_ascii=False, indent=2))
    else:
        print(f"{response['error']['code']}: {response['error']['message']}", file=sys.stderr)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
