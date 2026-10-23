#!/usr/bin/env python3
"""Boundary tests for offline ECC discovery and inert source-packet export."""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch


MODULE = Path(__file__).resolve().parents[1] / "extensions/ecc/sage_ecc.py"
SPEC = importlib.util.spec_from_file_location("sage_ecc", MODULE)
ecc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ecc)


class EccBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "repo"
        self.root.mkdir()
        self.catalog_path = self.root / "extensions/ecc/catalog.json"
        self.catalog_path.parent.mkdir(parents=True)
        self.commits = {"ECC": "a" * 40, "SAGE": "b" * 40}
        self.repos = {"ECC": "example/ecc", "SAGE": "example/sage"}
        self.entries = []
        self.document = {"schema_version": ecc.SCHEMA, "sources": {origin: {"repository": self.repos[origin], "commit": commit} for origin, commit in self.commits.items()}, "entries": self.entries, "summary": {}, "notices": []}
        self.add_notice("sources/upstream/ecc/LICENSE", b"MIT fixture notice; retain attribution.\n", "ECC", "MIT")
        self.add_notice("extensions/ecc/THIRD_PARTY_NOTICES.md", b"# Fixture attribution\nPer-skill license declarations retain precedence.\n", "ALL")
        for name in ecc.CORE_NAMES:
            self.add_entry(name, origin="SAGE", description="Core lifecycle stage", content="# " + name + "\n")
        self.python = self.add_entry("python-security", description="Python security validation", content="---\nname: python-security\nmodel: opus\ntools: Read, Bash\n---\n# Python security\nInspect relevant Python source.\n", domain="python security", rationale_fa="بررسی امنیت پایتون")
        self.add_entry("host-setup", decision="REFERENCE_ONLY", description="Install global hooks", content="# Reference only\n", domain="host")
        self.save()

    def tearDown(self):
        # Packets deliberately contain read-only files; make cleanup portable.
        for path in self.base.rglob("*"):
            if path.is_file() and not path.is_symlink():
                path.chmod(0o600)
        self.temp.cleanup()

    def add_entry(self, name, origin="ECC", kind="skill", decision="ADD", description="Fixture capability", content="# Fixture\n", domain="fixture", rationale_fa=""):
        source_path = ("skills/" + name + "/SKILL.md") if kind == "skill" else "agents/" + name + ".md"
        local_path = ("sources/upstream/ecc/" if origin == "ECC" else "") + source_path
        path = self.root / local_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content.encode("utf-8"))
        entry = {"id": f"{origin.lower()}.{kind}.{name}", "kind": kind, "name": name, "description": description, "origin": origin, "domain": domain, "profile": "engineering", "decision": decision if origin == "ECC" else "KEEP", "sage_targets": ["sage-implement"], "rationale_fa": rationale_fa, "improvement_fa": "", "execution_class": "read_only", "source": {"repository": self.repos[origin], "commit": self.commits[origin], "path": source_path, "url": f"https://github.com/{self.repos[origin]}/blob/{self.commits[origin]}/{source_path}", "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest()}, "local_path": local_path, "review": {"method": "STATIC", "execution_verified": False}, "dependency_flags": []}
        self.entries.append(entry)
        return entry

    def add_resource(self, entry, suffix="scripts/check.py", content=b"# resource\n"):
        parent = str(Path(entry["local_path"]).parent).replace(os.sep, "/")
        local_path = parent + "/" + suffix
        path = self.root / local_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        record = {"local_path": local_path, "source_path": str(Path(entry["source"]["path"]).parent).replace(os.sep, "/") + "/" + suffix, "sha256": hashlib.sha256(content).hexdigest()}
        entry.setdefault("resources", []).append(record)
        return record

    def save(self):
        self.catalog_path.write_text(json.dumps(self.document, ensure_ascii=False), encoding="utf-8")

    def add_notice(self, local_path, content, origin, license=None):
        path = self.root / local_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        self.document["notices"].append({"local_path": local_path, "sha256": hashlib.sha256(content).hexdigest(), "origin": origin, "license": license})

    def catalog(self):
        return ecc.Catalog(self.root)

    def assert_error(self, code, callback):
        with self.assertRaises(ecc.IntegrationError) as caught:
            callback()
        self.assertEqual(caught.exception.code, code)

    def assert_budget_failure(self, catalog, identifiers, byte_limit, expected_reads):
        opened = []
        original_open = Path.open

        def tracked_open(path, *args, **kwargs):
            opened.append(path)
            return original_open(path, *args, **kwargs)

        output = self.base / "packet"
        with patch.object(ecc, "MAX_PACKET_BYTES", byte_limit), patch.object(Path, "open", tracked_open):
            self.assert_error("LIMIT_EXCEEDED", lambda: catalog.bundle(identifiers, output))
        self.assertEqual(opened, [self.root / path for path in expected_reads])
        self.assertFalse(output.exists())

    def test_metadata_discovery_does_not_read_or_execute_sources(self):
        source = self.root / self.python["local_path"]
        source.unlink()
        catalog = self.catalog()
        self.assertTrue(catalog.list_entries(origin="ECC"))
        self.assertEqual(catalog.search("پایتون امنیت")[0]["id"], self.python["id"])
        self.assert_error("SOURCE_UNAVAILABLE", lambda: catalog.show(self.python["id"]))

    def test_persian_typescript_alias_matches_normalized_phrases(self):
        entry = self.add_entry("typescript", description="TypeScript programming", domain="typescript")
        self.save()
        catalog = self.catalog()
        for query in ("typescript", "تایپاسکریپت", "تایپ‌اسکریپت", "تایپ اسکریپت", "تايپ‌اسكريپت"):
            with self.subTest(query=query):
                self.assertEqual(catalog.search(query)[0]["id"], entry["id"])
                self.assertIn("typescript", ecc.tokens(query))
        self.assertNotIn("typescript", ecc.tokens("تایپاسکریپتیک"))

    def test_malformed_catalog_enums_return_json_errors(self):
        cases = [(self.python, field) for field in ("kind", "origin", "decision", "execution_class")]
        cases.append((self.document["notices"][0], "origin"))
        for record, field in cases:
            original = record[field]
            for value in ([], {}, None, 1, True):
                with self.subTest(field=field, value=value, record=record.get("id", "notice")):
                    record[field] = value
                    self.save()
                    stream = io.StringIO()
                    with contextlib.redirect_stdout(stream):
                        code = ecc.main(["--json", "--repo-root", str(self.root), "list"])
                    response = json.loads(stream.getvalue())
                    self.assertEqual(code, 2)
                    self.assertFalse(response["ok"])
                    self.assertEqual(response["error"]["code"], "INVALID_CATALOG")
                    self.assertFalse(response["execution_authorized"])
            record[field] = original
        self.save()

    def test_non_string_ids_are_rejected_before_membership_checks(self):
        catalog = self.catalog()
        output = self.base / "packet"
        self.assert_error("INVALID_INPUT", lambda: catalog.get([]))
        for identifiers in ([[]], [{}], [None], self.python["id"]):
            with self.subTest(identifiers=identifiers):
                self.assert_error("INVALID_INPUT", lambda: catalog.bundle(identifiers, output))
        self.assertFalse(output.exists())

    def test_malformed_sage_targets_return_json_errors(self):
        for targets in ({}, None, "sage-implement", [[]], [""], ["sage-implement", "sage-implement"]):
            with self.subTest(targets=targets):
                self.python["sage_targets"] = targets
                self.save()
                stream = io.StringIO()
                with contextlib.redirect_stdout(stream):
                    code = ecc.main(["--json", "--repo-root", str(self.root), "list"])
                self.assertEqual(code, 2)
                self.assertEqual(json.loads(stream.getvalue())["error"]["code"], "INVALID_CATALOG")

    def test_tampered_source_fails_before_export_writes(self):
        (self.root / self.python["local_path"]).write_text("# altered\n", encoding="utf-8")
        output = self.base / "packet"
        self.assert_error("HASH_MISMATCH", lambda: self.catalog().bundle([self.python["id"]], output))
        self.assertFalse(output.exists())

    def test_commit_mismatch_is_rejected_even_with_matching_file_hash(self):
        self.python["source"]["commit"] = "c" * 40
        self.save()
        self.assert_error("INVALID_PROVENANCE", self.catalog)

    def test_unpinned_or_wrong_case_source_url_is_rejected(self):
        self.python["source"]["url"] = self.python["source"]["url"].replace(self.commits["ECC"], "main")
        self.save()
        self.assert_error("INVALID_PROVENANCE", self.catalog)
        self.python["source"]["url"] = f"https://github.com/{self.repos['ECC']}/blob/{self.commits['ECC']}/skills/python-security/skill.md"
        self.save()
        self.assert_error("INVALID_PROVENANCE", self.catalog)

    def test_unknown_and_reference_only_ids_cannot_export(self):
        catalog = self.catalog()
        for identifier, code in (("ecc.skill.missing", "UNKNOWN_ID"), ("ecc.skill.host-setup", "REFERENCE_ONLY")):
            output = self.base / "packet"
            self.assert_error(code, lambda: catalog.bundle([self.python["id"], identifier], output))
            self.assertFalse(output.exists())
        self.assertEqual(catalog.show("ecc.skill.host-setup")["decision"], "REFERENCE_ONLY")

    def test_export_is_explicit_inert_and_source_preserving(self):
        sentinel = self.base / "source_was_executed"
        executable_text = f"from pathlib import Path\nPath({str(sentinel)!r}).write_text('unsafe')\n".encode()
        self.add_resource(self.python, content=executable_text)
        self.save()
        catalog = self.catalog()
        output = self.base / "packet"
        result = catalog.bundle([self.python["id"]], output, provider="codex", task="Inspect Python", scope="demo.py", risk="R1")
        self.assertFalse(sentinel.exists())
        packet = json.loads((output / "packet.json").read_text(encoding="utf-8"))
        self.assertEqual([e["id"] for e in packet["entries"]], [self.python["id"]])
        selected = packet["entries"][0]
        self.assertEqual((output / selected["packet_path"]).read_bytes(), (self.root / self.python["local_path"]).read_bytes())
        resource = selected["resources"][0]
        copied = output / resource["packet_path"]
        self.assertEqual(copied.read_bytes(), executable_text)
        if os.name != "nt":
            self.assertFalse(copied.stat().st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))
            self.assertFalse(copied.stat().st_mode & stat.S_IWUSR)
        self.assertFalse(result["execution_performed"])
        self.assertFalse(packet["authority_granted"])
        self.assertFalse(packet["native_installation_performed"])
        self.assertEqual(selected["declared_native_assumptions"]["model"], "opus")
        self.assertIn("not Codex bindings", " ".join(packet["adapter_notes"]))
        self.assertFalse((self.root / ".claude").exists())
        self.assertFalse((self.root / ".codex").exists())

    def test_output_path_boundaries(self):
        catalog = self.catalog()
        tests = [(self.root / "packet", "MANAGED_PATH_DENIED"), (MODULE.parents[2] / "ecc-test-must-not-write", "MANAGED_PATH_DENIED"), (self.base, "MANAGED_PATH_DENIED"), (self.base / "x/../packet", "INVALID_PATH"), (Path("packet"), "INVALID_PATH")]
        for output, code in tests:
            self.assert_error(code, lambda: catalog.bundle([self.python["id"]], output))
        existing = self.base / "existing"
        existing.mkdir()
        self.assert_error("OUTPUT_EXISTS", lambda: catalog.bundle([self.python["id"]], existing))
        missing_parent = self.base / "missing/packet"
        self.assert_error("OUTPUT_PARENT_MISSING", lambda: catalog.bundle([self.python["id"]], missing_parent))

    def test_entry_boundaries_survive_show_plan_and_packet_json(self):
        boundaries = ["Inspect only the authorized project scope.", "برای اقدام مخرب، تأیید صریح لازم است."]
        self.python["boundaries"] = boundaries
        self.save()
        catalog = self.catalog()
        self.assertEqual(catalog.show(self.python["id"])["boundaries"], boundaries)

        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            code = ecc.main(["--json", "--repo-root", str(self.root), "plan", "--task", "Python security", "--limit", "1"])
        self.assertEqual(code, 0)
        candidate = json.loads(stream.getvalue())["data"]["candidates"][0]
        self.assertEqual(candidate["id"], self.python["id"])
        self.assertEqual(candidate["boundaries"], boundaries)

        output = self.base / "packet"
        catalog.bundle([self.python["id"]], output)
        selected = json.loads((output / "packet.json").read_text(encoding="utf-8"))["entries"][0]
        self.assertEqual(selected["id"], self.python["id"])
        self.assertEqual(selected["boundaries"], boundaries)

    def test_symlink_sources_and_outputs_are_rejected(self):
        outside = self.base / "outside"
        outside.mkdir()
        link = self.base / "link"
        try:
            link.symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("Symlinks unavailable on this host.")
        self.assert_error("SYMLINK_DENIED", lambda: self.catalog().bundle([self.python["id"]], link / "packet"))
        source = self.root / self.python["local_path"]
        real = outside / "source.md"
        real.write_bytes(source.read_bytes())
        source.unlink()
        source.symlink_to(real)
        self.assert_error("SYMLINK_DENIED", lambda: self.catalog().show(self.python["id"]))

    def test_source_and_resource_traversal_are_rejected(self):
        self.python["local_path"] = "../outside.md"
        self.save()
        self.assert_error("INVALID_PATH", self.catalog)
        self.python["local_path"] = "sources/upstream/ecc/skills/python-security/SKILL.md"
        resource = self.add_resource(self.python)
        resource["source_path"] = "skills/other/scripts/check.py"
        self.save()
        self.assert_error("INVALID_PATH", self.catalog)

    def test_tampered_resource_prevents_partial_packet(self):
        resource = self.add_resource(self.python)
        self.save()
        (self.root / resource["local_path"]).write_bytes(b"changed")
        output = self.base / "packet"
        self.assert_error("HASH_MISMATCH", lambda: self.catalog().bundle([self.python["id"]], output))
        self.assertFalse(output.exists())

    def test_packet_budget_rejects_entrypoints_before_opening(self):
        second = self.add_entry("second", content="# Second source\n")
        self.save()
        catalog = self.catalog()
        first_size = (self.root / self.python["local_path"]).stat().st_size
        second_size = (self.root / second["local_path"]).stat().st_size
        for limit, expected in ((first_size - 1, []), (first_size, [self.python["local_path"]]), (first_size + second_size - 1, [self.python["local_path"]])):
            with self.subTest(limit=limit):
                self.assert_budget_failure(catalog, [self.python["id"], second["id"]], limit, expected)

    def test_packet_budget_stops_before_over_budget_and_later_resources(self):
        resources = [self.add_resource(self.python, f"data/resource-{i}.bin", b"x" * 64) for i in range(3)]
        self.save()
        catalog = self.catalog()
        source_size = (self.root / self.python["local_path"]).stat().st_size
        for extra, expected_resources in ((63, []), (64, resources[:1]), (96, resources[:1])):
            with self.subTest(extra_bytes=extra):
                expected = [self.python["local_path"]] + [resource["local_path"] for resource in expected_resources]
                self.assert_budget_failure(catalog, [self.python["id"]], source_size + extra, expected)

    def test_packet_budget_stops_before_over_budget_and_later_notices(self):
        self.add_notice("extensions/ecc/later-notice.md", b"Later notice\n", "ALL")
        self.save()
        catalog = self.catalog()
        first_notice = self.document["notices"][0]["local_path"]
        expected = [self.python["local_path"], first_notice]
        limit = sum((self.root / path).stat().st_size for path in expected)
        self.assert_budget_failure(catalog, [self.python["id"]], limit, expected)

    def test_packet_budget_accepts_exact_capacity_and_empty_files(self):
        resource = self.add_resource(self.python, content=b"x" * 64)
        empty = self.add_resource(self.python, "data/empty.bin", b"")
        self.save()
        catalog = self.catalog()
        paths = [self.python["local_path"], resource["local_path"], empty["local_path"]] + [notice["local_path"] for notice in self.document["notices"]]
        limit = sum((self.root / path).stat().st_size for path in paths)
        output = self.base / "packet"
        with patch.object(ecc, "MAX_PACKET_BYTES", limit):
            result = catalog.bundle([self.python["id"]], output)
        self.assertEqual(result["source_bytes"], limit)
        self.assertTrue((output / "packet.json").is_file())
        self.assertEqual(ecc.read_bounded(self.root / empty["local_path"], remaining_bytes=0), b"")

    def test_read_budget_is_rechecked_when_source_grows_after_stat(self):
        path = self.root / "growing.bin"
        path.write_bytes(b"x")
        original_open = Path.open

        def grow_before_open(open_path, *args, **kwargs):
            if open_path == path:
                with original_open(path, "wb") as handle:
                    handle.write(b"xxxx")
            return original_open(open_path, *args, **kwargs)

        with patch.object(Path, "open", grow_before_open):
            self.assert_error("LIMIT_EXCEEDED", lambda: ecc.read_bounded(path, remaining_bytes=3))

    def test_specific_license_and_attribution_bytes_are_preserved(self):
        self.python["license"] = "CC-BY-SA-4.0"
        self.python["license_scope"] = "skill_directory"
        self.python["source"]["license"] = "CC-BY-SA-4.0"
        resource = self.add_resource(self.python, "LICENSE.txt", b"CC-BY-SA fixture; original author attribution.\n")
        self.save()
        output = self.base / "packet"
        self.catalog().bundle([self.python["id"]], output)
        packet = json.loads((output / "packet.json").read_text(encoding="utf-8"))
        entry = packet["entries"][0]
        self.assertEqual(entry["license"], "CC-BY-SA-4.0")
        self.assertEqual(entry["source"]["license"], "CC-BY-SA-4.0")
        self.assertEqual((output / entry["resources"][0]["packet_path"]).read_bytes(), (self.root / resource["local_path"]).read_bytes())
        for notice in packet["notices"]:
            self.assertEqual((output / notice["packet_path"]).read_bytes(), (self.root / notice["local_path"]).read_bytes())

    def test_missing_or_tampered_notices_fail_before_export(self):
        self.document["notices"] = []
        self.save()
        output = self.base / "packet"
        self.assert_error("LICENSE_NOTICES_MISSING", lambda: self.catalog().bundle([self.python["id"]], output))
        self.assertFalse(output.exists())
        self.add_notice("sources/upstream/ecc/LICENSE", b"Original license", "ECC", "MIT")
        self.add_notice("extensions/ecc/THIRD_PARTY_NOTICES.md", b"Original attribution", "ALL")
        self.save()
        (self.root / "sources/upstream/ecc/LICENSE").write_text("tampered", encoding="utf-8")
        self.assert_error("HASH_MISMATCH", lambda: self.catalog().bundle([self.python["id"]], output))
        self.assertFalse(output.exists())

    def test_apache_notice_is_scoped_and_mit_ancestor_notice_retained(self):
        self.add_notice("extensions/ecc/licenses/Apache-2.0.txt", b"Apache fixture license", "ECC", "Apache-2.0")
        self.save()
        first = self.base / "mit-packet"
        self.catalog().bundle([self.python["id"]], first)
        mit_packet = json.loads((first / "packet.json").read_text(encoding="utf-8"))
        self.assertNotIn("Apache-2.0", [n.get("license") for n in mit_packet["notices"]])
        self.python["license"] = "Apache-2.0"
        self.save()
        second = self.base / "apache-packet"
        self.catalog().bundle([self.python["id"]], second)
        apache_packet = json.loads((second / "packet.json").read_text(encoding="utf-8"))
        self.assertIn("Apache-2.0", [n.get("license") for n in apache_packet["notices"]])
        self.assertIn("MIT", [n.get("license") for n in apache_packet["notices"]])

    def test_plan_is_bounded_repeatable_and_keeps_governance(self):
        target = self.add_entry("native-target", origin="SAGE")
        self.python["sage_targets"] = ["sage-implement", target["name"]]
        for i in range(8):
            self.add_entry(f"python-{i}", description="Python programming", domain="python")
        self.save()
        catalog = self.catalog()
        first = catalog.plan("Python security", scope="src/", risk="R3", limit=3)
        self.assertEqual(first, catalog.plan("Python security", scope="src/", risk="R3", limit=3))
        self.assertEqual(first["status"], "ADVISORY_PLAN")
        self.assertEqual(len(first["candidates"]), 3)
        self.assertEqual([x["role"] for x in first["lifecycle"]], ["intake", "discover", "plan", "implement", "verify"])
        self.assertTrue(first["independent_review_required"])
        self.assertFalse(first["execution_authorized"])
        self.assertEqual(first["risk_basis"], "caller_supplied_unverified")
        self.assertTrue(all(c["decision"] != "REFERENCE_ONLY" for c in first["candidates"]))
        candidate_ids = [candidate["id"] for candidate in first["candidates"]]
        self.assertNotIn(target["id"], candidate_ids)
        enhancements = {enhancement["sage_skill_id"]: enhancement for enhancement in first["enhancements"]}
        self.assertEqual(enhancements["sage.skill.sage-implement"]["ecc_candidate_ids"], candidate_ids)
        self.assertEqual(enhancements[target["id"]]["ecc_candidate_ids"], [self.python["id"]])
        self.assertEqual(enhancements[target["id"]]["source"], target["source"])
        self.assertTrue(all(enhancement["source_integrity_verified"] for enhancement in first["enhancements"]))

    def test_plan_verifies_enhancement_targets_outside_candidate_limit(self):
        target = self.add_entry("native-target", origin="SAGE")
        self.python["sage_targets"] = [target["name"]]
        self.save()
        (self.root / target["local_path"]).write_text("# Tampered target\n", encoding="utf-8")
        self.assert_error("HASH_MISMATCH", lambda: self.catalog().plan("Python security", limit=1))

    def test_unknown_task_has_no_random_fallback_candidates(self):
        plan = self.catalog().plan("flibbertigibbetxyz")
        self.assertEqual(plan["status"], "NEEDS_CLARIFICATION")
        self.assertEqual(plan["candidates"], [])
        self.assertEqual(plan["enhancements"], [])
        self.assertTrue(plan["clarification"])

    def test_missing_governance_blocks_an_otherwise_matching_plan(self):
        for name in ("sage-verify", "sage-implement"):
            with self.subTest(missing=name):
                self.entries[:] = [e for e in self.entries if e["name"] != name]
                self.save()
                plan = self.catalog().plan("Python security")
                self.assertEqual(plan["status"], "BLOCKED")
                self.assertIn("sage.skill." + name, plan["missing_governance"])

    def test_native_specialist_only_emits_selected_projection(self):
        native = self.add_entry("rust-engineer", origin="SAGE", kind="agent", domain="rust")
        body = json.dumps({"profiles": [{"profile_id": "rust-engineer", "capabilities": ["rust"]}, {"profile_id": "unrelated-engineer", "private_fixture": "do-not-export" * 50}]})
        native["source"]["path"] = "extensions/technology-engineering/specialists.json"
        native["source"]["url"] = f"https://github.com/{self.repos['SAGE']}/blob/{self.commits['SAGE']}/{native['source']['path']}"
        native["local_path"] = native["source"]["path"]
        native["source"]["sha256"] = hashlib.sha256(body.encode()).hexdigest()
        path = self.root / native["local_path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        self.save()
        result = self.catalog().show(native["id"])
        self.assertEqual(result["representation"], "selected_profile_projection")
        self.assertNotIn("do-not-export", result["source_content"])
        self.assertEqual(json.loads(result["source_content"])["profile_id"], "rust-engineer")
        projection = result["source_content"].encode("utf-8")
        limit = len(projection) + sum((self.root / notice["local_path"]).stat().st_size for notice in self.document["notices"] if notice["origin"] in ("SAGE", "ALL"))
        self.assertGreater(len(body.encode("utf-8")), limit)
        output = self.base / "packet"
        with patch.object(ecc, "MAX_PACKET_BYTES", limit):
            exported = self.catalog().bundle([native["id"]], output)
        selected = json.loads((output / "packet.json").read_text(encoding="utf-8"))["entries"][0]
        self.assertEqual(exported["source_bytes"], limit)
        self.assertEqual((output / selected["packet_path"]).read_bytes(), projection)
        self.assertEqual(selected["source"]["sha256"], hashlib.sha256(body.encode("utf-8")).hexdigest())
        self.assertEqual(selected["packet_sha256"], hashlib.sha256(projection).hexdigest())

    def test_expanded_native_projection_is_checked_before_retention(self):
        native = self.add_entry("compact-engineer", origin="SAGE", kind="agent")
        body = json.dumps({"profiles": [{"profile_id": "compact-engineer", "steps": ["step"] * 32}]}, separators=(",", ":"))
        native["source"]["path"] = "extensions/technology-engineering/specialists.json"
        native["source"]["url"] = f"https://github.com/{self.repos['SAGE']}/blob/{self.commits['SAGE']}/{native['source']['path']}"
        native["local_path"] = native["source"]["path"]
        native["source"]["sha256"] = hashlib.sha256(body.encode("utf-8")).hexdigest()
        path = self.root / native["local_path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        self.save()
        catalog = self.catalog()
        source_size = len(body.encode("utf-8"))
        self.assertGreater(len(catalog.show(native["id"])["source_content"].encode("utf-8")), source_size)
        self.assert_budget_failure(catalog, [native["id"]], source_size, [native["local_path"]])

    def test_json_cli_is_uniform_before_and_after_subcommands(self):
        for args in (["--json", "--repo-root", str(self.root), "show", self.python["id"]], ["show", self.python["id"], "--repo-root", str(self.root), "--json"]):
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                code = ecc.main(args)
            value = json.loads(stream.getvalue())
            self.assertEqual(code, 0)
            self.assertTrue(value["ok"])
            self.assertFalse(value["execution_authorized"])
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            code = ecc.main(["--json", "unknown-command"])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(stream.getvalue())["error"]["code"], "INVALID_ARGUMENTS")

    def test_json_cli_preserves_unicode_on_non_utf8_stdout(self):
        unknown_id = "ناموجود"
        for encoding in ("ascii", "cp1252"):
            for identifier, expected_code in ((self.python["id"], 0), (unknown_id, 2)):
                with self.subTest(encoding=encoding, identifier=identifier):
                    raw = io.BytesIO()
                    with io.TextIOWrapper(raw, encoding=encoding, errors="strict") as stream:
                        with contextlib.redirect_stdout(stream):
                            code = ecc.main(["--json", "--repo-root", str(self.root), "show", identifier])
                        stream.flush()
                        output = raw.getvalue()
                    response = json.loads(output.decode("ascii"))
                    self.assertEqual(code, expected_code)
                    self.assertFalse(response["execution_authorized"])
                    if expected_code == 0:
                        self.assertTrue(response["ok"])
                        self.assertEqual(response["data"]["rationale_fa"], self.python["rationale_fa"])
                    else:
                        self.assertFalse(response["ok"])
                        self.assertEqual(response["error"]["code"], "UNKNOWN_ID")
                        self.assertIn(unknown_id, response["error"]["message"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
