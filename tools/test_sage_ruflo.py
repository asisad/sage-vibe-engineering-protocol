"""Contract tests for SAGE's Ruflo transport and fail-closed boundaries."""
from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLIENT = ROOT / "extensions" / "ruflo" / "sage_ruflo.py"
PEER = ROOT / "tools" / "fixtures" / "fake_ruflo_mcp.py"


class RufloAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = str(Path(self.temp.name).resolve())
        self.command = json.dumps([sys.executable, str(PEER)])
        self.approval = Path(self.workspace) / "approval.json"
        self.run_contract = Path(self.workspace) / "sage-run.json"

    def approve(self, tool="memory_search", mode="READ_ONLY", expiry=None):
        doc = {
            "record_type": "sage_ruflo_approval", "schema_version": "sage-ruflo/0.1",
            "task_id": "test.ruflo.001", "workspace_root": self.workspace,
            "authority": {"status": "GRANTED", "approval_id": "a.test.001",
                          "source": "test_operator", "scope": ["src"] if mode == "MUTATING" else ["."]},
            "allowed_tools": [tool], "mode": mode,
            "expires_at": expiry or (dt.datetime.now(dt.timezone.utc) +
                                    dt.timedelta(minutes=10)).isoformat(),
            "max_timeout_seconds": 1 if tool == "hang_tool" else 10,
        }
        self.approval.write_text(json.dumps(doc), encoding="utf-8")
        if mode == "MUTATING":
            contract = {
                "record_type": "sage_run_contract", "schema_version": "sage-contracts/0.8",
                "run_id": "run.test.001",
                "task_packet": {"task_id": doc["task_id"],
                    "authority": doc["authority"],
                    "change_scope": {"allowed_paths": ["src"]}},
                "risk_assessment": {"task_id": doc["task_id"]},
                "gate_plan": {"task_id": doc["task_id"],
                    "gates": [{"state": "ACTIVE", "blocking": True, "status": "PASS"}]},
            }
            self.run_contract.write_text(json.dumps(contract), encoding="utf-8")

    def cli(self, action, *args):
        proc = subprocess.run([sys.executable, str(CLIENT), action, *args],
                              text=True, capture_output=True, timeout=25)
        self.assertTrue(proc.stdout.strip(), proc.stderr)
        return proc.returncode, json.loads(proc.stdout)

    def server(self, action, *args, command=None):
        return self.cli(action, "--workspace", self.workspace, "--live",
                        "--command-json", command or self.command,
                        "--ack-custom-command", *args)

    def invoke(self, tool, *args):
        run_args = ["--run-contract", str(self.run_contract)] if self.run_contract.exists() else []
        return self.server("invoke", "--tool", tool, "--approval-file",
                           str(self.approval), *run_args, *args)

    def test_status_does_not_start_runtime(self):
        code, reply = self.cli("status")
        self.assertEqual(code, 0)
        self.assertFalse(reply["executed"])
        self.assertFalse(reply["runtime_connected"])
        self.assertFalse(reply["installed_on_host"])

    def test_requires_explicit_live_and_workspace(self):
        code, result = self.cli("list", "--workspace", self.workspace)
        self.assertEqual(code, 2)
        self.assertEqual(result["error_code"], "LIVE_OPT_IN_REQUIRED")
        code, result = self.cli("probe", "--live")
        self.assertEqual(result["error_code"], "WORKSPACE_REQUIRED")

    def test_probe_negotiates_and_writes_hashed_receipt(self):
        code, reply = self.server("probe")
        self.assertEqual(code, 0, reply)
        self.assertEqual(reply["status"], "CONNECTED")
        self.assertEqual(reply["result"]["tool_count"], 5)
        path = Path(reply["receipt_path"])
        self.assertTrue(path.is_file())
        self.assertTrue(str(path).startswith(self.workspace))
        receipt = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(receipt["protocol_version"], "2025-06-18")
        self.assertEqual(receipt["receipt_sha256"], reply["receipt_sha256"])
        self.assertFalse(receipt["model_task_verified"])

    def test_list_returns_names_not_authority(self):
        code, result = self.server("list")
        self.assertEqual(code, 0, result)
        names = {x["name"]: x["read_only_policy"] for x in result["result"]["tools"]}
        self.assertTrue(names["memory_search"])
        self.assertFalse(names["agent_execute"])

    def test_real_transport_call_returns_unverified_not_done(self):
        self.approve()
        code, response = self.invoke("memory_search", "--args-json", '{"query":"sage"}')
        self.assertEqual(code, 0, response)
        self.assertTrue(response["executed"])
        self.assertEqual(response["status"], "EXECUTED_UNVERIFIED")
        self.assertFalse(response["result"]["synthetic"])
        self.assertFalse(response["model_task_verified"])
        self.assertNotIn("fake response", json.dumps(response))

    def test_batch_calls_share_one_mcp_session_and_receipt(self):
        self.approve()
        plan = Path(self.workspace) / "plan.json"
        plan.write_text(json.dumps({"steps": [
            {"tool": "memory_search", "arguments": {"query": "one"}},
            {"tool": "memory_search", "arguments": {"query": "two"}},
        ]}))
        code, reply = self.server("batch", "--batch-file", str(plan),
                                  "--approval-file", str(self.approval))
        self.assertEqual(code, 0, reply)
        self.assertEqual(reply["result"]["completed_steps"], 2)
        self.assertEqual(reply["result"]["planned_steps"], 2)
        self.assertEqual(reply["status"], "EXECUTED_UNVERIFIED")

    def test_untrusted_preview_requires_ack_and_is_not_persisted(self):
        self.approve()
        code, result = self.invoke("memory_search", "--show-result")
        self.assertEqual(code, 2)
        self.assertEqual(result["error_code"], "UNAUTHORIZED")
        code, result = self.invoke("memory_search", "--show-result",
                                   "--ack-result-disclosure")
        self.assertEqual(code, 0, result)
        self.assertIn("fake response", json.dumps(result["untrusted_redacted_previews"]))
        receipt = Path(result["receipt_path"]).read_text(encoding="utf-8")
        self.assertNotIn("fake response", receipt)

    def test_nonapproved_tool_blocked_before_server(self):
        self.approve("memory_search")
        code, response = self.invoke("agent_execute")
        self.assertEqual(code, 2)
        self.assertFalse(response["executed"])
        self.assertEqual(response["error_code"], "UNAUTHORIZED")

    def test_mutation_requires_separate_host_ack(self):
        self.approve("agent_execute", "MUTATING")
        code, result = self.invoke("agent_execute")
        self.assertEqual(result["error_code"], "UNAUTHORIZED")
        code, result = self.invoke("agent_execute", "--allow-mutation")
        self.assertEqual(result["error_code"], "UNAUTHORIZED")
        code, result = self.invoke("agent_execute", "--allow-mutation", "--ack-host-access")
        self.assertEqual(code, 0, result)
        self.assertEqual(result["status"], "EXECUTED_UNVERIFIED")
        self.assertFalse(result["host_sandbox_verified"])

    def test_native_run_contract_has_hard_gate(self):
        self.approve("agent_execute", "MUTATING")
        payload = json.loads(self.run_contract.read_text())
        payload["gate_plan"]["gates"][0]["status"] = "PENDING"
        self.run_contract.write_text(json.dumps(payload))
        code, reply = self.invoke("agent_execute", "--allow-mutation", "--ack-host-access")
        self.assertEqual(code, 2)
        self.assertEqual(reply["error_code"], "GATE_BLOCKED")

    def test_native_approval_identity_must_match(self):
        self.approve("agent_execute", "MUTATING")
        payload = json.loads(self.run_contract.read_text())
        payload["task_packet"]["authority"]["approval_id"] = "wrong"
        self.run_contract.write_text(json.dumps(payload))
        code, reply = self.invoke("agent_execute", "--allow-mutation", "--ack-host-access")
        self.assertEqual(reply["error_code"], "UNAUTHORIZED")

    def test_synthetic_worker_never_counts_as_evidence(self):
        self.approve("synthetic_test", "MUTATING")
        code, result = self.invoke("synthetic_test", "--allow-mutation", "--ack-host-access")
        self.assertEqual(code, 4, result)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertTrue(result["result"]["synthetic"])
        self.assertFalse(result["result"]["evidence_acceptable"])

    def test_upstream_error_is_blocked(self):
        self.approve("error_tool", "MUTATING")
        code, result = self.invoke("error_tool", "--allow-mutation", "--ack-host-access")
        self.assertEqual(code, 4, result)
        self.assertTrue(result["result"]["upstream_error"])

    def test_expired_authority_denied(self):
        self.approve(expiry="2001-01-01T00:00:00Z")
        code, reply = self.invoke("memory_search")
        self.assertEqual(reply["error_code"], "EXPIRED_APPROVAL")
        self.assertFalse(reply["executed"])

    def test_workspace_mismatch_denied(self):
        self.approve()
        doc = json.loads(self.approval.read_text())
        doc["workspace_root"] = "/not-the-workspace"
        self.approval.write_text(json.dumps(doc))
        code, reply = self.invoke("memory_search")
        self.assertEqual(reply["error_code"], "SCOPE_MISMATCH")

    def test_bad_mcp_version_denied(self):
        cmd = json.dumps([sys.executable, str(PEER), "wrong-version"])
        code, reply = self.server("probe", command=cmd)
        self.assertEqual(code, 2, reply)
        self.assertEqual(reply["error_code"], "VERSION_MISMATCH")

    def test_timeouts_terminate_the_process(self):
        self.approve("hang_tool", "MUTATING")
        code, reply = self.invoke("hang_tool", "--allow-mutation", "--ack-host-access")
        self.assertEqual(code, 2, reply)
        self.assertEqual(reply["error_code"], "TIMEOUT")

    def test_custom_executable_requires_ack(self):
        code, reply = self.cli("probe", "--workspace", self.workspace, "--live",
                               "--command-json", self.command)
        self.assertEqual(reply["error_code"], "UNAUTHORIZED")

    def test_malformed_arguments_do_not_reach_tool(self):
        self.approve()
        code, reply = self.invoke("memory_search", "--args-json", '["not","an","object"]')
        self.assertEqual(reply["error_code"], "INVALID_INPUT")

    def test_no_arbitrary_env_injection(self):
        code, reply = self.server("probe", "--pass-env", "NODE_OPTIONS")
        self.assertEqual(reply["error_code"], "INVALID_ENV")


if __name__ == "__main__":
    unittest.main()
