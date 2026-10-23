from __future__ import annotations

from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import MagicMock, patch

from sage_runtime import cli


class CliTests(unittest.TestCase):
    def setUp(self):
        self.engine = MagicMock()
        self.engine.create.return_value = {"run_id": "run-test", "status": "CREATED"}
        self.engine.run.return_value = {"run_id": "run-test", "status": "DONE"}
        self.engine.status.return_value = {"run_id": "run-test", "status": "WAITING_APPROVAL"}
        self.factory = MagicMock(return_value=self.engine)
        self.module_patch = patch.dict(sys.modules, {"sage_runtime.engine": types.SimpleNamespace(Engine=self.factory)})
        self.module_patch.start()
        self.addCleanup(self.module_patch.stop)

    def invoke(self, *arguments):
        out = io.StringIO()
        with redirect_stdout(out):
            code = cli.main(list(arguments))
        return code, json.loads(out.getvalue())

    def test_nonlive_default_only_creates_checkpoint(self):
        code, result = self.invoke("build", "Small stdlib app", "--output", str(Path.cwd() / "new-app"))
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "CREATED")
        self.engine.run.assert_not_called()
        self.assertFalse(self.engine.create.call_args.kwargs["live"])
        self.assertNotIn("source", self.engine.create.call_args.kwargs)

    def test_explicit_source_forwards_readonly_seed_and_separate_output(self):
        source, output = Path.cwd() / "existing-source", Path.cwd() / "new-fixed-copy"
        code, result = self.invoke("build", "Fix calculator subtraction while preserving its API", "--source", str(source),
                                   "--output", str(output), "--approval-id", "approved-local")
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "CREATED")
        self.assertEqual(self.engine.create.call_args.kwargs["source"], source)
        self.assertEqual(self.engine.create.call_args.args[1], output)
        self.engine.run.assert_not_called()

    def test_live_requires_approval_before_engine_construction(self):
        code, result = self.invoke("build", "Small app", "--output", str(Path.cwd() / "new-app"), "--live")
        self.assertEqual(code, 1)
        self.assertEqual(result["error"]["code"], "APPROVAL_REQUIRED")
        self.factory.assert_not_called()

    def test_live_runs_same_created_run_and_forwards_budget(self):
        code, result = self.invoke("build", "Small app", "--output", str(Path.cwd() / "new-app"),
                                   "--live", "--approval-id", "approved-local", "--auto-approve-plan",
                                   "--max-model-calls", "5", "--max-repairs", "1", "--max-seconds", "300",
                                   "--profile", "python-stdlib", "--pause-after", "plan")
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "DONE")
        self.engine.run.assert_called_once_with("run-test", live=True, pause_after="PLAN")
        kwargs = self.engine.create.call_args.kwargs
        self.assertEqual((kwargs["max_model_calls"], kwargs["max_repairs"], kwargs["max_seconds"]), (5, 1, 300))
        self.assertTrue(kwargs["auto_approve_plan"])

    def test_auto_approval_without_live_is_rejected(self):
        code, result = self.invoke("build", "Small app", "--output", "new-app", "--auto-approve-plan")
        self.assertEqual(code, 1)
        self.assertEqual(result["error"]["code"], "LIVE_REQUIRED")

    def test_resume_is_nonlive_by_default(self):
        self.invoke("resume", "run-test")
        self.engine.run.assert_called_once_with("run-test", live=False, pause_after=None)
        self.engine.create.assert_not_called()

    def test_locations_before_and_after_command(self):
        kit, state = Path.cwd(), Path.cwd() / "evidence"
        self.invoke("--kit-root", str(kit), "--state-root", str(state), "status", "run-test")
        self.factory.assert_called_with(kit, state)
        self.invoke("status", "run-test", "--kit-root", str(kit), "--state-root", str(state), "--json")
        self.factory.assert_called_with(kit, state)

    def test_approve_passes_exact_plan_hash(self):
        self.engine.approve.return_value = {"status": "PLAN_APPROVED"}
        self.invoke("approve", "run-test", "--plan-hash", "b" * 64)
        self.engine.approve.assert_called_once_with("run-test", "b" * 64)
        self.engine.run.assert_not_called()

    def test_clarify_and_cancel_only_dispatch_requested_action(self):
        self.engine.clarify.return_value = {"status": "CREATED"}
        self.invoke("clarify", "run-test", "--answer", "فقط محلی")
        self.engine.clarify.assert_called_once_with("run-test", "فقط محلی")
        self.engine.cancel.return_value = {"status": "CANCELLED"}
        code, result = self.invoke("cancel", "run-test")
        self.assertEqual(code, 2)
        self.assertEqual(result["status"], "CANCELLED")
        self.engine.run.assert_not_called()

    def test_bad_arguments_are_structured_json(self):
        code, result = self.invoke("approve", "run-test")
        self.assertEqual(code, 1)
        self.assertEqual(result["error"]["code"], "INVALID_ARGUMENT")
        self.factory.assert_not_called()

    def test_bad_profile_never_calls_engine(self):
        code, result = self.invoke("build", "App", "--output", "new-app", "--profile", "arbitrary-command")
        self.assertEqual(code, 1)
        self.assertEqual(result["error"]["code"], "INVALID_ARGUMENT")
        self.factory.assert_not_called()

    def test_safe_error_passes_code_not_traceback(self):
        from sage_runtime.safety import SageError
        self.engine.status.side_effect = SageError("EVIDENCE_TAMPERED", "Evidence verification failed.")
        code, result = self.invoke("status", "run-test")
        self.assertEqual(code, 1)
        self.assertEqual(result["error"], {"code": "EVIDENCE_TAMPERED", "message": "Evidence verification failed."})

    def test_unexpected_error_does_not_disclose_sensitive_exception(self):
        self.engine.status.side_effect = RuntimeError("private-token-must-not-appear")
        code, result = self.invoke("status", "run-test")
        self.assertEqual(code, 1)
        self.assertEqual(result["error"]["code"], "INTERNAL_ERROR")
        self.assertNotIn("private-token", json.dumps(result))

    def test_status_reports_action_needed_exit(self):
        code, result = self.invoke("status", "run-test")
        self.assertEqual(code, 2)
        self.assertEqual(result["status"], "WAITING_APPROVAL")

    def test_doctor_uses_no_engine_or_model(self):
        provider = MagicMock()
        provider.doctor.return_value = {"ready": True, "authenticated": True}
        module = types.SimpleNamespace(CodexProvider=MagicMock(return_value=provider))
        with patch.dict(sys.modules, {"sage_runtime.providers": module}):
            code, result = self.invoke("doctor")
        self.assertEqual(code, 0)
        self.assertTrue(result["kit_available"])
        self.assertEqual(result["model_invocations"], 0)
        self.assertEqual(result["sandbox_readiness"], "NOT_PROBED")
        self.assertEqual(result["live_acceptance"], "NOT_RUN")
        self.factory.assert_not_called()
        provider.generate.assert_not_called()

    def test_doctor_missing_provider_readiness_is_blocked(self):
        module = types.SimpleNamespace(CodexProvider=lambda: types.SimpleNamespace(doctor=lambda: {"ready": False}))
        with patch.dict(sys.modules, {"sage_runtime.providers": module}):
            code, result = self.invoke("doctor")
        self.assertEqual(code, 2)
        self.assertEqual(result["status"], "BLOCKED")

    def test_version_matches_additive_package_not_sdk(self):
        out = io.StringIO()
        with redirect_stdout(out), self.assertRaises(SystemExit) as stopped:
            cli.main(["--version"])
        self.assertEqual(stopped.exception.code, 0)
        self.assertEqual(out.getvalue().strip(), "sage-runtime 0.1.0")


