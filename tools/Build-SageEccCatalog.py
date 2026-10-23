#!/usr/bin/env python3
"""Build the pinned, offline ECC source catalog without executing upstream code.

All imported instructions are source data. This builder never invokes an ECC
installer, hook, agent, helper, package manager, or network request.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import html
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "extensions/ecc"
VENDOR = ROOT / "sources/upstream/ecc"
ECC_REPO = "affaan-m/ECC"
SAGE_REPO = "asisad/sage-vibe-engineering-protocol"
ECC_COMMIT = "90606c8315ee09cafc303515c5f33024db6b9882"
SAGE_COMMIT = "46e65164f726d902d360b3be341bd6f35171c982"
SCHEMA = "sage-ecc/0.1"
SOURCE_DIRS = ("agents", "skills", "commands", "rules", "hooks", "scripts",
               "mcp-configs", "contexts", "config", "schemas", "manifests",
               "src", "workflows", "integrations", "plugins", ".codex",
               ".codex-plugin")
SOURCE_FILES = ("LICENSE", "VERSION", "README.md", "SECURITY.md", "CHANGELOG.md",
                "the-shortform-guide.md", "the-longform-guide.md",
                "the-security-guide.md", "COMMANDS-QUICK-REF.md",
                "package.json", "package-lock.json", "agent.yaml", ".mcp.json")
SOURCE_DOCS = ("CODEX-NAVIGATION-GUIDE.md", "COMMAND-AGENT-MAP.md")
PATTERNS = {
    "host_configuration": r"~/\.(?:claude|codex|cursor)|CLAUDE_PLUGIN_ROOT|CODEX_HOME|settings\.json|hooks\.json",
    "provider_specific": r"\b(?:Claude Code|Codex CLI|claude -p|claude --|mcp__\w+|opus|sonnet|haiku)\b",
    "external_actions": r"\bgit push\b|\bgh (?:pr|issue|repo) create\b|\b(?:publish|send_email|send_message|deploy)\b",
    "destructive_command_examples": r"\brm\s+-[rf]+\b|git reset --hard|git clean -[a-z]*[fd]|DROP (?:TABLE|DATABASE)",
    "approval_override_examples": r"dangerously-skip-permissions|\bauto.approv\w*|\byolo\b|bypass.*approval|approval.*bypass",
    "network_install_examples": r"\bcurl\b.{0,160}\|\s*(?:bash|sh)|\bnpx\s+\S+@latest|\bpip install\b|\bnpm install\b",
    "fixed_quality_threshold": r"80%|80\s*percent|coverage.{0,40}(?:>=|≥)\s*80",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def git_head(path: Path) -> str:
    return subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()


def frontmatter(text: str) -> dict:
    """Extract ordinary scalar metadata only; never evaluate YAML or tags."""
    if not text.startswith("---\n"):
        return {}
    pieces = text.split("---", 2)
    if len(pieces) != 3:
        return {}
    result = {}
    lines = pieces[1].splitlines()
    for i, line in enumerate(lines):
        match = re.match(r"^([\w-]+):\s*(.*)$", line)
        if not match:
            continue
        key, value = match.groups()
        if value in ("|", ">", "|-", ">-", "|+", ">+"):
            continuation = []
            for follow in lines[i + 1:]:
                if follow and not follow[0].isspace():
                    break
                continuation.append(follow.strip())
            value = " ".join(continuation).strip()
        elif value[:1] in ("'", '"') and value[-1:] == value[:1]:
            value = value[1:-1]
        result[key] = value
    return result


def scan_text(text: str) -> dict:
    results = {}
    for flag, pattern in PATTERNS.items():
        hits = []
        for number, line in enumerate(text.splitlines(), 1):
            if re.search(pattern, line, flags=re.I):
                hits.append({"line": number, "excerpt": line[:220]})
        if hits:
            results[flag] = {"count": len(hits), "examples": hits[:3]}
    return results


def import_sources(upstream: Path) -> tuple[list, list]:
    if git_head(upstream) != ECC_COMMIT:
        raise ValueError("Upstream HEAD does not equal the reviewed ECC pin")
    if subprocess.check_output(["git", "-C", str(upstream), "status", "--porcelain", "--untracked-files=no"]):
        raise ValueError("Upstream checkout has tracked changes; pinned originals are required")
    tracked = subprocess.check_output(["git", "-C", str(upstream), "ls-files", "-z"])
    all_files = [p.decode("utf-8") for p in tracked.split(b"\0") if p]
    # Rebuild is allowed only in this dedicated, generated vendor subtree.
    if VENDOR.exists():
        if VENDOR.is_symlink():
            raise ValueError("Vendor root must not be a symlink")
        shutil.rmtree(VENDOR)
    inventory, scans = [], []
    for relative in sorted(all_files):
        source = upstream / relative
        if source.is_symlink() or not source.is_file():
            raise ValueError(f"Unsupported upstream file type: {relative}")
        data = source.read_bytes()
        parts = Path(relative).parts
        selected = (parts[0] in SOURCE_DIRS or relative in SOURCE_FILES or
                    relative in ["docs/" + p for p in SOURCE_DOCS])
        record = {"path": relative, "sha256": digest(data), "bytes": len(data),
                  "disposition": "VENDORED_SOURCE_ONLY" if selected else "UPSTREAM_REFERENCE_ONLY"}
        if selected:
            target = VENDOR / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            # Source examples and scripts remain non-executable repository data.
            target.chmod(0o644)
            try:
                body = data.decode("utf-8")
            except UnicodeDecodeError:
                record["text"] = False
            else:
                record["text"] = True
                findings = scan_text(body)
                scans.append({"path": relative, "sha256": record["sha256"],
                              "lines": len(body.splitlines()), "signals": findings})
        inventory.append(record)
    return inventory, scans


def source_record(origin: str, path: str, data: bytes) -> dict:
    repo, commit = ((ECC_REPO, ECC_COMMIT) if origin == "ECC" else (SAGE_REPO, SAGE_COMMIT))
    return {"repository": repo, "commit": commit, "path": path,
            "url": f"https://github.com/{repo}/blob/{commit}/{path}", "sha256": digest(data)}


def native_catalog() -> list:
    entries = []
    advisory_names = {"sage-intake", "sage-discover", "sage-plan", "sage-verify",
                      "cli-harness-review", "interface-audit", "mcp-review",
                      "docs-knowledge", "emerging-language-research", "technology-selection"}
    external_names = {"automation-iac", "cnc-gcode", "devops-containers", "embedded-iot", "robotics-motion"}
    skill_paths = sorted((ROOT / "skills").glob("*/SKILL.md"))
    skill_paths += sorted((ROOT / "extensions/technology-engineering/skills").glob("*/SKILL.md"))
    for path in skill_paths:
        data = path.read_bytes()
        meta = frontmatter(data.decode("utf-8"))
        name = path.parent.name
        rel = path.relative_to(ROOT).as_posix()
        if subprocess.check_output(["git", "-C", str(ROOT), "show", f"{SAGE_COMMIT}:{rel}"]) != data:
            raise ValueError(f"Native SAGE source differs from baseline pin: {rel}")
        entries.append({
            "id": f"sage.skill.{name}", "kind": "skill", "name": name,
            "description": meta.get("description", name), "origin": "SAGE",
            "domain": name, "profile": "engineering", "decision": "KEEP",
            "sage_targets": [], "rationale_fa": "مهارت موجود سیج؛ هویت و مسئولیت فعلی حفظ می‌شود.",
            "improvement_fa": "تخصص‌های مکمل ECC از طریق رابطهٔ تقویت به این مهارت متصل می‌شوند.",
            "execution_class": ("read_only" if name in advisory_names else
                                "external_action" if name in external_names else "local_change"),
            "local_path": rel, "source": source_record("SAGE", rel, data),
            "review": {"method": "STATIC", "execution_verified": False},
            "dependency_flags": [], "boundaries": ["SAGE task scope and evidence contract apply"],
            "resources": [],
            "license": "MIT", "license_scope": "SAGE repository license",
        })
    path = ROOT / "extensions/technology-engineering/specialists.json"
    data = path.read_bytes()
    rel = path.relative_to(ROOT).as_posix()
    if subprocess.check_output(["git", "-C", str(ROOT), "show", f"{SAGE_COMMIT}:{rel}"]) != data:
        raise ValueError("SAGE specialist profiles differ from baseline pin")
    for profile in json.loads(data)["profiles"]:
        name = profile["profile_id"]
        entries.append({
            "id": f"sage.agent.{name}", "kind": "agent", "name": name,
            "description": ", ".join(profile["capabilities"]), "origin": "SAGE",
            "domain": profile["kind"].lower(), "profile": "engineering", "decision": "KEEP",
            "sage_targets": [], "rationale_fa": "پروفایل متخصص موجود سیج؛ اجرای زنده با وجود تعریف یکسان نیست.",
            "improvement_fa": "تعریف‌های بازبین و رفع خطای ECC به صورت نقش مکمل قابل انتخاب‌اند.",
            "execution_class": "local_change", "local_path": rel,
            "source": source_record("SAGE", rel, data),
            "review": {"method": "STATIC", "execution_verified": False},
            "dependency_flags": [], "boundaries": ["ON_DEMAND; native execution_verified remains false"],
            "resources": [],
            "license": "MIT", "license_scope": "SAGE repository license",
        })
    return entries


def build_entries(reviews: list, kind: str, scans: dict) -> list:
    entries = []
    for review in sorted(reviews, key=lambda item: item["name"]):
        name = review["name"]
        relative = f"skills/{name}/SKILL.md" if kind == "skill" else f"agents/{name}.md"
        path = VENDOR / relative
        data = path.read_bytes()
        meta = frontmatter(data.decode("utf-8"))
        resources = []
        if kind == "skill":
            for resource in sorted(path.parent.rglob("*")):
                if resource.is_file() and resource != path:
                    resources.append({"local_path": resource.relative_to(ROOT).as_posix(),
                                      "source_path": resource.relative_to(VENDOR).as_posix(),
                                      "sha256": digest(resource.read_bytes())})
        flags = set(scans.get(relative, {}).get("signals", {}))
        for resource in resources:
            flags.update(scans.get(resource["source_path"], {}).get("signals", {}))
        entries.append({
            "id": f"ecc.{kind}.{name}", "kind": kind, "name": name,
            "description": meta.get("description", name), "origin": "ECC",
            "domain": review["domain"], "profile": review["profile"],
            "decision": review["decision"], "sage_targets": review["sage_targets"],
            "rationale_fa": review["rationale_fa"], "improvement_fa": review["improvement_fa"],
            "execution_class": review["execution_class"],
            "local_path": path.relative_to(ROOT).as_posix(),
            "source": source_record("ECC", relative, data),
            "review": {"method": "STATIC", "execution_verified": False},
            "dependency_flags": sorted(flags), "boundaries": review.get("boundaries", []),
            "native_model_hint": meta.get("model"), "native_tools_hint": meta.get("tools"),
            "license": meta.get("license", "MIT"),
            "license_scope": "skill-local declaration takes precedence over upstream root license",
            "resources": resources,
        })
    return entries


def require_complete(reviews: list, expected: set, label: str) -> None:
    names = [item["name"] for item in reviews]
    if len(names) != len(set(names)) or set(names) != expected:
        raise ValueError(f"{label} review coverage mismatch: missing={sorted(expected-set(names))}, "
                         f"extra={sorted(set(names)-expected)}, duplicated={len(names)-len(set(names))}")
    for item in reviews:
        for key in ("name", "domain", "decision", "sage_targets", "rationale_fa", "improvement_fa", "profile", "execution_class"):
            if key not in item:
                raise ValueError(f"Missing {key} in {label}/{item['name']}")
        if item["decision"] not in ("ADD", "ENHANCE", "REFERENCE_ONLY"):
            raise ValueError(f"Unsupported decision {item['decision']}")


def reports(catalog: dict, inventory: list, scans: list) -> None:
    entries = catalog["entries"]
    lines = ["# SAGE × ECC — ماتریس کامل تطبیق", "", "این جدول تمام تعریف‌های اصلی ECC در Commit قفل‌شده را پوشش می‌دهد.",
             "بررسی ایستا و تصمیم معماری، مدرک اجرای مهارت یا اثبات برتری عملکرد نیست.", "",
             f"- ECC: `{ECC_COMMIT}`", f"- SAGE baseline: `{SAGE_COMMIT}`", "",
             "| نوع | نام | تصمیم | اتصال به سیج | دلیل و ارزش افزوده |", "|---|---|---|---|---|"]
    for entry in entries:
        if entry["origin"] != "ECC":
            continue
        clean = lambda value: str(value).replace("|", "\\|").replace("\n", " ")
        lines.append("| " + " | ".join(clean(x) for x in (
            entry["kind"], f"[{entry['name']}]({entry['source']['url']})", entry["decision"],
            ", ".join(entry["sage_targets"]) or "—", entry["rationale_fa"] + " " + entry["improvement_fa"])) + " |")
    (EXT / "review").mkdir(parents=True, exist_ok=True)
    (EXT / "review/OVERLAP-MATRIX.fa.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    grouped = collections.defaultdict(list)
    for entry in entries:
        if entry["origin"] == "ECC":
            for target in entry["sage_targets"]:
                grouped[target].append(entry["id"])
    write_json(EXT / "enhancements.json", {"schema_version": SCHEMA,
               "meaning": "complementary source candidates, not automatic replacement or benchmark wins",
               "targets": [{"sage_skill": key, "ecc_candidates": value} for key, value in sorted(grouped.items())]})
    by_root = collections.Counter(Path(row["path"]).parts[0] for row in inventory)
    write_json(EXT / "review/component-dispositions.json", {
        "canonical_entries": {"skills": 311, "agents": 71},
        "root_file_counts": dict(sorted(by_root.items())),
        "decisions": [
            {"surface": "skills/ + agents/", "decision": "PER_ITEM_MAPPED", "reason": "All canonical definitions and skill-local resources are packaged as attributed source."},
            {"surface": "commands/", "decision": "REFERENCE_ONLY", "reason": "Slash commands depend on host; reuse through selected skills, not a second SAGE lifecycle."},
            {"surface": "rules/", "decision": "REFERENCE_ONLY", "reason": "SAGE governing policies and dynamic quality gates remain authoritative."},
            {"surface": "hooks/ + scripts/", "decision": "INERT_SOURCE", "reason": "Included for inspection and dependency traceability; no automatic installation or execution."},
            {"surface": "MCP/provider manifests", "decision": "REFERENCE_ONLY", "reason": "Endpoint credentials, host compatibility and permissions are not provisioned by catalog import."},
            {"surface": "memory/orchestration/learning", "decision": "ADAPT_IDEAS", "reason": "No independent control plane or memory store is automatically installed."},
            {"surface": "translations/editor copies/assets/tests", "decision": "UPSTREAM_REFERENCE_ONLY", "reason": "Excluded duplicate/marketing/runtime-test surfaces remain individually inventoried by hash; not counted as new skills."},
        ],
    })
    write_json(EXT / "review/static-scan.json", {
        "method": "full-text pattern scan of every vendored UTF-8 source; examples are signals, not vulnerability findings",
        "files_scanned": len(scans), "patterns": PATTERNS, "files": scans,
        "security_certified": False, "upstream_scripts_executed": False,
    })


def descriptors(entries: list) -> dict:
    """Portable sidecars in one registry; native upstream files stay unchanged."""
    result = []
    for entry in entries:
        result.append({
            "schema_version": SCHEMA, "id": entry["id"], "version": "0.1.0",
            "title": entry["name"], "description": entry["description"],
            "intents": [entry["description"]], "domains": [entry["domain"]],
            "risk_range": {"min": "R0", "max": "R4", "classification_owner": "SAGE", "classification_performed": False},
            "invocation_policy": "forbidden_in_environment" if entry["decision"] == "REFERENCE_ONLY" else "explicit",
            "inputs": {"required": ["task", "scope", "target_context"], "optional": ["risk_class", "existing_authorization", "evidence_refs"]},
            "outputs": ["scoped_artifact_or_findings", "actual_check_results", "evidence_refs", "limitations", "unresolved_items"],
            "preconditions": ["source_hash_verified", "scope_clear", "required_tools_observed", "applicable_authorization_present"],
            "side_effects": {"potential_class": entry["execution_class"], "execution_by_catalog": False},
            "permissions": {"granted": [], "checked_at_invocation": True,
                            "existing_authorization_reused": True, "policy_owner": "SAGE"},
            "required_capabilities": ["source-context-reader"],
            "optional_capabilities": entry["dependency_flags"],
            "tools": {"native_hints": entry.get("native_tools_hint"), "resolved_tools": [], "binding_verified": False},
            "context_requirements": "Load only selected entry and necessary resources; native instructions are subordinate source material.",
            "procedure_ref": entry["local_path"],
            "evidence_contract": "extensions/ecc/policy.json#/evidence_contract",
            "failure_modes": ["INVALID_INPUT", "PERMISSION_DENIED", "TOOL_UNAVAILABLE", "VERIFICATION_FAILED", "UNSUPPORTED_CASE", "BUDGET_EXHAUSTED"],
            "retry_policy": {"automatic": False},
            "stop_conditions": ["task_complete", "scope_conflict", "missing_authority", "missing_tool", "budget_exhausted"],
            "compatibility": {"generic": "source_packet", "codex": "source_packet_not_native_install", "claude": "source_packet_not_native_install"},
            "native_bindings": {"installed": False, "model_hint": entry.get("native_model_hint")},
        })
        entry["contract_ref"] = "extensions/ecc/descriptors.json#" + entry["id"]
    return {"schema_version": SCHEMA, "architecture_owner": "SAGE", "descriptors": result}


def web_catalog(catalog: dict) -> None:
    template = (EXT / "catalog.template.html").read_text(encoding="utf-8")
    # Metadata only: do not dump source bodies or resources into every page view.
    view_entries = [{k: v for k, v in row.items() if k not in ("resources",)} for row in catalog["entries"]]
    data = json.dumps({"summary": catalog["summary"], "sources": catalog["sources"], "entries": view_entries}, ensure_ascii=False)
    data = data.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    output = ROOT / "docs/catalog/index.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(template.replace("__SAGE_CATALOG_DATA__", data), encoding="utf-8")


def build(upstream: Path) -> None:
    skill_reviews = json.loads((EXT / "review/skills.json").read_text(encoding="utf-8"))
    agent_reviews = json.loads((EXT / "review/agents.json").read_text(encoding="utf-8"))
    require_complete(skill_reviews, {p.parent.name for p in (upstream / "skills").glob("*/SKILL.md")}, "skills")
    require_complete(agent_reviews, {p.stem for p in (upstream / "agents").glob("*.md")}, "agents")
    inventory, scans = import_sources(upstream)
    scan_map = {entry["path"]: entry for entry in scans}
    entries = native_catalog() + build_entries(skill_reviews, "skill", scan_map) + build_entries(agent_reviews, "agent", scan_map)
    native_names = {e["name"] for e in entries if e["origin"] == "SAGE" and e["kind"] == "skill"}
    for entry in entries:
        invalid = set(entry["sage_targets"]) - native_names
        if invalid:
            raise ValueError(f"Unknown SAGE targets for {entry['id']}: {invalid}")
    write_json(EXT / "descriptors.json", descriptors(entries))
    catalog = {
        "schema_version": SCHEMA, "catalog_id": "sage.ecc-capabilities", "version": "0.1.0",
        "reviewed_at": "2026-10-23", "sources": {
            "ECC": {"repository": ECC_REPO, "commit": ECC_COMMIT, "version": (upstream / "VERSION").read_text().strip(), "license": "MIT with skill-local Apache-2.0 and CC-BY-SA-4.0 exceptions"},
            "SAGE": {"repository": SAGE_REPO, "commit": SAGE_COMMIT, "version": "0.8.4-source"},
        },
        "summary": {
            "ecc_skills": len(skill_reviews), "ecc_agents": len(agent_reviews),
            "sage_skills": sum(e["origin"] == "SAGE" and e["kind"] == "skill" for e in entries),
            "sage_agents": sum(e["origin"] == "SAGE" and e["kind"] == "agent" for e in entries),
            "definitions": len(entries), "decisions": dict(collections.Counter(e["decision"] for e in entries)),
            "vendored_files": sum(e["disposition"] == "VENDORED_SOURCE_ONLY" for e in inventory),
            "upstream_files_inventoried": len(inventory), "execution_verified_definitions": 0,
        },
        "authority_granted": False, "external_execution": False,
        "review_scope": "All canonical definitions mapped; supporting vendored source scanned statically. No claim of per-skill functional certification.",
        "entries": sorted(entries, key=lambda e: e["id"]),
        "notices": [{"local_path": p, "sha256": digest((ROOT / p).read_bytes()), "origin": origin, **({"license": license_name} if license_name else {})}
                    for p, origin, license_name in (
                        ("sources/upstream/ecc/LICENSE", "ECC", "MIT"),
                        ("extensions/ecc/THIRD_PARTY_NOTICES.md", "ALL", None),
                        ("extensions/ecc/licenses/Apache-2.0.txt", "ECC", "Apache-2.0"),
                        ("LICENSE", "SAGE", "MIT"))],
    }
    write_json(EXT / "catalog.json", catalog)
    write_json(EXT / "upstream-lock.json", {"schema_version": SCHEMA, "repository": ECC_REPO,
               "commit": ECC_COMMIT, "license": "MIT with skill-local exceptions; see THIRD_PARTY_NOTICES.md", "files": inventory})
    reports(catalog, inventory, scans)
    web_catalog(catalog)
    print(json.dumps(catalog["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True, help="Local pinned ECC checkout; no network")
    args = parser.parse_args()
    build(args.upstream.resolve())
