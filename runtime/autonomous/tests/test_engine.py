"""Controller proofs with declared test doubles, never live models or code."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from sage_runtime.engine import Engine, digest
from sage_runtime.providers import ModelResult
from sage_runtime.safety import SageError


def plan():
    return {"status": "READY", "summary": "Local arithmetic package", "questions": [],
            "profile": "python-stdlib", "risk": "R1", "technology_rationale": "Python stdlib suffices.",
            "architecture_mermaid": "flowchart TD\n A[caller] --> B[add]",
            "tasks": [{"id": "implement", "description": "Implement and test addition",
                       "paths": ["app.py", "test_app.py", "README.md"]}],
            "acceptance": ["Addition returns arithmetic sum"], "dependencies": [], "external_actions": []}


def files():
    return {"summary": "Implemented", "notes": [], "files": [
        {"path": "app.py", "content": "def add(a, b):\n    return a + b\n"},
        {"path": "test_app.py", "content": "import unittest\nfrom app import add\nclass Addition(unittest.TestCase):\n    def test_add(self):\n        self.assertEqual(add(1, 2), 3)\n"},
        {"path": "README.md", "content": "# Addition\nA local stdlib example.\n"}]}


class FakeDiscovery:
    def __init__(self, root):
        pass

    def select(self, idea, stage, maximum):
        return {"selected": [], "omitted": [], "source_pins": {}, "context": "Test-double reference"}


class FakeProvider:
    def __init__(self):
        self.calls = []
        self.plans = []
        self.reviews = []
        self.generated = []
        self.on_review = None

    def generate(self, stage, prompt, schema, workspace, timeout_seconds):
        self.calls.append(stage)
        if stage == "planner":
            value = self.plans.pop(0) if self.plans else plan()
        elif stage == "reviewer":
            if self.on_review:
                self.on_review()
            value = self.reviews.pop(0) if self.reviews else {"accepted": True, "summary": "Reviewed fixture", "findings": []}
        else:
            value = self.generated.pop(0) if self.generated else files()
        return ModelResult(copy.deepcopy(value), {"provider": "TEST_DOUBLE", "stage": stage, "invocations": 1})


class FakeRunner:
    def __init__(self, statuses=None):
        self.statuses = list(statuses or ["PASS"])
        self.calls = 0

    def run(self, profile, workspace, timeout_seconds):
        self.calls += 1
        status = self.statuses.pop(0) if self.statuses else "PASS"
        return {"status": status, "sandbox": "TEST_DOUBLE", "profile": profile,
                "exit_code": 0 if status == "PASS" else 1,
                "summary": {"tests_run": 1, "status": status, "profile": profile}}


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="sage-engine-unit-")
        self.root = Path(self.temporary.name).resolve()
        (self.root / "kit").mkdir()
        self.discovery_patch = patch("sage_runtime.engine.Discovery", FakeDiscovery)
        self.discovery_patch.start()
        self.provider = FakeProvider()
        self.runner = FakeRunner()
        self.engine = Engine(self.root / "kit", self.root / "runs", self.provider, self.runner)

    def tearDown(self):
        self.discovery_patch.stop()
        self.temporary.cleanup()

    def create(self, **overrides):
        options = dict(live=True, auto_approve_plan=True)
        options.update(overrides)
        return self.engine.create("Build a local Python addition library with real unittest tests.",
                                  self.root / "project", "test-unit-approval", **options)

    def test_nonlive_never_calls_provider_or_creates_project(self):
        state = self.create(live=False)
        self.assertEqual(state["status"], "NEEDS_AUTHORIZATION")
        self.assertEqual(state["calls_used"], 0)
        self.assertFalse((self.root / "project").exists())
        self.assertEqual(self.engine.run(state["run_id"])["status"], "NEEDS_AUTHORIZATION")
        self.assertEqual(self.provider.calls, [])

    def test_live_requires_identifier_and_strict_boolean(self):
        with self.assertRaises(SageError):
            self.engine.create("idea", self.root / "project", None, live=True)
        state = self.create()
        with self.assertRaises(SageError):
            self.engine.run(state["run_id"], live="false")

    def test_simple_build_has_independent_review_and_bound_receipts(self):
        state = self.create()
        result = self.engine.run(state["run_id"], live=True)
        self.assertEqual(result["status"], "DONE")
        self.assertEqual(self.provider.calls, ["planner", "implementer", "reviewer"])
        self.assertEqual(result["calls_used"], 3)
        loaded = self.engine.store.load(state["run_id"])
        self.assertEqual(loaded["verification"]["manifest_hash"], digest(loaded["manifest"]))
        self.assertEqual(loaded["review"]["manifest_hash"], digest(loaded["manifest"]))
        self.assertTrue((self.engine.store.run_dir(state["run_id"]) / "delivery.json").is_file())

    def test_manual_approval_requires_current_hash(self):
        state = self.create(auto_approve_plan=False)
        result = self.engine.run(state["run_id"], live=True)
        self.assertEqual(result["status"], "WAITING_APPROVAL")
        self.assertFalse((self.root / "project").exists())
        with self.assertRaises(SageError):
            self.engine.approve(state["run_id"], "wrong")
        self.engine.approve(state["run_id"], result["plan_hash"])
        self.assertEqual(self.engine.run(state["run_id"], live=True)["status"], "DONE")

    def test_native_tool_failure_reaches_repair_with_no_claimed_pass(self):
        self.runner.statuses = ["FAIL", "PASS"]
        state = self.create()
        result = self.engine.run(state["run_id"], live=True)
        self.assertEqual(result["status"], "DONE")
        self.assertEqual(result["repairs_used"], 1)
        self.assertEqual(self.provider.calls, ["planner", "implementer", "repairer", "reviewer"])

    def test_review_findings_require_repair_and_fresh_review(self):
        self.provider.reviews = [{"accepted": False, "summary": "Gap", "findings": ["Add edge case"]}]
        state = self.create()
        result = self.engine.run(state["run_id"], live=True)
        self.assertEqual(result["status"], "DONE")
        self.assertEqual(result["calls_used"], 5)
        self.assertEqual(result["repairs_used"], 1)
        self.assertEqual(self.runner.calls, 2)

    def test_model_call_budget_is_durable_and_cannot_be_reset_by_resume(self):
        state = self.create(max_model_calls=2)
        result = self.engine.run(state["run_id"], live=True)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("MODEL_BUDGET", result["reason"])
        self.assertEqual(result["calls_used"], 2)
        self.assertEqual(self.engine.run(state["run_id"], live=True)["calls_used"], 2)

    def test_pause_after_plan_then_resume_does_not_replan(self):
        state = self.create()
        paused = self.engine.run(state["run_id"], live=True, pause_after="PLAN")
        self.assertEqual(paused["status"], "PAUSED")
        self.assertEqual(paused["calls_used"], 1)
        result = self.engine.run(state["run_id"], live=True)
        self.assertEqual(result["status"], "DONE")
        self.assertEqual(self.provider.calls.count("planner"), 1)

    def test_pause_after_implementation_does_not_regenerate(self):
        state = self.create()
        self.assertEqual(self.engine.run(state["run_id"], live=True, pause_after="IMPLEMENT")["status"], "PAUSED")
        self.assertEqual(self.engine.run(state["run_id"], live=True)["status"], "DONE")
        self.assertEqual(self.provider.calls.count("implementer"), 1)

    def test_external_actions_and_risk_escalation_never_create_source(self):
        bad = plan()
        bad["external_actions"] = ["deploy to server"]
        self.provider.plans = [bad]
        state = self.create()
        result = self.engine.run(state["run_id"], live=True)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse((self.root / "project").exists())
        with self.assertRaises(SageError):
            self.engine.approve(state["run_id"], result["plan_hash"])

    def test_capability_gap_does_not_silently_substitute_language(self):
        unsupported = plan()
        unsupported.update(status="UNSUPPORTED", summary="Native iOS runtime unavailable", profile="")
        self.provider.plans = [unsupported]
        state = self.create()
        self.assertEqual(self.engine.run(state["run_id"], live=True)["status"], "ESCALATED")
        self.assertFalse((self.root / "project").exists())

    def test_unplanned_file_rejected_before_source_write(self):
        output = files()
        output["files"].append({"path": "outside.py", "content": "# unapproved"})
        self.provider.generated = [output]
        state = self.create()
        self.assertEqual(self.engine.run(state["run_id"], live=True)["status"], "BLOCKED")
        self.assertFalse((self.root / "project/app.py").exists())

    def test_source_change_after_done_invalidates_status(self):
        state = self.create()
        self.engine.run(state["run_id"], live=True)
        (self.root / "project/app.py").write_text("# changed", encoding="utf-8")
        with self.assertRaises(SageError) as caught:
            self.engine.status(state["run_id"])
        self.assertEqual(caught.exception.code, "WORKSPACE_INTEGRITY")

    def test_missing_sandbox_blocks_without_spending_repair_calls(self):
        self.runner.statuses = ["BLOCKED"]
        state = self.create()
        result = self.engine.run(state["run_id"], live=True)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["calls_used"], 2)
        self.assertEqual(result["repairs_used"], 0)

    def test_cancel_during_review_cannot_be_completed(self):
        state = self.create()
        marker = self.engine.store.run_dir(state["run_id"]) / "cancel.request"
        self.provider.on_review = marker.touch
        result = self.engine.run(state["run_id"], live=True)
        self.assertEqual(result["status"], "CANCELLED")

    def test_cancel_before_first_call(self):
        state = self.create()
        self.engine.cancel(state["run_id"])
        self.assertEqual(self.engine.run(state["run_id"], live=True)["status"], "CANCELLED")
        self.assertEqual(self.provider.calls, [])

    def test_clarification_is_saved_and_replanned_with_same_budget(self):
        question = plan()
        question.update(status="NEEDS_CLARIFICATION", questions=["Which input format?"])
        self.provider.plans = [question, plan()]
        state = self.create()
        self.assertEqual(self.engine.run(state["run_id"], live=True)["status"], "NEEDS_CLARIFICATION")
        self.engine.clarify(state["run_id"], "Use integer function arguments.")
        result = self.engine.run(state["run_id"], live=True)
        self.assertEqual(result["status"], "DONE")
        self.assertEqual(result["calls_used"], 4)

    def test_corrupted_private_artifact_blocks_resume(self):
        state = self.create()
        self.engine.run(state["run_id"], live=True, pause_after="PLAN")
        (self.engine.store.run_dir(state["run_id"]) / "architecture.mmd").write_text("tampered", encoding="utf-8")
        with self.assertRaises(SageError):
            self.engine.run(state["run_id"], live=True)

    def test_live_input_credentials_are_rejected_before_storage(self):
        with self.assertRaises(SageError):
            self.engine.create("use api_key='real-looking-credential-value'", self.root / "project", "unit", live=True)

    def test_strict_model_output_contract_rejects_unknown_fields(self):
        bad = plan()
        bad["execute"] = "shell"
        self.provider.plans = [bad]
        state = self.create()
        result = self.engine.run(state["run_id"], live=True)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["calls_used"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
