"""Offline proof of dispatch gates; all servers/workers here are test doubles."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

from sage_runtime.ruflo import RufloProvider, binding, load_binding, _tool_value, TOOLS, DockerCoordinator, container_user
from sage_runtime.providers import ModelResult
from sage_runtime.safety import SageError
from test_engine import FakeProvider, FakeDiscovery, FakeRunner, plan
from sage_runtime.engine import Engine


class TaskSession:
    fail_assignment = False
    corrupt_completion = False
    corrupt_persistence = False
    task = None
    def __init__(self, *args):
        self.calls = []
        self.contract_hash, self.inventory_hash = "contract", "inventory"
        self.session = types.SimpleNamespace(version="2024-11-05")
    def __enter__(self):
        return self
    def __exit__(self, *_):
        pass
    def reconcile(self):
        pass
    def call(self, tool, arguments):
        self.calls.append({"tool": tool, "arguments": deepcopy(arguments)})
        if tool == "task_create":
            self.task = dict(arguments, taskId="task-123-abc", status="pending", assignedTo=[])
        elif tool == "task_assign":
            self.task.update(status="pending" if self.fail_assignment else "in_progress", assignedTo=arguments["agentIds"])
        elif tool == "task_complete":
            self.task.update(status="completed", result=arguments["result"])
            if self.corrupt_completion:
                self.task["result"] = {"wrong": "hash"}
        elif tool == "task_cancel":
            self.task.update(status="cancelled")
        return deepcopy(self.task)
    def persisted(self, task_id):
        result = deepcopy(self.task)
        if self.corrupt_persistence:
            result["result"] = {}
        return result


class Worker(FakeProvider):
    def generate(self, *args):
        result = super().generate(*args)
        result.receipt.update(provider="codex-cli", status="COMPLETED", invocations=1, tools_executed=0,
                              test_double="OFFLINE_ONLY_NOT_REAL_EXECUTION")
        return result


class RufloTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.config = {"schema_version": "sage-ruflo-worker/0.1", "image_id": "sha256:" + "a"*64,
                       "coordination_root": str(self.root / "coordination")}
        self.worker, self.sessions = Worker(), []
        def session_factory(*args):
            session = TaskSession(*args)
            self.sessions.append(session)
            return session
        self.provider = RufloProvider(self.worker, self.root, self.config, "b"*32, "offline-test", session_factory)
    def tearDown(self):
        self.temporary.cleanup()
    def invoke(self):
        from sage_runtime.schemas import PLAN_SCHEMA
        return self.provider.generate("planner", "PRIVATE task content", PLAN_SCHEMA, self.root, 30)
    def test_actual_worker_is_gated_and_response_completion_is_not_product_acceptance(self):
        result = self.invoke()
        self.assertEqual(self.worker.calls, ["planner"])
        coordination = result.receipt["coordination"]
        self.assertEqual(coordination["execution_mode"], "SAGE_CODEX_EXTERNAL_WORKER")
        self.assertFalse(coordination["product_acceptance"])
        self.assertFalse(coordination["native_ruflo_llm_executed"])
        self.assertTrue(coordination["independent_persisted_readback"])
        self.assertNotIn("PRIVATE", json.dumps(self.sessions[0].calls))
        self.assertEqual([item["tool"] for item in self.sessions[0].calls],
                         ["task_create", "task_assign", "task_status", "task_complete", "task_status"])
    def test_failed_assignment_denies_model_and_cancels_task(self):
        with patch.object(TaskSession, "fail_assignment", True), self.assertRaises(SageError):
            self.invoke()
        self.assertEqual(self.worker.calls, [])
        self.assertEqual(self.sessions[0].task["status"], "cancelled")
    def test_unavailable_coordinator_never_falls_back_to_direct_model(self):
        self.provider.session_factory = lambda *_: (_ for _ in ()).throw(SageError("RUFLO_UNAVAILABLE", "offline"))
        with self.assertRaises(SageError):
            self.invoke()
        self.assertEqual(self.worker.calls, [])
    def test_corrupt_completion_or_persistence_is_not_accepted(self):
        for attribute in ("corrupt_completion", "corrupt_persistence"):
            with self.subTest(attribute=attribute), patch.object(TaskSession, attribute, True), self.assertRaises(SageError):
                self.invoke()
    def test_invalid_worker_payload_is_cancelled_not_completed(self):
        self.worker.plans = [{"wrong": "schema"}]
        with self.assertRaises(SageError):
            self.invoke()
        self.assertNotIn("task_complete", [row["tool"] for row in self.sessions[0].calls])
    def test_worker_failure_preserves_cancellation_and_no_product_acceptance(self):
        self.worker.generate = lambda *_: (_ for _ in ()).throw(SageError("PROVIDER_FAILED", "offline"))
        with self.assertRaises(SageError):
            self.invoke()
        self.assertEqual(self.sessions[0].task["status"], "cancelled")
    def test_cancellation_stops_before_completion(self):
        self.provider.cancel_check = lambda: True
        with self.assertRaises(SageError) as caught:
            self.invoke()
        self.assertEqual(caught.exception.code, "CANCELLED")
        self.assertEqual(self.worker.calls, [])
        self.assertEqual(self.sessions, [])
    def test_unknown_roles_and_extra_configuration_cannot_supply_commands(self):
        from sage_runtime.schemas import PLAN_SCHEMA
        with self.assertRaises(SageError):
            self.provider.generate("shell", "prompt", PLAN_SCHEMA, self.root, 30)
        for extra in ("command", "model", "allowed_tools", "credentials"):
            with self.subTest(extra=extra), self.assertRaises(SageError):
                binding(dict(self.config, **{extra: "untrusted"}))
    def test_image_tag_or_unsafe_root_or_nested_roots_are_denied(self):
        for image in ("ruflo:latest", "sha256:wrong", "../image"):
            with self.subTest(image=image), self.assertRaises(SageError):
                binding(dict(self.config, image_id=image))
        with self.assertRaises(SageError):
            binding(dict(self.config, coordination_root=str(Path.home())))
        with self.assertRaises(SageError):
            binding(self.config, state_root=self.root)
    def test_binding_file_is_bounded_and_non_executable(self):
        path = self.root / "binding.json"
        path.write_text(json.dumps(self.config), encoding="utf-8")
        self.assertEqual(load_binding(path), self.config)
        path.write_text("a"*9000, encoding="utf-8")
        with self.assertRaises(SageError):
            load_binding(path)
    def test_private_posix_mount_uses_nonroot_owner_without_permission_widening(self):
        with patch("sage_runtime.ruflo.os.name", "posix"), \
                patch("sage_runtime.ruflo.os.getuid", return_value=1001, create=True), \
                patch("sage_runtime.ruflo.os.getgid", return_value=1002, create=True):
            self.assertEqual(container_user(), "1001:1002")
        with patch("sage_runtime.ruflo.os.name", "posix"), \
                patch("sage_runtime.ruflo.os.getuid", return_value=0, create=True), self.assertRaises(SageError):
            container_user()
    def test_coordinator_cannot_mutate_original_snapshot_tree(self):
        with self.assertRaises(SageError):
            binding(self.config, source=self.root)
        with self.assertRaises(SageError):
            binding(self.config, source=self.root / "coordination")
    def test_mount_grammar_and_control_characters_are_not_path_authority(self):
        for suffix in ("folder,source=elsewhere", "line\nbreak", "line\rbreak"):
            with self.subTest(suffix=suffix), self.assertRaises(SageError):
                binding(dict(self.config, coordination_root=str(self.root / suffix)))
    def test_tool_error_or_synthetic_payload_cannot_become_success(self):
        fake = types.SimpleNamespace(is_synthetic=lambda v: "synthetic" in json.dumps(v))
        for result in ({"isError": True}, {"structuredContent": {"synthetic": True}},
                       {"structuredContent": {"success": False}}, {"content": [{"type": "text", "text": "success"}]}):
            with self.subTest(result=result), self.assertRaises(SageError):
                _tool_value(fake, result)
    def test_task_allowlist_never_advertises_native_execution_hooks_or_network(self):
        self.assertEqual(TOOLS, {"task_create", "task_assign", "task_status", "task_complete", "task_cancel"})
        with self.assertRaises(SageError):
            DockerCoordinator.call(types.SimpleNamespace(), "agent_execute", {})
    def test_reconciliation_only_cancels_this_run_unfinished_metadata(self):
        root = self.root / "metadata"
        store = root / ".claude-flow/tasks/store.json"
        store.parent.mkdir(parents=True)
        own = "SAGE structured model job " + "b"*32 + " planner interrupted"
        records = {"own-pending": {"description": own, "status": "pending"},
                   "own-done": {"description": own, "status": "completed"},
                   "other": {"description": "another system", "status": "in_progress"}}
        store.write_text(json.dumps({"tasks": records}), encoding="utf-8")
        calls = []
        def call(tool, args):
            calls.append((tool, args["taskId"]))
            return {"status": "cancelled"}
        fake = types.SimpleNamespace(volume=root, run_id="b"*32, call=call)
        DockerCoordinator.reconcile(fake)
        self.assertEqual(calls, [("task_cancel", "own-pending"), ("task_status", "own-pending")])
    def test_engine_nonlive_does_not_launch_coordinator_and_binding_survives_reload(self):
        with patch("sage_runtime.engine.Discovery", FakeDiscovery):
            engine = Engine(self.root / "kit", self.root / "runs", Worker(), FakeRunner())
        with patch("sage_runtime.ruflo.RufloProvider", side_effect=AssertionError("no activation")):
            state = engine.create("small local app", self.root / "output", "offline-test", coordinator=self.config)
            self.assertEqual(state["coordinator"], "ruflo")
            self.assertEqual(engine.run(state["run_id"])["status"], "NEEDS_AUTHORIZATION")
            self.assertEqual(engine.store.load(state["run_id"])["coordinator"], self.config)


if __name__ == "__main__":
    unittest.main()
