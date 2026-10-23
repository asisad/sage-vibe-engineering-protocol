"""Source-snapshot regressions. All model/check workers are explicit test doubles."""

from copy import deepcopy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from sage_runtime.engine import Engine
from sage_runtime.providers import ModelResult
from sage_runtime.safety import Policy, SageError, project_manifest, write_project_files


BROKEN = "def divide(a, b):\n    return a * b\n"
FIXED = "def divide(a, b):\n    return a / b\n"
README = "# Original division project\nDo not mutate this source project.\n"
TEST = "import unittest\nfrom calc import divide\nclass Division(unittest.TestCase):\n    def test_divide(self):\n        self.assertEqual(divide(6, 3), 2)\n"
PLAN = {
    "status": "READY", "summary": "Repair the supplied division snapshot.", "questions": [],
    "profile": "python-stdlib", "risk": "R1", "technology_rationale": "Python standard library only.",
    "architecture_mermaid": "flowchart LR\n input-->divide-->quotient",
    "tasks": [{"id": "repair", "description": "Preserve all source, tests and documentation.",
               "paths": ["README.md", "calc.py", "test_calc.py"]}],
    "acceptance": ["Division returns a/b and the original source project remains unchanged."],
    "dependencies": [], "external_actions": [],
}


class EmptyDiscovery:
    def __init__(self, _):
        pass

    def select(self, *_):
        return {"selected": [], "omitted": [], "context": "", "authority_granted": False}


class SnapshotProvider:
    def __init__(self):
        self.calls = []
        self.plan = deepcopy(PLAN)
        self.planner_source = []
        self.prompts = []

    def generate(self, stage, prompt, schema, workspace, timeout_seconds):
        self.calls.append(stage)
        self.prompts.append(prompt)
        if stage == "planner":
            path = Path(workspace) / "calc.py"
            self.planner_source.append(path.read_text(encoding="utf-8") if path.is_file() else None)
            payload = deepcopy(self.plan)
        elif stage in ("implementer", "repairer"):
            # Intentionally retain the defect on first implementation to exercise
            # the bounded repair route. This is not a real model output.
            payload = {"summary": "Offline injected snapshot mutation.", "notes": [], "files": [
                {"path": "calc.py", "content": FIXED if stage == "repairer" else BROKEN}]}
        else:
            payload = {"accepted": True, "summary": "Offline injected review.", "findings": []}
        return ModelResult(payload, {"status": "OFFLINE_TEST_DOUBLE", "no_real_model_call": True})


