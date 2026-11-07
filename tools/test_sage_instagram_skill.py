"""Offline SAGE Instagram specialist checks; no Instagram or network access."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

MODULE = Path(__file__).resolve().parents[1] / "extensions" / "internet-eyes" / "instagram-specialist" / "router.py"
MANIFEST = MODULE.parent / "manifest.json"
POLICY = MODULE.parent / "policy.json"
spec = importlib.util.spec_from_file_location("ig_sage_router", MODULE)
router = importlib.util.module_from_spec(spec)
spec.loader.exec_module(router)

class InstagramRouterContractTests(unittest.TestCase):
    def test_has_exact_13_skills(self):
        self.assertEqual(len(router.SKILL_NAMES), 13)
        self.assertEqual(len(set(router.SKILL_NAMES)), 13)
        self.assertEqual({v[0] for v in router.ROUTES.values()}, set(router.SKILL_NAMES))

    def test_pinned_commit_and_read_only_channel(self):
        m = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(m["upstream"]["pinned_commit"], "d03c56bb598be770c60b201f94237e5d1a4268a6")
        self.assertFalse(m["integration"]["auto_post"])
        self.assertEqual(m["existing_agent_reach"]["actions"], ["search", "profile", "posts"])

    def test_side_effects_are_not_authorized(self):
        p = json.loads(POLICY.read_text(encoding="utf-8"))
        self.assertFalse(any(p["side_effects"].values()))
        self.assertFalse(p["per_language"]["fa"]["automatic_humanize"])

    def test_all_routes_are_discovery_only(self):
        for intent in router.ROUTES:
            with self.subTest(intent=intent):
                result = router.route(intent, "en")
                self.assertFalse(result["authority_granted"])
                self.assertFalse(result["external_execution"])
                self.assertFalse(result["instagram_mutation_allowed"])

    def test_persian_halfspace_warning(self):
        for intent in ("humanize", "caption", "reel"):
            self.assertIn("U+200C", " ".join(router.route(intent, "fa")["warnings"]))

    def test_no_fabricated_insights(self):
        self.assertIn("views", " ".join(router.route("viral-research", "fa")["warnings"]))

    def test_missing_install_not_claimed(self):
        with tempfile.TemporaryDirectory() as d:
            with patch.object(Path, "home", return_value=Path(d)):
                self.assertEqual(router.route("reel", "fa")["status"], "NOT_INSTALLED_ON_THIS_HOST")

    def test_existing_skill_is_discovered(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / ".agents" / "skills" / "ig-reel"
            f.mkdir(parents=True)
            (f / "SKILL.md").write_text("---\nname: ig-reel\n---\n", encoding="utf-8")
            with patch.object(Path, "home", return_value=Path(d)):
                self.assertEqual(router.route("reel", "en")["status"], "DISCOVERED")

    def test_cli_output_is_json(self):
        for args in (["status"], ["list"], ["route", "--intent", "reel", "--language", "fa"]):
            cp = subprocess.run([sys.executable, str(MODULE), *args], text=True, capture_output=True, timeout=8)
            self.assertEqual(cp.returncode, 0, cp.stderr)
            self.assertEqual(json.loads(cp.stdout)["schema_version"], router.SCHEMA)

if __name__ == "__main__":
    unittest.main()