@unittest.skipUnless(importlib.util.find_spec("setuptools"), "Packaging backend is optional for direct source execution.")
class PackagingClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        setup_file = Path(__file__).resolve().parents[1] / "setup.py"
        spec = importlib.util.spec_from_file_location("sage_runtime_packaging", setup_file)
        cls.packaging = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.packaging)

    def test_offline_closure_preserves_all_declared_source_and_notice_hashes(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "_kit"
            inventory = self.packaging.stage_resources(target)
            rows = inventory["files"]
            self.assertGreater(len(rows), 400)
            self.assertEqual(inventory["treatment"], "attributed_source_data_not_executed")
            paths = {row["path"] for row in rows}
            self.assertIn("sources/upstream/ecc/LICENSE", paths)
            self.assertIn("extensions/ecc/THIRD_PARTY_NOTICES.md", paths)
            self.assertIn("extensions/ecc/licenses/Apache-2.0.txt", paths)
            registry = json.loads((target / "skills/registry.json").read_text(encoding="utf-8"))
            for relative in registry["optional_extensions"]:
                manifest_path = target / relative
                self.assertTrue(manifest_path.is_file(), relative)
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                for key in ("catalog", "policy", "schema", "lockfile", "review_matrix", "enhancements", "cli", "web_catalog"):
                    if key in manifest:
                        resource = (manifest_path.parent / manifest[key]).resolve()
                        self.assertTrue(resource.is_relative_to(target.resolve()))
                        self.assertTrue(resource.is_file(), relative + ":" + key)
                for key in ("architecture_delta", "guide", "acceptance_ref"):
                    if key in manifest:
                        self.assertTrue((target / manifest[key]).is_file(), relative + ":" + key)
            for row in rows:
                payload = (target / row["path"]).read_bytes()
                self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
                self.assertNotIn(".env", Path(row["path"]).parts)
                self.assertNotIn(".git", Path(row["path"]).parts)

    def test_source_paths_cannot_escape_closure(self):
        with tempfile.TemporaryDirectory() as temp:
            for value in ("../secrets", "/outside", "C:/outside", "one\\two", "a/./b", "a//b"):
                with self.subTest(value=value), self.assertRaises(RuntimeError):
                    self.packaging.safe_source(Path(temp), value)

    def test_closure_rejects_tampered_source_before_copy(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "entry.md").write_text("not the pinned content", encoding="utf-8")
            destination = root / "output"
            with patch.object(self.packaging, "resource_root", return_value=root), \
                    patch.object(self.packaging, "source_closure", return_value={"entry.md": "a" * 64}):
                with self.assertRaisesRegex(RuntimeError, "SHA256 mismatch"):
                    self.packaging.stage_resources(destination)
            self.assertFalse(destination.exists())

    def test_closure_cannot_include_unrelated_private_repository_data(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            catalog = root / self.packaging.CATALOG
            catalog.parent.mkdir(parents=True)
            catalog.write_text(json.dumps({
                "schema_version": "sage-ecc/0.1",
                "entries": [{"local_path": "sources/supplied-originals/private.txt",
                             "source": {"sha256": "a" * 64}}],
            }), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "outside the public capability"):
                self.packaging.source_closure(root)

    def test_closure_rejects_stale_private_output_instead_of_packaging_it(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "entry.md").write_text("pinned reference", encoding="utf-8")
            destination = root / "output"
            destination.mkdir()
            private = destination / "unrelated-secret.env"
            private.write_text("do not package this", encoding="utf-8")
            expected = hashlib.sha256((root / "entry.md").read_bytes()).hexdigest()
            with patch.object(self.packaging, "resource_root", return_value=root), \
                    patch.object(self.packaging, "source_closure", return_value={"entry.md": expected}):
                with self.assertRaisesRegex(RuntimeError, "Unexpected stale resource"):
                    self.packaging.stage_resources(destination)
            self.assertTrue(private.is_file())
            self.assertFalse((destination / "entry.md").exists())


if __name__ == "__main__":
    unittest.main()
