"""Independent controller regressions, using no model or native execution."""

from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from sage_runtime.engine import Engine
from sage_runtime.providers import ModelResult
from sage_runtime.safety import Policy, SageError, _read_regular, write_project_files
from sage_runtime.schemas import REVIEW_SCHEMA, validate


PLAN = {
    "status": "READY", "summary": "Build a bounded local demonstration.",
    "questions": [], "profile": "python-stdlib", "risk": "R1",
    "technology_rationale": "Only Python's standard library is required.",
    "architecture_mermaid": "flowchart LR\n input-->output",
    "tasks": [{"id": "implementation", "description": "Build source, tests, and required documentation.",
               "paths": ["app.py", "tests/test_app.py", "README.md"]}],
    "acceptance": ["The source, tests and README exist, and behavioral checks pass."],
    "dependencies": [], "external_actions": [],
}
SOURCE = {"summary": "Implement the approved local demonstration.", "notes": [], "files": [
    {"path": "app.py", "content": "def answer():\n    return 42\n"},
    {"path": "tests/test_app.py", "content": "import unittest\nfrom app import answer\nclass TestApp(unittest.TestCase):\n    def test_answer(self):\n        self.assertEqual(answer(), 42)\n"},
    {"path": "README.md", "content": "Run python -m unittest discover -s tests.\n"},
]}


class EmptyDiscovery:
    def __init__(self, _):
        pass

    def select(self, *_):
        return {"selected": [], "omitted": [], "context": "", "authority_granted": False}


class FakeProvider:
    def __init__(self):
        self.on_review = None
        self.source = deepcopy(SOURCE)
        self.calls = []

    def generate(self, stage, prompt, schema, workspace, timeout_seconds):
        self.calls.append(stage)
        if stage == "planner":
            payload = deepcopy(PLAN)
        elif stage in ("implementer", "repairer"):
            payload = deepcopy(self.source)
        else:
            if self.on_review:
                self.on_review()
            payload = {"accepted": True, "summary": "Offline injected review.", "findings": []}
        return ModelResult(payload, {"status": "OFFLINE_TEST_DOUBLE", "no_real_model_call": True})


class FakeRunner:
    def run(self, profile, workspace, timeout_seconds):
        return {"status": "PASS", "exit_code": 0, "argv": ["offline-test-double"],
                "sandbox": "TEST_DOUBLE_NOT_LIVE", "no_real_execution": True}


class EngineAdversarialTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "kit").mkdir()
        self.provider = FakeProvider()
        self.runner = FakeRunner()
        self.discovery = patch("sage_runtime.engine.Discovery", EmptyDiscovery)
        self.discovery.start()
        self.engine = Engine(self.root / "kit", self.root / "state", self.provider, self.runner)

    def tearDown(self):
        self.discovery.stop()
        self.temp.cleanup()

    def create(self, **kwargs):
        return self.engine.create("Build a local answer module with tests and README.",
                                  self.root / "project", "offline-adversarial-test",
                                  live=True, auto_approve_plan=True, **kwargs)["run_id"]

    def test_cancel_during_final_review_cannot_be_delivered_done(self):
        run_id = self.create()
        self.provider.on_review = lambda: (self.engine.store.run_dir(run_id) / "cancel.request").touch()
        result = self.engine.run(run_id, live=True)
        self.assertEqual(result["status"], "CANCELLED")
        self.assertFalse((self.engine.store.run_dir(run_id) / "delivery.json").exists())

    def test_interrupted_verification_is_durably_time_charged_before_resume(self):
        run_id = self.create(max_seconds=1)
        self.engine.run(run_id, live=True, pause_after="IMPLEMENT")
        clock = [100.0]
        def interrupted_check(*_):
            clock[0] = 102.0
            raise KeyboardInterrupt("simulated controller interruption after elapsed sandbox work")
        with patch.object(self.runner, "run", side_effect=interrupted_check), \
                patch("sage_runtime.engine.time.monotonic", side_effect=lambda: clock[0]):
            with self.assertRaises(KeyboardInterrupt):
                self.engine.run(run_id, live=True)
        resumed = self.engine.run(run_id, live=True)
        self.assertEqual(resumed["status"], "BLOCKED")
        self.assertIn("TIME_BUDGET", resumed["reason"])
        self.assertNotIn("reviewer", self.provider.calls)

    def test_source_apply_crash_resumes_only_from_recorded_intent_and_fresh_checks(self):
        run_id = self.create()
        def crash_after_validated_write(workspace, files, policy):
            write_project_files(workspace, files, policy)
            raise KeyboardInterrupt("simulated interruption after source application")
        with patch("sage_runtime.engine.write_project_files", side_effect=crash_after_validated_write):
            with self.assertRaises(KeyboardInterrupt):
                self.engine.run(run_id, live=True)
        resumed = self.engine.run(run_id, live=True)
        self.assertEqual(resumed["status"], "DONE")
        self.assertIn("reviewer", self.provider.calls)
        self.assertEqual(self.provider.calls.count("implementer"), 1)

    def test_partial_source_apply_replays_intended_packets_without_another_model_call(self):
        run_id = self.create()
        def crash_after_first_file(workspace, files, policy):
            write_project_files(workspace, files[:1], policy)
            raise KeyboardInterrupt("simulated partial source application")
        with patch("sage_runtime.engine.write_project_files", side_effect=crash_after_first_file):
            with self.assertRaises(KeyboardInterrupt):
                self.engine.run(run_id, live=True)
        resumed = self.engine.run(run_id, live=True)
        self.assertEqual(resumed["status"], "DONE")
        self.assertTrue((self.root / "project" / "README.md").is_file())
        self.assertEqual(self.provider.calls.count("implementer"), 1)

    def test_pending_source_recovery_never_overwrites_unexplained_source_change(self):
        run_id = self.create()
        def crash_after_first_file(workspace, files, policy):
            write_project_files(workspace, files[:1], policy)
            raise KeyboardInterrupt("simulated partial source application")
        with patch("sage_runtime.engine.write_project_files", side_effect=crash_after_first_file):
            with self.assertRaises(KeyboardInterrupt):
                self.engine.run(run_id, live=True)
        source = self.root / "project" / "app.py"
        source.write_text("# unexplained external operator change\n", encoding="utf-8")
        with self.assertRaises(SageError):
            self.engine.run(run_id, live=True)
        self.assertEqual(source.read_text(encoding="utf-8"), "# unexplained external operator change\n")

    def test_missing_approved_required_file_cannot_be_declared_complete(self):
        run_id = self.create()
        self.provider.source["files"] = [item for item in self.provider.source["files"] if item["path"] != "README.md"]
        result = self.engine.run(run_id, live=True)
        self.assertNotEqual(result["status"], "DONE")
        self.assertFalse((self.engine.store.run_dir(run_id) / "delivery.json").exists())

    def test_malformed_huge_integer_is_classified_not_an_internal_overflow(self):
        with self.assertRaises(SageError) as caught:
            validate({"accepted": 10 ** 1000, "summary": "bad type", "findings": []}, REVIEW_SCHEMA)
        self.assertEqual(caught.exception.code, "INVALID_MODEL_OUTPUT")

    def test_model_unpaired_surrogate_is_rejected_before_utf8_hashing(self):
        with self.assertRaises(SageError) as caught:
            validate({"accepted": True, "summary": "\ud800", "findings": []}, REVIEW_SCHEMA)
        self.assertEqual(caught.exception.code, "INVALID_MODEL_OUTPUT")

    def test_source_context_rejects_concurrent_read_change_before_provider(self):
        run_id = self.create()
        self.engine.run(run_id, live=True, pause_after="IMPLEMENT")
        state = self.engine.store.load(run_id)
        before_calls = list(self.provider.calls)
        def tampered_read(path, limit):
            if Path(path).name == "README.md":
                return b"# concurrent unrelated source change\n"
            return _read_regular(path, limit)
        with patch("sage_runtime.engine._read_regular", side_effect=tampered_read):
            with self.assertRaises(SageError) as caught:
                self.engine._source_context(state, Policy())
        self.assertEqual(caught.exception.code, "WORKSPACE_INTEGRITY")
        self.assertEqual(self.provider.calls, before_calls)

    def test_source_context_final_recheck_rejects_change_to_already_read_file(self):
        run_id = self.create()
        self.engine.run(run_id, live=True, pause_after="IMPLEMENT")
        state = self.engine.store.load(run_id)
        before_calls = list(self.provider.calls)
        changed = [False]
        def read_then_mutate(path, limit):
            raw = _read_regular(path, limit)
            if Path(path).name == "README.md" and not changed[0]:
                changed[0] = True
                Path(path).write_text("# changed after read\n", encoding="utf-8")
            return raw
        with patch("sage_runtime.engine._read_regular", side_effect=read_then_mutate):
            with self.assertRaises(SageError) as caught:
                self.engine._source_context(state, Policy())
        self.assertEqual(caught.exception.code, "WORKSPACE_INTEGRITY")
        self.assertEqual(self.provider.calls, before_calls)


if __name__ == "__main__":
    unittest.main()
