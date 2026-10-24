"""Offline experiment boundaries; no SDK, model or Docker is started here."""
import base64
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from sage_runtime.safety import SageError

ROOT = Path(__file__).resolve().parents[3]


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / file)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


class EvaluationBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bench = module("sage_evaluation_offline", "Evaluate-SageCodingEngines.py")
        cls.sdk = module("sage_sdk_evaluation_offline", "sage_openhands_evaluation_worker.py")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.folder, self.budget = self.bench.setup(self.base / "evidence")

    def provider(self):
        return self.sdk.EvaluationProvider(self.budget, self.base / "sdk-python.exe",
                                           self.base / "private", self.folder, set())

    def test_scenarios_are_closed_and_oracle_is_controller_owned(self):
        for scenario in ("slug", "divide", "gate"):
            idea, oracle, _, _ = self.bench.case(scenario)
            self.assertTrue(idea)
            compile(oracle, "oracle", "exec")
        with self.assertRaises(SageError):
            self.bench.case("../../private")

    def test_missing_live_flag_cannot_create_state_or_launch_provider(self):
        from contextlib import redirect_stderr
        target = self.base / "not-created"
        with patch.object(sys, "argv", ["evaluation", "--root", str(target), "--route", "direct", "--scenario", "slug"]), \
                redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            self.bench.main()
        self.assertFalse(target.exists())

    def test_existing_evaluation_authority_cannot_silently_change(self):
        authority = self.folder / "evaluation-authority.json"
        changed = json.loads(authority.read_text()); changed["paid_api_access"] = True
        authority.write_text(json.dumps(changed))
        with self.assertRaises(SageError):
            self.bench.setup(self.folder)

    def test_missing_budget_with_only_direct_results_cannot_reset(self):
        self.budget.path.unlink()
        with self.assertRaises(SageError):
            self.bench.setup(self.folder)
        self.assertFalse(self.budget.path.exists())

    def test_sdk_private_state_cannot_use_home_or_source_as_persistence(self):
        for root in (Path.home(), ROOT, self.folder):
            with self.subTest(root=str(root)), self.assertRaises(SageError):
                self.sdk.EvaluationProvider(self.budget, self.base / "python.exe", root, self.folder, set())

    def test_cancel_before_bootstrap_never_reads_auth_or_reserves_a_job(self):
        worker = self.provider(); worker.cancel_check = lambda: True
        with patch.object(self.sdk, "subscription_grant", side_effect=AssertionError("must not read")), self.assertRaises(SageError) as caught:
            worker.generate("implementer", "offline", {}, self.base, 10)
        self.assertEqual(caught.exception.code, "CANCELLED")
        self.assertEqual(json.loads(self.budget.path.read_text())["reserved_calls"], 0)

    def test_failed_sdk_is_charged_and_never_routed_to_codex(self):
        token = self.base / "fake-auth.json"; token.write_text("offline-only")
        process = {"timed_out": True, "cancelled": False, "exit_code": 0, "output_truncated": False,
                   "stdout": "", "duration_seconds": .1}
        self.budget.provider = object()
        with patch.object(self.sdk, "subscription_grant", return_value=(token, hashlib.sha256(token.read_bytes()).hexdigest(), {})), \
                patch.object(self.sdk, "run_bounded", return_value=process), self.assertRaises(SageError) as caught:
            self.provider().generate("implementer", "offline", {}, self.base, 10)
        self.assertEqual(caught.exception.code, "PROVIDER_FAILED")
        self.assertEqual(json.loads(self.budget.path.read_text())["reserved_calls"], 1)

    def test_fabricated_sdk_success_receipt_is_not_execution_evidence(self):
        token = self.base / "fake-auth.json"; token.write_text("offline-only")
        fake = {"status": "COMPLETED", "sdk_model_jobs": 1, "conversation_status": "finished",
                "payload": {}, "synthetic": True}
        process = {"timed_out": False, "cancelled": False, "exit_code": 0, "output_truncated": False,
                   "stdout": self.sdk.SENTINEL + json.dumps(fake), "duration_seconds": .1}
        with patch.object(self.sdk, "subscription_grant", return_value=(token, hashlib.sha256(token.read_bytes()).hexdigest(), {})), \
                patch.object(self.sdk, "run_bounded", return_value=process), self.assertRaises(SageError) as caught:
            self.provider().generate("implementer", "offline", {}, self.base, 10)
        self.assertEqual(caught.exception.code, "SDK_EVIDENCE")

    def test_expired_or_api_authentication_cannot_become_a_subscription_grant(self):
        cache = self.base / "fake-native-auth"; cache.mkdir()
        payload = base64.urlsafe_b64encode(json.dumps({"exp": int(time.time())+20}).encode()).decode().rstrip("=")
        for mode in ("chatgpt", "apikey"):
            (cache / "auth.json").write_text(json.dumps({"auth_mode": mode, "tokens": {"access_token": "offline."+payload+".offline"}}))
            with patch.dict(os.environ, {"CODEX_HOME": str(cache)}), self.assertRaises(SageError):
                self.sdk.subscription_grant()

    def test_invalid_worker_grant_is_rejected_before_optional_sdk_import(self):
        packet = {"approval": "not-approved", "model": self.sdk.MODEL, "stage": "implementer"}
        result = subprocess.run([sys.executable, "-B", str(ROOT / "tools/sage_openhands_evaluation_worker.py"), "--sdk-worker"],
                                input=json.dumps(packet), capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 1)
        reply = json.loads(result.stdout.split(self.sdk.SENTINEL)[-1])
        self.assertEqual(reply["phase"], "input")
        self.assertEqual(reply["error_type"], "RuntimeError")


if __name__ == "__main__":
    unittest.main()
