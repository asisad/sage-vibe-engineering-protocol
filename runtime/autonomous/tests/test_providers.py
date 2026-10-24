"""Offline transport tests. Fake CLI receipts never claim a live model call."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
import contextlib
import io
import time
from pathlib import Path
from unittest.mock import patch

from sage_runtime.providers import (CodexProvider, ModelResult, SandboxRunner, _DISABLED, _safe_startup_snippet,
                                    _DISABLED_CODE_MODE_NOTICE, _DISABLED_CODE_MODE_SHA256)
from sage_runtime.safety import SageError
from sage_runtime.verify_profile import python_stdlib, static_web


def completed(stdout="", stderr="", code=0, **extra):
    return {"argv": [], "exit_code": code, "stdout": stdout, "stderr": stderr,
            "duration_seconds": 0.01, "timed_out": False, "cancelled": False,
            "output_truncated": False, "launch_error": False, **extra}


class ProviderTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="sage-provider-unit-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.executable = self.root / ("codex.exe" if os.name == "nt" else "codex")
        self.executable.write_text("not executable; mocked", encoding="utf-8")
        self.provider = CodexProvider(self.executable)

    @staticmethod
    def ready():
        return {"ready": True, "version": "0.163.0", "authenticated": True}

    @staticmethod
    def fake_generate(argv, **kwargs):
        target = Path(argv[argv.index("--output-last-message") + 1])
        target.write_text('{"answer":"offline mock"}', encoding="utf-8")
        events = [{"type": "thread.started", "thread_id": "test"},
                  {"type": "turn.started"},
                  {"type": "item.completed", "item": {"type": "agent_message", "text": "mock"}},
                  {"type": "turn.completed", "usage": {"input_tokens": 1, "output_tokens": 1}}]
        return completed("\n".join(json.dumps(event) for event in events))

    def test_result_dataclass(self):
        result = ModelResult({"answer": 1}, {"mock": True})
        self.assertEqual(result.payload, {"answer": 1})

    def test_shell_wrapper_explicitly_rejected(self):
        shim = self.root / "codex.cmd"
        shim.write_text("echo not run", encoding="utf-8")
        self.assertIsNone(CodexProvider(shim).executable)

    def test_diagnostic_never_returns_raw_auth(self):
        def diagnostic(arguments, cwd, timeout_seconds=10, **kwargs):
            if arguments == ["--version"]:
                return completed("codex-cli 0.163.0")
            if arguments == ["exec", "--help"]:
                return completed("--ignore-user-config --ignore-rules --ephemeral --output-schema --output-last-message --json --disable --strict-config")
            if arguments == ["features", "list"]:
                return completed("\n".join(name + " stable true" for name in (*_DISABLED, "skip_host_skill_discovery")))
            if arguments[-2:] == ["features", "list"]:
                return completed("bootstrap supported")
            return completed("", "Logged in using ChatGPT; harmless-private-auth-detail")
        with patch.object(self.provider, "_diagnostic", side_effect=diagnostic):
            result = self.provider.doctor()
        self.assertTrue(result["ready"])
        self.assertFalse(result["model_invoked"])
        self.assertNotIn("harmless-private", json.dumps(result))

    def test_missing_shell_disable_feature_is_not_ready(self):
        def diagnostic(arguments, cwd, timeout_seconds=10, **kwargs):
            if arguments == ["--version"]:
                return completed("codex-cli 0.163.0")
            if arguments == ["exec", "--help"]:
                return completed("--ignore-user-config --ignore-rules --ephemeral --output-schema --output-last-message --json --disable --strict-config")
            if arguments == ["features", "list"]:
                return completed("\n".join(name + " stable true" for name in (*_DISABLED, "skip_host_skill_discovery") if name != "shell_tool"))
            return completed("Logged in using ChatGPT")
        with patch.object(self.provider, "_diagnostic", side_effect=diagnostic):
            self.assertFalse(self.provider.doctor()["ready"])

    def test_generate_exactly_one_tool_disabled_readonly_job(self):
        with patch.object(self.provider, "doctor", return_value=self.ready()), \
             patch("sage_runtime.providers.run_bounded", side_effect=self.fake_generate) as process:
            result = self.provider.generate("planner", "idea", {"type": "object"}, self.root, 10)
        self.assertEqual(process.call_count, 1)
        argv = process.call_args.args[0]
        self.assertIn("--ignore-user-config", argv)
        self.assertEqual(argv[argv.index("--sandbox") + 1], "read-only")
        self.assertIn("project_doc_max_bytes=0", argv)
        self.assertIn("shell_tool", argv)
        self.assertNotEqual(Path(process.call_args.kwargs["cwd"]), self.root)
        self.assertEqual(result.receipt["tools_executed"], 0)
        self.assertEqual(result.payload["answer"], "offline mock")
        self.assertNotIn("stdout", result.receipt)

    def test_no_implicit_retry_on_provider_error(self):
        with patch.object(self.provider, "doctor", return_value=self.ready()), \
             patch("sage_runtime.providers.run_bounded", return_value=completed(code=2)) as process:
            with self.assertRaises(SageError) as caught:
                self.provider.generate("implementer", "idea", {"type": "object"}, self.root, 10)
        self.assertEqual(caught.exception.code, "PROVIDER_FAILED")
        self.assertEqual(process.call_count, 1)

    def test_safe_failure_receipt_classifies_config_without_raw_secrets(self):
        failure = completed(stderr="model_providers contains reserved built-in provider IDs: openai; private-canary-value", code=1)
        with patch.object(self.provider, "doctor", return_value=self.ready()), \
             patch("sage_runtime.providers.run_bounded", return_value=failure):
            with self.assertRaises(SageError) as caught:
                self.provider.generate("planner", "idea", {"type": "object"}, self.root, 10)
        receipt = caught.exception.safe_receipt
        self.assertEqual(receipt["diagnostic_code"], "CLI_RESERVED_PROVIDER_CONFIG")
        self.assertFalse(receipt["model_turn_started_observed"])
        self.assertFalse(receipt["logs_included"])
        self.assertNotIn("private-canary-value", str(caught.exception) + json.dumps(receipt))

    def test_unknown_configuration_field_is_safely_classified(self):
        failure = completed(stderr="Error: unknown configuration field tools.view_image in -c/--config override", code=1)
        with patch.object(self.provider, "doctor", return_value=self.ready()), \
             patch("sage_runtime.providers.run_bounded", return_value=failure):
            with self.assertRaises(SageError) as caught:
                self.provider.generate("planner", "idea", {"type": "object"}, self.root, 10)
        self.assertEqual(caught.exception.safe_receipt["diagnostic_code"], "CLI_CONFIG_INVALID")

    def test_doctor_strict_preflight_never_starts_model_turn(self):
        records = []
        def diagnostic(arguments, cwd, timeout_seconds=10, **kwargs):
            records.append((arguments, kwargs))
            if arguments == ["--version"]:
                return completed("codex-cli 0.163.0")
            if arguments == ["exec", "--help"]:
                return completed("--ignore-user-config --ignore-rules --ephemeral --output-schema --output-last-message --json --disable --strict-config")
            if arguments == ["features", "list"]:
                return completed("\n".join(name + " stable true" for name in (*_DISABLED, "skip_host_skill_discovery")))
            if arguments[:2] == ["app-server", "--strict-config"]:
                self.assertEqual(arguments[-2:], ["--listen", "stdio://"])
                self.assertTrue(kwargs["clean_config"])
                self.assertNotIn("tools.view_image=false", arguments)
                self.assertFalse(any(value.startswith("model_providers.openai.") for value in arguments))
                return completed()
            return completed("Logged in using ChatGPT")
        with patch.object(self.provider, "_diagnostic", side_effect=diagnostic):
            self.assertTrue(self.provider.doctor()["ready"])
        self.assertEqual(sum(arguments[:2] == ["app-server", "--strict-config"] for arguments, kwargs in records), 1)
        self.assertFalse(any("exec" in arguments and "--help" not in arguments for arguments, kwargs in records))

    def test_tool_event_is_rejected(self):
        events = [{"type": "item.completed", "item": {"type": "command_execution"}},
                  {"type": "turn.completed"}]
        with self.assertRaises(ValueError):
            CodexProvider._check_events(events)

    def test_only_exact_intentionally_disabled_notice_is_recorded(self):
        import hashlib
        self.assertEqual(len(_DISABLED_CODE_MODE_NOTICE.encode()), 157)
        self.assertEqual(hashlib.sha256(_DISABLED_CODE_MODE_NOTICE.encode()).hexdigest(), _DISABLED_CODE_MODE_SHA256)
        notice = {"type": "item.completed", "item": {"id": "item_0", "type": "error", "message": _DISABLED_CODE_MODE_NOTICE}}
        events = [{"type": "thread.started"}, notice, {"type": "turn.started"},
                  {"type": "item.completed", "item": {"type": "agent_message"}}, {"type": "turn.completed"}]
        result = CodexProvider._check_events(events)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["code"], "CODE_MODE_HOST_INTENTIONALLY_DISABLED")
        self.assertFalse(result[0]["tool_execution"])
        self.assertFalse(result[0]["capability_enabled"])

    def test_disabled_notice_changed_duplicate_postturn_fatal_and_tool_rejected(self):
        notice = {"type": "item.completed", "item": {"id": "item_0", "type": "error", "message": _DISABLED_CODE_MODE_NOTICE}}
        prefix, suffix = {"type": "thread.started"}, [{"type": "turn.started"}, {"type": "turn.completed"}]
        invalid = [
            [prefix, {**notice, "item": {**notice["item"], "message": _DISABLED_CODE_MODE_NOTICE + " "}}, *suffix],
            [prefix, notice, notice, *suffix],
            [prefix, suffix[0], notice, suffix[1]],
            [prefix, {**notice, "item": {**notice["item"], "fatal": True}}, *suffix],
            [prefix, {**notice, "item": {**notice["item"], "command": "anything"}}, *suffix],
            [prefix, {**notice, "item": {**notice["item"], "type": "command_execution"}}, *suffix],
            [prefix, {**notice, "type": "item.started"}, *suffix],
            [notice, *suffix],
        ]
        for events in invalid:
            with self.subTest(events=events), self.assertRaises(ValueError):
                CodexProvider._check_events(events)

    def test_accepted_notice_never_enables_code_mode_or_host(self):
        from sage_runtime.providers import _config_arguments
        arguments = _config_arguments()
        for feature in ("code_mode", "code_mode_host"):
            position = arguments.index(feature)
            self.assertEqual(arguments[position - 1], "--disable")
        self.assertNotIn("tools.code_mode.enabled=false", arguments)

    def test_unknown_event_or_missing_completed_turn_rejected(self):
        for events in ([], [{"type": "turn.failed"}], [{"type": "error"}],
                       [{"type": "turn.completed"}, {"type": "turn.completed"}]):
            with self.subTest(events=events), self.assertRaises(ValueError):
                CodexProvider._check_events(events)

    def test_unsupported_stage_never_launches(self):
        with patch.object(self.provider, "doctor") as doctor, self.assertRaises(SageError):
            self.provider.generate("deploy", "idea", {"type": "object"}, self.root, 10)
        doctor.assert_not_called()

    def test_provider_cancel_is_not_reported_success(self):
        with patch.object(self.provider, "doctor", return_value=self.ready()), \
             patch("sage_runtime.providers.run_bounded", return_value=completed(cancelled=True)):
            with self.assertRaises(SageError) as caught:
                self.provider.generate("reviewer", "idea", {"type": "object"}, self.root, 10)
        self.assertEqual(caught.exception.code, "CANCELLED")

    def test_final_object_required(self):
        def not_object(argv, **kwargs):
            receipt = self.fake_generate(argv, **kwargs)
            Path(argv[argv.index("--output-last-message") + 1]).write_text("[]", encoding="utf-8")
            return receipt
        with patch.object(self.provider, "doctor", return_value=self.ready()), \
             patch("sage_runtime.providers.run_bounded", side_effect=not_object), self.assertRaises(SageError):
            self.provider.generate("reviewer", "idea", {"type": "object"}, self.root, 10)

    def test_unexpected_item_receipt_preserves_only_event_shape(self):
        def tool(argv, **kwargs):
            self.fake_generate(argv, **kwargs)
            events = [{"type": "turn.started"},
                      {"type": "item.completed", "item": {"type": "file_change", "text": "private-canary-content"}},
                      {"type": "turn.completed"}]
            return completed("\n".join(json.dumps(event) for event in events))
        with patch.object(self.provider, "doctor", return_value=self.ready()), \
             patch("sage_runtime.providers.run_bounded", side_effect=tool):
            with self.assertRaises(SageError) as caught:
                self.provider.generate("planner", "idea", {"type": "object"}, self.root, 10)
        receipt = caught.exception.safe_receipt
        self.assertEqual(receipt["response_failure_phase"], "event_validation")
        self.assertEqual(receipt["response_error_code"], "TOOL_OR_UNEXPECTED_ITEM")
        self.assertEqual(receipt["event_shapes"][1], {"type": "item.completed", "item_type": "file_change"})
        self.assertTrue(receipt["final_response_present"])
        self.assertGreater(receipt["final_response_bytes"], 0)
        self.assertNotIn("private-canary-content", json.dumps(receipt))

    def test_invalid_final_json_records_phase_and_parse_error_only(self):
        def invalid(argv, **kwargs):
            result = self.fake_generate(argv, **kwargs)
            Path(argv[argv.index("--output-last-message") + 1]).write_text("private-canary-not-json", encoding="utf-8")
            return result
        with patch.object(self.provider, "doctor", return_value=self.ready()), \
             patch("sage_runtime.providers.run_bounded", side_effect=invalid):
            with self.assertRaises(SageError) as caught:
                self.provider.generate("planner", "idea", {"type": "object"}, self.root, 10)
        receipt = caught.exception.safe_receipt
        self.assertEqual(receipt["response_failure_phase"], "response_parse")
        self.assertEqual(receipt["response_error_class"], "JSONDecodeError")
        self.assertNotIn("private-canary-not-json", json.dumps(receipt))

    def test_unknown_event_type_is_hashed_in_diagnostic(self):
        def unknown(argv, **kwargs):
            self.fake_generate(argv, **kwargs)
            return completed(json.dumps({"type": "private-canary-event"}))
        with patch.object(self.provider, "doctor", return_value=self.ready()), \
             patch("sage_runtime.providers.run_bounded", side_effect=unknown):
            with self.assertRaises(SageError) as caught:
                self.provider.generate("planner", "idea", {"type": "object"}, self.root, 10)
        receipt = caught.exception.safe_receipt
        self.assertEqual(receipt["response_error_code"], "EVENT_TYPE_UNEXPECTED")
        self.assertIsInstance(receipt["event_shapes"][0]["type"], dict)
        self.assertNotIn("private-canary-event", json.dumps(receipt))

    def test_startup_snippet_redacts_paths_emails_urls_and_tokens(self):
        message = 'Warning at "C:\\Users\\Private User\\secrets.txt" for person@example.invalid token=hidden-private-key https://example.invalid/?secret=hidden abcdefghijklmnopqrstuvwxyz12345'
        result = _safe_startup_snippet(message)
        for private in ("Private User", "secrets.txt", "person@example", "hidden-private-key", "example.invalid", "abcdefghijklmnopqrstuvwxyz"):
            self.assertNotIn(private, result)
        self.assertIn("Warning", result)

    def test_provider_doctor_consumes_same_job_deadline(self):
        def doctor(**kwargs):
            time.sleep(.04)
            return self.ready()
        with patch.object(self.provider, "doctor", side_effect=doctor), \
             patch("sage_runtime.providers.run_bounded", side_effect=self.fake_generate) as process:
            self.provider.generate("planner", "idea", {"type": "object"}, self.root, .2)
        self.assertLess(process.call_args.kwargs["timeout_seconds"], .18)


class SandboxTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="sage-sandbox-unit-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.native = self.root / "codex.exe"
        self.native.write_text("mock", encoding="utf-8")
        self.runner = SandboxRunner(self.native, docker_executable=self.root / "docker.exe",
                                    docker_image="python:3.13-slim")

    def test_unknown_stack_has_no_substitution(self):
        self.assertEqual(self.runner.run("rust", self.root, 10)["status"], "BLOCKED")

    def test_failed_native_does_not_execute_generated_code(self):
        self.runner.docker_image = None
        with patch.object(self.runner, "_native_probe", return_value={"status": "BLOCKED", "reason": "canary denied"}), \
             patch.object(self.runner, "_native_run") as execute:
            result = self.runner.run("python-stdlib", self.root, 10)
        self.assertEqual(result["status"], "BLOCKED")
        execute.assert_not_called()

    def test_missing_local_image_never_pulled(self):
        with patch("sage_runtime.providers.run_bounded", return_value=completed(code=1)) as process:
            result = self.runner._docker_run("python-stdlib", self.root, 10)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(process.call_count, 1)
        self.assertIn("inspect", process.call_args.args[0])
        self.assertNotIn("pull", process.call_args.args[0])

    def test_docker_fixed_limits_id_and_exact_cleanup(self):
        image = "sha256:" + "a" * 64
        records = []
        def process(argv, **kwargs):
            records.append((argv, kwargs))
            if "inspect" in argv:
                return completed(image + "\n")
            if "run" in argv:
                summary = {"status": "PASS", "profile": "python-stdlib", "tests_run": 1, "worker_completed": True}
                return completed("SAGE_VERIFY_RESULT:" + json.dumps(summary))
            return completed()
        with patch("sage_runtime.providers.run_bounded", side_effect=process):
            result = self.runner._docker_run("python-stdlib", self.root, 10)
        argv = records[1][0]
        for flag in ("--pull=never", "--read-only", "--cap-drop", "--pids-limit", "--memory", "--cpus"):
            self.assertIn(flag, argv)
        self.assertEqual(argv[argv.index("--network") + 1], "none")
        self.assertIn(image, argv)
        self.assertNotIn("python:3.13-slim", argv)
        self.assertNotIn("USERPROFILE", records[1][1]["env"])
        self.assertEqual(records[2][0][-1], argv[argv.index("--name") + 1])
        self.assertEqual(result["status"], "PASS")
        self.assertFalse(result["unsandboxed_fallback"])

    def test_success_exit_without_trusted_profile_marker_is_failure(self):
        result = self.runner._finish("python-stdlib", completed(), "mock", {})
        self.assertEqual(result["status"], "FAIL")

    def test_duplicate_marker_zero_tests_or_missing_worker_cannot_pass(self):
        valid = {"status": "PASS", "profile": "python-stdlib", "tests_run": 1, "worker_completed": True}
        for summary in ({**valid, "tests_run": 0}, {**valid, "worker_completed": False}):
            line = "SAGE_VERIFY_RESULT:" + json.dumps(summary)
            self.assertEqual(self.runner._finish("python-stdlib", completed(line), "mock", {})["status"], "FAIL")
        line = "SAGE_VERIFY_RESULT:" + json.dumps(valid)
        self.assertEqual(self.runner._finish("python-stdlib", completed(line + "\n" + line), "mock", {})["status"], "FAIL")

    def test_timeout_or_cancel_cannot_pass_with_marker(self):
        summary = "SAGE_VERIFY_RESULT:" + json.dumps({"status": "PASS", "profile": "python-stdlib"})
        for extra in ({"timed_out": True}, {"cancelled": True}, {"output_truncated": True}):
            result = self.runner._finish("python-stdlib", completed(summary, **extra), "mock", {})
            self.assertEqual(result["status"], "FAIL")

    def test_native_profile_is_explicit_and_windows_does_not_downgrade(self):
        argv = self.runner._native_argv(self.root, ["python", "-c", "pass"], self.root / "denied")
        self.assertIn("sage-check", argv)
        self.assertIn("permissions.sage-check.network.enabled=false", argv)
        if os.name == "nt":
            self.assertIn('windows.sandbox="mxc"', argv)
        self.assertNotIn("danger-full-access", argv)

    def test_cancellation_before_any_sandbox_command(self):
        self.runner.cancel_check = lambda: True
        with patch("sage_runtime.providers.run_bounded") as process:
            self.assertTrue(self.runner.run("python-stdlib", self.root, 10)["cancelled"])
        process.assert_not_called()

    def test_docker_inspection_and_cleanup_share_total_deadline(self):
        timeouts = []
        image = "sha256:" + "a" * 64
        def process(argv, **kwargs):
            timeouts.append(kwargs["timeout_seconds"])
            time.sleep(.03)
            if "inspect" in argv:
                return completed(image)
            if "run" in argv:
                return completed('SAGE_VERIFY_RESULT:{"status":"PASS","profile":"python-stdlib","tests_run":1,"worker_completed":true}')
            return completed()
        with patch("sage_runtime.providers.run_bounded", side_effect=process):
            result = self.runner._docker_run("python-stdlib", self.root, .5)
        self.assertEqual(result["status"], "PASS")
        self.assertLess(timeouts[1], .4)
        self.assertLess(timeouts[2], .2)


class StaticHarnessTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="sage-static-unit-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def test_static_validates_html_and_local_references_only(self):
        (self.root / "index.html").write_text('<html><head><link href="style.css"></head></html>', encoding="utf-8")
        (self.root / "style.css").write_text("body {}", encoding="utf-8")
        result = static_web(self.root)
        self.assertEqual(result["status"], "PASS")
        self.assertIn("No browser", result["limits"][0])

    def test_static_missing_entry_rejected(self):
        with self.assertRaises(ValueError):
            static_web(self.root)

    def test_static_remote_dependency_rejected(self):
        (self.root / "index.html").write_text('<html><script src="https://example.invalid/app.js"></script></html>', encoding="utf-8")
        with self.assertRaises(ValueError):
            static_web(self.root)

    def test_static_missing_or_outside_reference_rejected(self):
        for ref in ("missing.js", "../outside.js", "%2e%2e/outside.js"):
            (self.root / "index.html").write_text('<html><script src="' + ref + '"></script></html>', encoding="utf-8")
            with self.subTest(ref=ref), self.assertRaises(ValueError):
                static_web(self.root)


class PythonHarnessTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="sage-python-harness-unit-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def check_source(self, source):
        (self.root / "test_fixture.py").write_text(source, encoding="utf-8")
        # These are fixed trusted regression fixtures, not model-generated code.
        with contextlib.redirect_stderr(io.StringIO()):
            return python_stdlib(self.root)

    def test_real_unittest_completes_in_separate_interpreter(self):
        result = self.check_source("import unittest\nclass Checks(unittest.TestCase):\n def test_ok(self): self.assertEqual(2+2,4)\n")
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["tests_run"], 1)
        self.assertTrue(result["worker_completed"])

    def test_tests_directory_does_not_require_init_file(self):
        (self.root / "app.py").write_text("def add(a,b): return a+b\n", encoding="utf-8")
        (self.root / "tests").mkdir()
        (self.root / "tests" / "test_app.py").write_text("import unittest,app\nclass Checks(unittest.TestCase):\n def test_add(self): self.assertEqual(app.add(2,3),5)\n", encoding="utf-8")
        with contextlib.redirect_stderr(io.StringIO()):
            result = python_stdlib(self.root)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["tests_run"], 1)

    def test_early_exit_without_worker_completion_is_rejected(self):
        with self.assertRaises(ValueError):
            self.check_source("import os\nos._exit(0)\n")

    def test_forged_pass_then_early_exit_is_rejected(self):
        source = ('import os\nprint(\'SAGE_VERIFY_RESULT:{"status":"PASS","profile":"python-stdlib","tests_run":1}\',flush=True)\nos._exit(0)\n')
        with self.assertRaises(ValueError):
            self.check_source(source)

    def test_worker_monkeypatch_does_not_replace_outer_module(self):
        # A source module replacing its own unittest runner cannot manufacture
        # the controller's receipt by returning exit code zero with no result.
        with self.assertRaises(ValueError):
            self.check_source("import unittest,os\nunittest.TextTestRunner.run=lambda *a,**k: os._exit(0)\nclass Checks(unittest.TestCase):\n def test_ok(self): pass\n")

    def test_zero_or_all_skipped_tests_cannot_pass(self):
        with self.assertRaises(ValueError):
            self.check_source("# no tests\n")
        result = self.check_source("import unittest\n@unittest.skip('not executed')\nclass Checks(unittest.TestCase):\n def test_ok(self): pass\n")
        self.assertEqual(result["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
