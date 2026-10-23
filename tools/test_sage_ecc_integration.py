#!/usr/bin/env python3
"""Exercise real catalog records without running their scripts or providers."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("sage_ecc_integration", ROOT / "extensions/ecc/sage_ecc.py")
ecc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ecc)


class RealCatalogIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = ecc.Catalog(ROOT)

    def test_all_425_definitions_can_load_with_verified_source(self):
        self.assertEqual(len(self.catalog.entries), 425)
        for entry in self.catalog.entries.values():
            content, _ = self.catalog.verified_source(entry)
            self.assertTrue(content)

    def test_real_rust_plan_keeps_lifecycle_and_bounded_candidates(self):
        result = self.catalog.plan("Review Rust ownership lifetime unsafe and Cargo tests", scope="src/lib.rs", risk="R1", limit=6)
        self.assertFalse(result["execution_authorized"])
        self.assertFalse(result["execution_performed"])
        candidates = json.dumps(result)
        self.assertIn("rust", candidates.lower())
        self.assertIn("sage-intake", candidates)
        self.assertIn("sage-verify", candidates)

    def test_three_complementary_workflows_export_with_attribution(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary).resolve() / "packet"
            ids = ["ecc.agent.code-reviewer", "ecc.skill.security-review", "ecc.skill.verification-loop"]
            self.catalog.bundle(ids, target, provider="codex", task="Review the scoped change", scope="selected diff", risk="R1")
            packet = json.loads((target / "packet.json").read_text(encoding="utf-8"))
            self.assertEqual({e["id"] for e in packet["entries"]}, set(ids))
            self.assertFalse(packet["authority_granted"])
            self.assertFalse(packet["native_installation_performed"])
            text = json.dumps(packet)
            self.assertIn("THIRD_PARTY_NOTICES", text)
            self._writable(target)

    def test_large_skill_resource_closure_and_local_license(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary).resolve() / "creative"
            self.catalog.bundle(["ecc.skill.taste-application", "ecc.skill.osint-investigation"], target)
            packet = json.loads((target / "packet.json").read_text(encoding="utf-8"))
            entries = {e["id"]: e for e in packet["entries"]}
            taste = entries["ecc.skill.taste-application"]
            self.assertGreater(len(taste["resources"]), 50)
            osint = entries["ecc.skill.osint-investigation"]
            self.assertEqual(osint["license"], "CC-BY-SA-4.0")
            self.assertTrue(any(r["source_path"].endswith("LICENSE.txt") for r in osint["resources"]))
            self._writable(target)

    def test_reference_control_plane_cannot_activate(self):
        self.assertEqual(self.catalog.get("ecc.agent.loop-operator")["decision"], "REFERENCE_ONLY")
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary).resolve() / "ref"
            with self.assertRaises(ecc.IntegrationError):
                self.catalog.bundle(["ecc.agent.loop-operator"], target)
            self.assertFalse(target.exists())

    def test_unmatched_task_does_not_choose_random_tools(self):
        result = self.catalog.plan("zzzzzzzznonexistentcapability", limit=6)
        self.assertEqual(result["status"], "NEEDS_CLARIFICATION")

    @staticmethod
    def _writable(path):
        for item in path.rglob("*"):
            if item.is_file():
                item.chmod(0o600)


if __name__ == "__main__":
    unittest.main(verbosity=2)
