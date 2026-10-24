"""Harmless local subprocess fixtures; no generated project code or model call."""

import json
import os
import sys
import tempfile
import time
import unittest

from sage_runtime.process import minimal_environment, run_bounded


class ProcessTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="sage-process-unit-")
        self.addCleanup(self.directory.cleanup)

    def run_code(self, code, **options):
        return run_bounded([sys.executable, "-I", "-S", "-c", code],
                           cwd=self.directory.name, env=minimal_environment(),
                           timeout_seconds=options.pop("timeout_seconds", 5), **options)

    def test_round_trip_stdin_without_shell(self):
        result = self.run_code("import sys; print(sys.stdin.read())", input_text="hello ; echo never")
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["stdout"].strip(), "hello ; echo never")

    def test_timeout_kills_owned_process(self):
        result = self.run_code("import time; time.sleep(10)", timeout_seconds=0.15)
        self.assertTrue(result["timed_out"])
        self.assertLess(result["duration_seconds"], 5)

    def test_combined_output_is_bounded(self):
        result = self.run_code("import sys; sys.stdout.write('x'*50000); sys.stdout.flush()", max_output_bytes=1024)
        self.assertTrue(result["output_truncated"])
        self.assertLessEqual(len(result["stdout"].encode()) + len(result["stderr"].encode()), 1024)

    def test_cancel_callback_stops_child(self):
        started = time.monotonic()
        result = self.run_code("import time; time.sleep(10)", cancel_check=lambda: time.monotonic() - started > .15)
        self.assertTrue(result["cancelled"])

    def test_check_environment_excludes_account_and_api_auth(self):
        from unittest.mock import patch
        with patch.dict(os.environ, {"OPENAI_API_KEY": "harmless-canary", "CODEX_HOME": "private-canary",
                                     "GITHUB_TOKEN": "harmless-canary", "SAGE_FAKE_SECRET": "canary"}):
            result = self.run_code("import json,os; print(json.dumps(dict(os.environ)))")
        output = json.loads(result["stdout"])
        for name in ("OPENAI_API_KEY", "CODEX_HOME", "GITHUB_TOKEN", "SAGE_FAKE_SECRET"):
            self.assertNotIn(name, output)

    def test_invalid_bounds_never_launch(self):
        for timeout in (0, -1, float("inf"), True, 3601):
            with self.subTest(timeout=timeout), self.assertRaises(ValueError):
                self.run_code("pass", timeout_seconds=timeout)

    def test_missing_executable_is_reported_safely(self):
        result = run_bounded(["sage-no-such-executable-123"], cwd=self.directory.name,
                             env=minimal_environment(), timeout_seconds=2)
        self.assertTrue(result["launch_error"])
        self.assertIsNone(result["exit_code"])


if __name__ == "__main__":
    unittest.main()