class SnapshotRunner:
    def __init__(self):
        self.calls = 0

    def run(self, profile, workspace, timeout_seconds):
        self.calls += 1
        passed = (Path(workspace) / "calc.py").read_text(encoding="utf-8") == FIXED
        return {"status": "PASS" if passed else "FAIL", "exit_code": 0 if passed else 1,
                "argv": ["offline-snapshot-content-test-double"], "sandbox": "TEST_DOUBLE_NOT_LIVE",
                "no_real_execution": True}


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "original"
        self.output = self.root / "fixed-copy"
        self.kit = self.root / "kit"
        self.kit.mkdir()
        self.provider = SnapshotProvider()
        self.runner = SnapshotRunner()
        self.discovery_patch = patch("sage_runtime.engine.Discovery", EmptyDiscovery)
        self.discovery_patch.start()
        self.engine = Engine(self.kit, self.root / "private-state", self.provider, self.runner)
        write_project_files(self.source, [
            {"path": "calc.py", "content": BROKEN}, {"path": "README.md", "content": README},
            {"path": "test_calc.py", "content": TEST}], Policy())

    def tearDown(self):
        self.discovery_patch.stop()
        self.temp.cleanup()

    def create(self, **kwargs):
        return self.engine.create("Fix divide to return a/b without modifying the original.", self.output,
                                  "offline-snapshot-tests", live=True, auto_approve_plan=True,
                                  source=self.source, **kwargs)["run_id"]

    def test_snapshot_bugfix_repair_preserves_original_bytes_and_hash_provenance(self):
        before = project_manifest(self.source)
        (self.source / ".git").mkdir()
        (self.source / ".git" / "config").write_text("excluded original metadata", encoding="utf-8")
        run_id = self.create()
        self.assertFalse(self.output.exists())
        self.assertEqual(self.provider.calls, [])
        state = self.engine.store.load(run_id)
        self.assertEqual(state["source_provenance"]["manifest"], before)
        self.assertEqual(state["source_provenance"]["path"], str(self.source.resolve()))
        self.assertIs(state["source_provenance"]["source_modified"], False)
        result = self.engine.run(run_id, live=True)
        self.assertEqual(result["status"], "DONE")
        self.assertEqual(result["repairs_used"], 1)
        self.assertEqual(self.provider.calls, ["planner", "implementer", "repairer", "reviewer"])
        self.assertEqual(self.provider.planner_source, [BROKEN])
        self.assertIn("Existing snapshot", self.provider.prompts[0])
        self.assertEqual(project_manifest(self.source), before)
        self.assertEqual((self.source / "calc.py").read_text(encoding="utf-8"), BROKEN)
        self.assertEqual((self.output / "calc.py").read_text(encoding="utf-8"), FIXED)
        self.assertEqual((self.output / "README.md").read_text(encoding="utf-8"), README)
        self.assertNotEqual((self.source / ".git" / "config").read_bytes(), (self.output / ".git" / "config").read_bytes())

    def test_source_and_output_and_private_roots_must_be_separate(self):
        nested_output = self.source / "nested-output"
        cases = [(self.source, nested_output), (self.root, self.output),
                 (self.kit, self.output), (self.engine.state_root, self.output)]
        for source, output in cases:
            with self.subTest(source=source, output=output):
                with self.assertRaises(SageError) as caught:
                    self.engine.create("Repair bounded local source.", output, "offline-separation-test",
                                       live=True, source=source)
                self.assertIn(caught.exception.code, {"INVALID_SOURCE", "INVALID_WORKSPACE"})
        self.assertFalse(nested_output.exists())
        self.assertFalse(self.output.exists())
        self.assertEqual(self.provider.calls, [])

    def test_source_bytes_changed_after_manifest_are_rejected_before_state_creation(self):
        original_manifest = project_manifest
        def manifest_then_change(path):
            result = original_manifest(path)
            if Path(path) == self.source:
                (self.source / "calc.py").write_text("# concurrent external source change\n", encoding="utf-8")
            return result
        with patch("sage_runtime.engine.project_manifest", side_effect=manifest_then_change):
            with self.assertRaises(SageError) as caught:
                self.create()
        self.assertEqual(caught.exception.code, "SOURCE_INTEGRITY")
        self.assertFalse(self.output.exists())
        self.assertEqual(list(self.engine.state_root.iterdir()), [])
        self.assertEqual(self.provider.calls, [])

    def test_already_read_source_change_is_rejected_by_final_snapshot_recheck(self):
        original_sha256 = hashlib.sha256
        seen = [0]
        def mutate_after_second_original_hash(data=b"", *args, **kwargs):
            value = original_sha256(data, *args, **kwargs)
            if data == README.encode("utf-8"):
                seen[0] += 1
                if seen[0] == 2:
                    (self.source / "README.md").write_text("# changed after this file was read\n", encoding="utf-8")
            return value
        with patch("sage_runtime.engine.hashlib.sha256", side_effect=mutate_after_second_original_hash):
            with self.assertRaises(SageError) as caught:
                self.create()
        self.assertEqual(caught.exception.code, "SOURCE_INTEGRITY")
        self.assertFalse(self.output.exists())
        self.assertEqual(self.provider.calls, [])

    def test_credentials_and_protected_files_are_not_imported_or_echoed(self):
        token = "sk-or-v1-" + "x" * 48
        (self.source / "calc.py").write_text(token, encoding="utf-8")
        with self.assertRaises(SageError) as caught:
            self.create()
        self.assertEqual(caught.exception.code, "CREDENTIAL_DETECTED")
        self.assertNotIn(token, str(caught.exception))
        self.assertFalse(self.output.exists())
        self.assertEqual(list(self.engine.state_root.iterdir()), [])
        (self.source / "calc.py").write_text(BROKEN, encoding="utf-8")
        (self.source / ".env").write_text("not imported", encoding="utf-8")
        with self.assertRaises(SageError) as protected:
            self.create()
        self.assertEqual(protected.exception.code, "PROTECTED_PATH")
        self.assertEqual(self.provider.calls, [])

    def test_snapshot_over_file_limit_is_rejected_without_copy_or_provider(self):
        (self.source / "calc.py").write_text("x" * 131073, encoding="utf-8")
        with self.assertRaises(SageError) as caught:
            self.create()
        self.assertEqual(caught.exception.code, "SIZE_LIMIT")
        self.assertFalse(self.output.exists())
        self.assertEqual(list(self.engine.state_root.iterdir()), [])
        self.assertEqual(self.provider.calls, [])

    def test_cancel_before_seed_copy_keeps_output_absent_and_original_unchanged(self):
        before = project_manifest(self.source)
        run_id = self.create()
        self.engine.cancel(run_id)
        result = self.engine.run(run_id, live=True)
        self.assertEqual(result["status"], "CANCELLED")
        self.assertFalse(self.output.exists())
        self.assertEqual(project_manifest(self.source), before)
        self.assertEqual(self.provider.calls, [])

    def test_crash_after_workspace_checkpoint_does_not_skip_seed_on_resume(self):
        run_id = self.create()
        with patch("sage_runtime.engine.preflight_project_files", side_effect=KeyboardInterrupt("interrupted before seed intent")):
            with self.assertRaises(KeyboardInterrupt):
                self.engine.run(run_id, live=True)
        self.assertTrue(self.engine.store.load(run_id)["workspace_created"])
        result = self.engine.run(run_id, live=True)
        self.assertEqual(result["status"], "DONE")
        self.assertEqual(self.provider.planner_source, [BROKEN])
        self.assertEqual((self.source / "calc.py").read_text(encoding="utf-8"), BROKEN)

    def test_partial_seed_intent_recovers_before_first_planner_call(self):
        run_id = self.create()
        def interrupted_seed(workspace, files, policy):
            write_project_files(workspace, files[:1], policy)
            raise KeyboardInterrupt("interrupted partial seed copy")
        with patch("sage_runtime.engine.write_project_files", side_effect=interrupted_seed):
            with self.assertRaises(KeyboardInterrupt):
                self.engine.run(run_id, live=True)
        self.assertEqual(self.provider.calls, [])
        result = self.engine.run(run_id, live=True)
        self.assertEqual(result["status"], "DONE")
        self.assertEqual(self.provider.planner_source, [BROKEN])
        self.assertEqual((self.source / "calc.py").read_text(encoding="utf-8"), BROKEN)

    def test_planner_cannot_drop_original_snapshot_paths(self):
        run_id = self.create()
        self.provider.plan["tasks"][0]["paths"].remove("README.md")
        result = self.engine.run(run_id, live=True)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("SCOPE_DENIED", result["reason"])
        self.assertEqual(self.provider.calls, ["planner"])
        self.assertEqual((self.output / "README.md").read_text(encoding="utf-8"), README)
        self.assertEqual((self.source / "calc.py").read_text(encoding="utf-8"), BROKEN)

    def test_snapshot_clarification_retains_workspace_owner_and_resumes(self):
        before = project_manifest(self.source)
        run_id = self.create()
        self.provider.plan["status"] = "NEEDS_CLARIFICATION"
        self.provider.plan["questions"] = ["Should zero division use Python's built-in exception?"]
        paused = self.engine.run(run_id, live=True)
        self.assertEqual(paused["status"], "NEEDS_CLARIFICATION")
        marker = self.output / ".sage-workspace.json"
        previous_marker = marker.read_bytes()
        self.engine.clarify(run_id, "Use Python's built-in ZeroDivisionError.")
        self.assertEqual(self.engine.status(run_id)["status"], "READY")
        self.provider.plan = deepcopy(PLAN)
        resumed = self.engine.run(run_id, live=True)
        self.assertEqual(resumed["status"], "DONE")
        self.assertEqual(marker.read_bytes(), previous_marker)
        self.assertEqual(project_manifest(self.source), before)
        self.assertEqual(self.provider.calls.count("planner"), 2)

    def test_replanning_artifact_interruption_preserves_last_committed_evidence(self):
        run_id = self.create()
        self.provider.plan["status"] = "NEEDS_CLARIFICATION"
        self.provider.plan["questions"] = ["Should zero division use Python's built-in exception?"]
        self.assertEqual(self.engine.run(run_id, live=True)["status"], "NEEDS_CLARIFICATION")
        self.engine.clarify(run_id, "Use Python's built-in ZeroDivisionError.")
        self.provider.plan = deepcopy(PLAN)
        original_artifact = self.engine._artifact
        def interrupt_after_plan_artifact(state, name, text):
            original_artifact(state, name, text)
            if name == "plan.json":
                raise KeyboardInterrupt("interrupted after replacing a replanned artifact")
        with patch.object(self.engine, "_artifact", side_effect=interrupt_after_plan_artifact):
            with self.assertRaises(KeyboardInterrupt):
                self.engine.run(run_id, live=True)
        resumed = self.engine.run(run_id, live=True)
        self.assertEqual(resumed["status"], "DONE")
        self.assertEqual((self.source / "calc.py").read_text(encoding="utf-8"), BROKEN)


class DeliveryBudgetOfflineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).resolve().parents[3] / "tools" / "Run-SageAutonomousLive.py"
        specification = importlib.util.spec_from_file_location("sage_acceptance_budget_offline_test", path)
        cls.live = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(cls.live)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_shared_twelve_call_cap_persists_across_wrapper_reopen(self):
        provider = SnapshotProvider()
        budget = self.live.DeliveryBudget(provider, self.folder)
        for _ in range(7):
            budget.generate("reviewer", "offline", {}, self.folder, 1)
        reopened = self.live.DeliveryBudget(provider, self.folder)
        for _ in range(5):
            reopened.generate("reviewer", "offline", {}, self.folder, 1)
        with self.assertRaises(SageError) as caught:
            reopened.generate("reviewer", "offline", {}, self.folder, 1)
        self.assertEqual(caught.exception.code, "DELIVERY_BUDGET")
        self.assertEqual(len(provider.calls), 12)
        stored = json.loads((self.folder / "live-budget.json").read_text(encoding="utf-8"))
        self.assertEqual(stored["reserved_calls"], 12)
        self.assertEqual(len(stored["stages"]), 12)

    def test_failed_provider_is_reserved_before_launch_and_never_refunded(self):
        provider = SnapshotProvider()
        def unavailable(*_):
            raise SageError("PROVIDER_UNAVAILABLE", "Offline simulated provider failure")
        provider.generate = unavailable
        budget = self.live.DeliveryBudget(provider, self.folder)
        with self.assertRaises(SageError):
            budget.generate("planner", "offline", {}, self.folder, 1)
        reopened = self.live.DeliveryBudget(SnapshotProvider(), self.folder)
        stored = json.loads(reopened.path.read_text(encoding="utf-8"))
        self.assertEqual(stored["reserved_calls"], 1)

    def test_missing_shared_budget_with_previous_runs_cannot_reset_to_zero(self):
        self.live.DeliveryBudget(SnapshotProvider(), self.folder)
        (self.folder / "runs").mkdir()
        (self.folder / "live-budget.json").unlink()
        with self.assertRaises(SageError) as caught:
            self.live.DeliveryBudget(SnapshotProvider(), self.folder)
        self.assertEqual(caught.exception.code, "DELIVERY_BUDGET")
        self.assertFalse((self.folder / "live-budget.json").exists())

    def test_mutated_limit_cannot_authorize_more_than_twelve(self):
        provider = SnapshotProvider()
        budget = self.live.DeliveryBudget(provider, self.folder)
        budget.path.write_text(json.dumps({"limit": 99, "reserved_calls": 0, "stages": []}), encoding="utf-8")
        with self.assertRaises(SageError) as caught:
            budget.generate("reviewer", "offline", {}, self.folder, 1)
        self.assertEqual(caught.exception.code, "DELIVERY_BUDGET")
        self.assertEqual(provider.calls, [])

    def test_ambiguous_resume_all_is_rejected_before_provider_instantiation(self):
        argv = ["Run-SageAutonomousLive.py", "--live", "--approval-id", "offline-parser-test",
                "--evidence-root", str(self.folder), "--docker-image", "offline-unused",
                "--resume-run", "a" * 32]
        with patch.object(sys, "argv", argv), patch("sys.stderr", new=io.StringIO()), \
                patch.object(self.live, "CodexProvider", side_effect=AssertionError("must not instantiate")):
            with self.assertRaises(SystemExit) as caught:
                self.live.main()
        self.assertEqual(caught.exception.code, 2)
        self.assertEqual(list(self.folder.iterdir()), [])

    def oracle_state(self):
        workspace = self.folder / "oracle-source"
        manifest = write_project_files(workspace, [{"path": "app.py", "content": "answer = 42\n"}], Policy())
        verification = {"status": "PASS", "exit_code": 0, "sandbox": "docker-isolated",
                        "summary": {"tests_run": 3},
                        "independent_oracle_sha256": hashlib.sha256(self.live.SLUG_ORACLE.encode()).hexdigest(),
                        "oracle_source_snapshot": deepcopy(manifest),
                        "project_check": {"status": "PASS", "exit_code": 0, "sandbox": "docker-isolated",
                                          "summary": {"tests_run": 1}}}
        return {"status": "DONE", "workspace": str(workspace), "manifest": manifest, "verification": verification}

    def test_independent_acceptance_requires_expected_oracle_and_current_source(self):
        state = self.oracle_state()
        self.assertIsNone(self.live.assert_independent_acceptance(state, self.live.SLUG_ORACLE))
        for mutation in ("wrong_oracle", "wrong_snapshot", "wrong_manifest", "bare_done", "project_failed", "unsafe_backend", "oracle_not_run"):
            candidate = deepcopy(state)
            if mutation == "wrong_oracle":
                candidate["verification"]["independent_oracle_sha256"] = "0" * 64
            elif mutation == "wrong_snapshot":
                candidate["verification"]["oracle_source_snapshot"] = []
            elif mutation == "wrong_manifest":
                candidate["manifest"] = []
            elif mutation == "bare_done":
                candidate["verification"] = None
            elif mutation == "project_failed":
                candidate["verification"]["project_check"]["status"] = "FAIL"
            elif mutation == "oracle_not_run":
                candidate["verification"]["summary"]["tests_run"] = 1
            else:
                candidate["verification"]["sandbox"] = "unisolated"
            with self.subTest(mutation=mutation):
                with self.assertRaises(SageError) as caught:
                    self.live.assert_independent_acceptance(candidate, self.live.SLUG_ORACLE)
                self.assertEqual(caught.exception.code, "ACCEPTANCE_ORACLE")

    def test_independent_acceptance_rejects_process_failure_flags_despite_pass(self):
        state = self.oracle_state()
        for scope in ("oracle", "project"):
            for flag in ("timed_out", "cancelled", "output_truncated", "launch_error", "unsandboxed_fallback"):
                candidate = deepcopy(state)
                target = candidate["verification"] if scope == "oracle" else candidate["verification"]["project_check"]
                target[flag] = True
                with self.subTest(scope=scope, flag=flag):
                    with self.assertRaises(SageError) as caught:
                        self.live.assert_independent_acceptance(candidate, self.live.SLUG_ORACLE)
                    self.assertEqual(caught.exception.code, "ACCEPTANCE_ORACLE")

    def test_oracle_runner_places_oracle_in_the_actual_tests_discovery_directory(self):
        source = self.folder / "source"
        write_project_files(source, [{"path": "app.py", "content": "answer = 42\n"},
                                     {"path": "tests/test_app.py", "content": "# offline fixture, never executed\n"}], Policy())
        temporary = self.folder / "oracle-temporary"
        temporary.mkdir()
        calls = []
        class RecordingRunner:
            def run(inner, profile, workspace, timeout):
                calls.append(Path(workspace))
                return {"status": "PASS", "exit_code": 0, "sandbox": "TEST_DOUBLE_NOT_LIVE",
                        "summary": {"tests_run": 1 if len(calls) == 1 else 3}}
        wrapped = self.live.OracleRunner(RecordingRunner(), self.live.SLUG_ORACLE)
        with patch.object(self.live.tempfile, "mkdtemp", return_value=str(temporary)):
            receipt = wrapped.run("python-stdlib", source, 10)
        oracle_path = "tests/test_sage_acceptance_oracle.py"
        self.assertEqual(receipt["independent_oracle_path"], oracle_path)
        self.assertEqual((calls[1] / oracle_path).read_text(encoding="utf-8"), self.live.SLUG_ORACLE)
        self.assertFalse((calls[1] / "test_sage_acceptance_oracle.py").exists())
        self.assertFalse((source / oracle_path).exists())
        self.assertEqual(len(calls), 2)

    def test_oracle_runner_rejects_generated_source_collision_before_oracle_check(self):
        source = self.folder / "collision-source"
        oracle_path = "tests/test_sage_acceptance_oracle.py"
        write_project_files(source, [{"path": "app.py", "content": "answer = 42\n"},
                                     {"path": oracle_path, "content": "# generated reserved-name collision\n"}], Policy())
        before = project_manifest(source)
        temporary = self.folder / "collision-temporary"
        temporary.mkdir()
        calls = []
        class RecordingRunner:
            def run(inner, profile, workspace, timeout):
                calls.append(Path(workspace))
                return {"status": "PASS", "exit_code": 0, "sandbox": "TEST_DOUBLE_NOT_LIVE",
                        "summary": {"tests_run": 1}}
        wrapped = self.live.OracleRunner(RecordingRunner(), self.live.SLUG_ORACLE)
        with patch.object(self.live.tempfile, "mkdtemp", return_value=str(temporary)):
            with self.assertRaises(SageError) as caught:
                wrapped.run("python-stdlib", source, 10)
        self.assertEqual(caught.exception.code, "ACCEPTANCE_ORACLE")
        self.assertEqual(len(calls), 1)
        self.assertEqual(project_manifest(source), before)


if __name__ == "__main__":
    unittest.main()
