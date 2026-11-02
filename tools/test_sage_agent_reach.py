"""Isolated contract tests for the optional Agent Reach research adapter."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest import mock

CLIENT = Path(__file__).resolve().parents[1] / "extensions" / "agent-reach" / "sage_agent_reach.py"
spec = importlib.util.spec_from_file_location("sage_agent_reach", CLIENT)
ar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ar)


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name)
        self.root = self.home / "private-state"
        self.vault = self.home / "Alireza-Brain"
        (self.vault / ".obsidian").mkdir(parents=True)

    def invoke_args(self, **overrides):
        d = {"task_id": "research.001", "agent": "sage", "authority_ref": "authorized-task-001",
             "channel": "github", "action": "search", "params_json": '["agent-reach"]',
             "timeout": 3, "event_id": "stable-event", "title": "SAGE research", "live": True}
        d.update(overrides)
        return SimpleNamespace(**d)

    def invoke(self, raw=None, **overrides):
        if raw is None:
            raw = {"ok": True, "channel": "github", "action": "search",
                   "backend": "github-api", "items": [
                       {"title": "Agent Reach", "url": "https://github.com/Panniantong/Agent-Reach?token=hidden",
                        "text": "Some public text; api_key=SUPERSECRET_1234567",
                        "author": "author", "published_at": "2026-10-23"}]}
        fake = SimpleNamespace(stdout=json.dumps(raw), stderr="", returncode=0 if raw['ok'] else 1)
        def simulate(command, **kwargs):
            if command[-1] == "version":
                return SimpleNamespace(stdout=json.dumps({"ok": True, "result": {"version": "1.6.0"}}),
                                       stderr="", returncode=0)
            return fake
        with mock.patch.object(ar.shutil, "which", return_value="/mock/agent-reach"), mock.patch.object(ar.subprocess, "run", side_effect=simulate) as run:
            code, result = ar.invoke(self.invoke_args(**overrides), self.root)
            return code, result, run.call_count

    def configure(self):
        return ar.configure_vault(SimpleNamespace(vault=str(self.vault), folder="11-AI/Research/Agent-Reach"), self.root)

    def test_declared_operations_are_read_only_and_pinned(self):
        self.assertEqual(len(ar.ACTIONS) - 1, 14)
        self.assertEqual(sum(map(len, ar.ACTIONS.values())) - 1, 40)
        for banned in ("login", "add", "uninstall", "post", "comment", "message"):
            self.assertFalse(any(banned in ops for ops in ar.ACTIONS.values()))

    def test_cli_status_never_launches_upstream(self):
        run = subprocess.run([sys.executable, str(CLIENT), "status", "--state-dir", str(self.root)],
                             capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode, 0)
        data = json.loads(run.stdout)
        self.assertFalse(data["result"]["agent_reach_version_verified"])

    def test_live_flag_required_and_paths_separate_from_repo(self):
        with self.assertRaises(ar.AdapterError) as ctx:
            ar.invoke(self.invoke_args(live=False), self.root)
        self.assertEqual(ctx.exception.code, "LIVE_OPT_IN_REQUIRED")
        with self.assertRaises(ar.AdapterError):
            ar.state_root(str(CLIENT.parents[2] / "state"))

    def test_default_report_queued_without_vault(self):
        code, output, calls = self.invoke()
        self.assertEqual((code, calls), (0, 2))
        self.assertEqual(output["report"]["status"], "PENDING")
        docs = list((self.root / "tasks").glob("*.json"))
        self.assertEqual(len(docs), 1)
        self.assertNotIn("SUPERSECRET", docs[0].read_text())
        self.assertEqual(ar.load_json(docs[0])["events"][0]["sources"][0]["url"],
                         "https://github.com/Panniantong/Agent-Reach")

    def test_idempotency_and_consistent_one_note_per_task(self):
        self.configure()
        self.invoke()
        self.invoke()
        docs = list((self.root / "tasks").glob("*.json"))
        self.assertEqual(len(ar.load_json(docs[0])["events"]), 1)
        notes = list(self.vault.rglob("*.md"))
        self.assertEqual(len(notes), 1)
        content = notes[0].read_text()
        self.assertIn("Agent Reach", content)
        self.assertNotIn("SUPERSECRET", content)
        self.assertNotIn("token=hidden", content)
        self.assertIn("sage", content)

    def test_finalize_updates_note_and_preserves_user_extras(self):
        self.configure()
        self.invoke()
        notes = list(self.vault.rglob("*.md"))
        with notes[0].open("a", encoding="utf-8") as file:
            file.write("\n## User notes\nKeep this.\n")
        answer = self.home / "answer.txt"
        answer.write_text("A researched conclusion: **redacted?** \n bearer verysecret-token-value", encoding="utf-8")
        result = ar.finalize(SimpleNamespace(task_id="research.001", agent="sage", answer_file=str(answer), title="Concluded", confidence="medium"), self.root)
        self.assertEqual(result["report"]["status"], "SYNCED")
        content = notes[0].read_text()
        self.assertIn("Keep this.", content)
        self.assertIn("A researched conclusion", content)
        self.assertNotIn("verysecret-token-value", content)
        self.assertIn("medium", content)
        self.assertEqual(len(list(self.vault.rglob("*.md"))), 1)

    def test_external_edit_in_managed_region_is_detected(self):
        self.configure()
        self.invoke()
        note = list(self.vault.rglob("*.md"))[0]
        note.write_text(note.read_text().replace("Agent Reach", "CHANGED CONTENT"))
        self.invoke(event_id="next-event")
        self.assertIn("CHANGED CONTENT", note.read_text())
        state = ar.sync_reports(self.root)
        self.assertEqual(state["status"], "PENDING")
        self.assertEqual(state["failed"], 1)
        self.assertEqual(state["last"], "MANAGED_NOTE_MODIFIED")

    def test_platform_block_does_not_retry_or_swap_backend(self):
        raw = {"ok": False, "channel": "youtube", "action": "read", "backend": None,
               "items": [], "error": {"code": "PLATFORM_BLOCKED", "message": "Sign in to confirm not a bot"}}
        code, result, calls = self.invoke(raw, channel="youtube", action="read", params_json='["https://youtube.com/watch?v=example"]')
        self.assertEqual((code, calls), (2, 2))
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["result"]["error"]["code"], "PLATFORM_BLOCKED")

    def test_tool_timeout_has_error_and_report(self):
        def timed(command, **kwargs):
            if command[-1] == "version":
                return SimpleNamespace(stdout=json.dumps({"ok": True, "result": {"version": "1.6.0"}}),
                                       stderr="", returncode=0)
            raise subprocess.TimeoutExpired("agent-reach", 3)
        with mock.patch.object(ar.shutil, "which", return_value="/mock/agent-reach"), mock.patch.object(ar.subprocess, "run", side_effect=timed):
            code, response = ar.invoke(self.invoke_args(event_id="timeout-001"), self.root)
        self.assertEqual(code, 2)
        self.assertEqual(response["result"]["error"]["code"], "TIMEOUT")
        self.assertEqual(response["report"]["status"], "PENDING")

    def test_version_mismatch_fails_closed_without_search(self):
        version = SimpleNamespace(stdout=json.dumps({"ok": True, "result": {"version": "1.7.0"}}),
                                  stderr="", returncode=0)
        with mock.patch.object(ar.shutil, "which", return_value="/mock/agent-reach"), mock.patch.object(ar.subprocess, "run", return_value=version) as run:
            with self.assertRaises(ar.AdapterError) as context:
                ar.invoke(self.invoke_args(), self.root)
        self.assertEqual(context.exception.code, "VERSION_MISMATCH")
        self.assertEqual(run.call_count, 1)

    def test_block_private_link_and_mutating_action(self):
        with self.assertRaises(ar.AdapterError):
            ar.parse_params('["http://127.0.0.1:1234/internal"]', "auto", "read")
        with self.assertRaises(ar.AdapterError):
            ar.parse_params('["file:///etc/passwd"]', "auto", "read")
        with self.assertRaises(ar.AdapterError) as ctx:
            ar.invoke(self.invoke_args(action="login"), self.root)
        self.assertEqual(ctx.exception.code, "ACTION_DENIED")

    def test_restore_after_vault_unavailable(self):
        self.configure()
        (self.vault / ".obsidian").rename(self.vault / ".obsidian-off")
        self.invoke()
        self.assertEqual(len(list(self.vault.rglob("*.md"))), 0)
        (self.vault / ".obsidian-off").rename(self.vault / ".obsidian")
        report = ar.sync_reports(self.root)
        self.assertEqual(report["status"], "SYNCED")
        self.assertEqual(len(list(self.vault.rglob("*.md"))), 1)

    def test_different_agents_separate_notes_and_thread_safe(self):
        self.configure()
        self.invoke(agent="sage")
        self.invoke(agent="deep-research")
        self.assertEqual(len(list(self.vault.rglob("*.md"))), 2)
        errors = []
        def worker(i):
            try:
                ar.append_record(self.root, "sage", "parallel.100", {"event_id": f"evt-{i}", "at": ar.now(),
                        "channel": "web", "action": "search", "ok": True, "query": "parallel", "sources": []})
            except Exception as exc:
                errors.append(repr(exc))
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(errors, [])
        doc = ar.load_json(ar.task_file(self.root, "sage", "parallel.100"))
        self.assertEqual(len(doc["events"]), 8)

if __name__ == "__main__":
    unittest.main()
