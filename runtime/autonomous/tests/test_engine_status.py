"""Status/cancellation regressions with explicit test doubles only.

No Git process, model, native sandbox or generated test program runs here.
Temporary local checkpoints and proposed source fixtures are the only writes.
"""
from __future__ import annotations

import copy
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from sage_runtime.engine import Engine
from sage_runtime.providers import ModelResult
from sage_runtime.safety import SageError


def local_plan():
    return {"status": "READY", "summary": "Local arithmetic fixture", "questions": [],
            "profile": "python-stdlib", "risk": "R1", "technology_rationale": "Standard library only.",
            "architecture_mermaid": "flowchart TD\n A[caller] --> B[add]",
            "tasks": [{"id": "local", "description": "Arithmetic and regression test",
                       "paths": ["app.py", "test_app.py", "README.md"]}],
            "acceptance": ["Addition returns the sum"], "dependencies": [], "external_actions": []}


class SourceDiscoveryDouble:
    def __init__(self, root):
        pass

    def select(self, idea, stage, maximum):
        return {"selected": [], "omitted": [], "source_pins": {}, "context": "Declared test-double sources"}


class ProviderDouble:
    def __init__(self):
        self.plan = local_plan()
        self.calls = []
        self.on_plan = None

    def generate(self, stage, prompt, schema, workspace, timeout_seconds):
        self.calls.append(stage)
        if stage == "planner":
            if self.on_plan:
                self.on_plan()
            payload = self.plan
        elif stage == "reviewer":
            payload = {"accepted": True, "summary": "Fixture review", "findings": []}
        else:
            payload = {"summary": "Fixture source", "notes": [], "files": [
                {"path": "app.py", "content": "def add(a, b):\n    return a + b\n"},
                {"path": "test_app.py", "content": "import unittest\nfrom app import add\nclass Check(unittest.TestCase):\n    def test_sum(self):\n        self.assertEqual(add(1, 2), 3)\n"},
                {"path": "README.md", "content": "# Local arithmetic fixture\n"}]}
        return ModelResult(copy.deepcopy(payload), {"provider": "TEST_DOUBLE", "invocations": 1})


class RunnerDouble:
    def __init__(self):
        self.calls = 0
        self.on_run = None

    def run(self, profile, workspace, timeout_seconds):
        self.calls += 1
        if self.on_run:
            self.on_run()
            return {"status": "BLOCKED", "cancelled": True, "sandbox": "TEST_DOUBLE",
                    "profile": profile, "exit_code": None}
        return {"status": "PASS", "sandbox": "TEST_DOUBLE", "profile": profile,
                "exit_code": 0, "summary": {"tests_run": 1}}


class StatusCancellationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="sage-status-unit-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        (self.root / "kit").mkdir()
        discovered = patch("sage_runtime.engine.Discovery", SourceDiscoveryDouble)
        discovered.start()
        self.addCleanup(discovered.stop)
        git = patch("sage_runtime.engine.subprocess.run", return_value=SimpleNamespace(returncode=0))
        git.start()
        self.addCleanup(git.stop)
        self.provider, self.runner = ProviderDouble(), RunnerDouble()
        self.engine = Engine(self.root / "kit", self.root / "runs", self.provider, self.runner)

    def create(self, name="project", *, auto=True):
        return self.engine.create("Build a local Python stdlib arithmetic library with a regression unittest.",
                                  self.root / name, "test-only-local-approval", live=True, auto_approve_plan=auto)

    def cancel_marker(self, run_id):
        marker = self.engine.store.run_dir(run_id) / "cancel.request"
        marker.touch()

    def assert_action_cancelled(self, operation):
        try:
            result = operation()
        except SageError as exc:
            self.assertEqual(exc.code, "CANCELLED")
        else:
            self.assertEqual(result["status"], "CANCELLED")

    def test_nonrecoverable_block_cannot_be_reopened_by_nonlive_resume(self):
        self.provider.plan["external_actions"] = ["deploy to an unapproved server"]
        state = self.create()
        initial = self.engine.run(state["run_id"], live=True)
        self.assertEqual(initial["status"], "BLOCKED")
        self.assertFalse(initial["recoverable"])
        self.assertEqual(initial["calls_used"], 1)
        no_live = self.engine.run(state["run_id"], live=False)
        self.assertEqual(no_live["status"], "BLOCKED")
        self.assertEqual(no_live["reason"], initial["reason"])
        self.assertFalse(no_live["recoverable"])
        repeated = self.engine.run(state["run_id"], live=True)
        self.assertEqual(repeated["status"], "BLOCKED")
        self.assertEqual(repeated["calls_used"], 1)
        self.assertEqual(self.provider.calls, ["planner"])
        self.assertFalse((self.root / "project").exists())

    def test_cancelled_check_has_priority_over_blocked_and_pause_states(self):
        for index, pause_after in enumerate((None, "VERIFY")):
            with self.subTest(pause_after=pause_after):
                state = self.create("project-" + str(index))
                self.runner.on_run = lambda run_id=state["run_id"]: self.cancel_marker(run_id)
                result = self.engine.run(state["run_id"], live=True, pause_after=pause_after)
                self.assertEqual(result["status"], "CANCELLED")
                self.assertFalse(result["recoverable"])
                self.assertEqual(result["calls_used"], 2)
                self.assertFalse((self.engine.store.run_dir(state["run_id"]) / "delivery.json").exists())
        self.assertNotIn("reviewer", self.provider.calls)

    def test_queued_cancel_prevents_plan_approval(self):
        state = self.create(auto=False)
        waiting = self.engine.run(state["run_id"], live=True)
        self.assertEqual(waiting["status"], "WAITING_APPROVAL")
        self.cancel_marker(state["run_id"])
        self.assert_action_cancelled(lambda: self.engine.approve(state["run_id"], waiting["plan_hash"]))
        saved = self.engine.store.load(state["run_id"])
        self.assertFalse(saved["plan_approved"])
        self.assertEqual(saved["calls_used"], 1)
        self.assertFalse((self.root / "project").exists())

    def prepare_clarification(self):
        self.provider.plan.update(status="NEEDS_CLARIFICATION", questions=["Which arithmetic input format?"])
        state = self.create()
        result = self.engine.run(state["run_id"], live=True)
        self.assertEqual(result["status"], "NEEDS_CLARIFICATION")
        return state, self.engine.store.load(state["run_id"])

    def test_queued_cancel_prevents_clarification_mutation(self):
        state, before = self.prepare_clarification()
        self.cancel_marker(state["run_id"])
        self.assert_action_cancelled(lambda: self.engine.clarify(state["run_id"], "Use integer arguments."))
        after = self.engine.store.load(state["run_id"])
        self.assertEqual(after["idea_hash"], before["idea_hash"])
        self.assertEqual(after["calls_used"], 1)
        self.assertEqual(self.provider.calls, ["planner"])

    def test_pending_cancellation_is_not_hidden_by_clarification_early_return(self):
        state, _ = self.prepare_clarification()
        self.cancel_marker(state["run_id"])
        result = self.engine.run(state["run_id"], live=True)
        self.assertEqual(result["status"], "CANCELLED")
        self.assertEqual(result["calls_used"], 1)
        self.assertEqual(self.provider.calls, ["planner"])

    def test_planner_finish_cancellation_beats_clarification_result(self):
        self.provider.plan.update(status="NEEDS_CLARIFICATION", questions=["Which arithmetic input format?"])
        state = self.create()
        self.provider.on_plan = lambda: self.cancel_marker(state["run_id"])
        result = self.engine.run(state["run_id"], live=True)
        self.assertEqual(result["status"], "CANCELLED")
        self.assertEqual(result["calls_used"], 1)
        self.assertEqual(self.provider.calls, ["planner"])
        self.assertFalse((self.root / "project").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
