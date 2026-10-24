"""Offline hostile-input, persistence, crash-boundary and actual OS-lock checks."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from sage_runtime.safety import Policy, SageError, preflight_project_files, project_manifest, reject_links, safe_relative, write_project_files
from sage_runtime.storage import RunStore


class SafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.project = self.root / "project"

    def tearDown(self):
        self.temp.cleanup()

    def assertCode(self, code, fn, *args, **kwargs):
        with self.assertRaises(SageError) as caught:
            fn(*args, **kwargs)
        self.assertEqual(caught.exception.code, code)
        return caught.exception

    def test_policy_defaults_and_strict_finite_bounds(self):
        self.assertEqual(Policy().max_model_calls, 12)
        for kwargs in ({"max_model_calls": 13}, {"max_model_calls": True}, {"max_seconds": float("inf")},
                       {"max_repairs": -1}, {"max_files": 257}, {"max_context_bytes": 0},
                       {"max_project_bytes": 10, "max_file_bytes": 11}):
            with self.subTest(kwargs=kwargs):
                self.assertCode("INVALID_POLICY", Policy, **kwargs)

    def test_paths_reject_traversal_alias_devices_and_controls(self):
        bad = ("../outside.py", "/tmp/a.py", "C:/x.py", "a\\b.py", "a//b", "./a", "a/../b",
               "a:payload", "a.", "a ", " a", "a/", "con.txt", "COM1.py", "LPT¹.txt",
               "NUL", "x/PRN.js", "SAGE-W~1.JSO", "src/CONTROL~12/config.py", "x\n.py", "a\u202eb.py", "a\x00b", "a?", "a" * 101)
        for value in bad:
            with self.subTest(value=repr(value)):
                self.assertCode("UNSAFE_PATH", safe_relative, value)
        self.assertEqual(safe_relative("src/برنامه.py"), "src/برنامه.py")

    def test_protected_runtime_controls_and_credentials(self):
        for value in (".git/config", ".sage/state", ".codex/config.toml", ".github/workflows/a.yml",
                      "src/hooks/start.py", "AGENTS.md", "x/CLAUDE.md", ".env", ".env.local",
                      ".npmrc", "credentials.json", "key.pem", ".sage-workspace.json"):
            with self.subTest(value=value):
                self.assertCode("PROTECTED_PATH", safe_relative, value)

    def test_all_packets_preflight_before_any_directory_or_write(self):
        self.assertCode("UNSAFE_PATH", write_project_files, self.project,
                        [{"path": "app.py", "content": "print(1)"}, {"path": "../bad", "content": "bad"}], Policy())
        self.assertFalse(self.project.exists())

    def test_credentials_preflight_not_echoed(self):
        secret = "sk-or-v1-" + "a" * 48
        error = self.assertCode("CREDENTIAL_DETECTED", write_project_files, self.project,
                                [{"path": "ok.py", "content": "pass"}, {"path": "bad.py", "content": secret}], Policy())
        self.assertNotIn(secret, str(error))
        self.assertFalse(self.project.exists())
        self.assertCode("CREDENTIAL_DETECTED", write_project_files, self.project,
                        [{"path": "bad.py", "content": "password = 'a-real-secret-value'"}], Policy())

    def test_normal_python_node_and_web_source_and_hashes(self):
        files = [{"path": "app.py", "content": "print('سلام')\n"},
                 {"path": "package.json", "content": '{"private":true}'},
                 {"path": "web/index.html", "content": "<!doctype html><title>SAGE</title>"},
                 {"path": "README.md", "content": "Read credentials from the environment."}]
        manifest = write_project_files(self.project, files, Policy())
        self.assertEqual(manifest, project_manifest(self.project))
        self.assertEqual([record["path"] for record in manifest], sorted(packet["path"] for packet in files))
        record = next(record for record in manifest if record["path"] == "app.py")
        raw = files[0]["content"].encode("utf-8")
        self.assertEqual(record["sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(record["size_bytes"], len(raw))

    def test_dry_preflight_returns_exact_manifest_without_any_mutation(self):
        packets = [{"path": "src/app.py", "content": "pass\n"}]
        predicted = preflight_project_files(self.project, packets, Policy())
        self.assertFalse(self.project.exists())
        self.assertEqual(write_project_files(self.project, packets, Policy()), predicted)
        previous = (self.project / "src/app.py").read_bytes()
        changed = [{"path": "src/app.py", "content": "print(42)\n"}, {"path": "README.md", "content": "demo"}]
        predicted = preflight_project_files(self.project, changed, Policy())
        self.assertEqual((self.project / "src/app.py").read_bytes(), previous)
        self.assertFalse((self.project / "README.md").exists())
        self.assertEqual(write_project_files(self.project, changed, Policy()), predicted)

    def test_existing_content_not_deleted_and_late_rejection_leaves_bytes(self):
        write_project_files(self.project, [{"path": "keep.py", "content": "old"}], Policy())
        write_project_files(self.project, [{"path": "new.py", "content": "new"}], Policy())
        self.assertEqual((self.project / "keep.py").read_text(), "old")
        self.assertCode("INVALID_FILES", write_project_files, self.project,
                        [{"path": "keep.py", "content": "replace"}, {"path": "last.py", "content": "x", "command": "no"}], Policy())
        self.assertEqual((self.project / "keep.py").read_text(), "old")

    def test_bytes_and_total_file_count_limits_are_utf8_based(self):
        policy = Policy(max_file_bytes=3, max_project_bytes=6, max_files=2)
        self.assertCode("SIZE_LIMIT", write_project_files, self.project, [{"path": "a.py", "content": "سلام"}], policy)
        self.assertFalse(self.project.exists())
        write_project_files(self.project, [{"path": "a.py", "content": "abc"}, {"path": "b.py", "content": "def"}], policy)
        self.assertCode("SIZE_LIMIT", write_project_files, self.project, [{"path": "c.py", "content": "x"}], policy)
        self.assertFalse((self.project / "c.py").exists())

    def test_mutated_policy_is_revalidated(self):
        policy = Policy()
        policy.max_model_calls = 999
        self.assertCode("INVALID_POLICY", write_project_files, self.project, [{"path": "a.py", "content": "pass"}], policy)

    def test_packet_and_parent_case_aliases_and_conflicts(self):
        for packets in ([{"path": "A.py", "content": "a"}, {"path": "a.py", "content": "b"}],
                        [{"path": "Src/a.py", "content": "a"}, {"path": "src/b.py", "content": "b"}]):
            self.assertCode("DUPLICATE_PATH", write_project_files, self.project, packets, Policy())
        self.assertCode("PATH_CONFLICT", write_project_files, self.project,
                        [{"path": "src", "content": "a"}, {"path": "src/b.py", "content": "b"}], Policy())
        self.project.mkdir()
        (self.project / "SRC").mkdir()
        self.assertCode("DUPLICATE_PATH", write_project_files, self.project, [{"path": "src/a.py", "content": "a"}], Policy())

    def test_owner_marker_and_git_are_excluded_but_cannot_be_generated(self):
        self.project.mkdir()
        (self.project / ".git").mkdir()
        (self.project / ".git" / "config").write_text("opaque git metadata")
        (self.project / ".sage-workspace.json").write_text('{"owner":"controller"}')
        self.assertEqual(project_manifest(self.project), [])
        self.assertCode("PROTECTED_PATH", write_project_files, self.project,
                        [{"path": ".sage-workspace.json", "content": "{}"}], Policy())

    def test_binary_existing_file_and_invalid_unicode_are_rejected(self):
        self.project.mkdir()
        (self.project / "binary.bin").write_bytes(b"\xff")
        self.assertCode("INVALID_SOURCE", project_manifest, self.project)
        other = self.root / "other"
        self.assertCode("INVALID_SOURCE", write_project_files, other, [{"path": "x.py", "content": "\ud800"}], Policy())
        self.assertFalse(other.exists())

    def test_hardlinks_are_rejected_without_overwriting_outside_content(self):
        self.project.mkdir()
        outside = self.root / "outside.py"
        outside.write_text("untouched")
        try:
            os.link(outside, self.project / "alias.py")
        except OSError:
            self.skipTest("The filesystem does not support hardlinks.")
        self.assertCode("UNSAFE_LINK", project_manifest, self.project)
        self.assertEqual(outside.read_text(), "untouched")

    def test_symlink_ancestor_and_file_rejected_when_supported(self):
        self.project.mkdir()
        outside = self.root / "outside"
        outside.mkdir()
        link = self.project / "link"
        try:
            link.symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("Creating symlinks is not permitted by this Windows account.")
        self.assertCode("UNSAFE_LINK", project_manifest, self.project)
        self.assertCode("UNSAFE_LINK", reject_links, link / "new.py")
        self.assertCode("UNSAFE_LINK", write_project_files, link / "new-project", [{"path": "a.py", "content": "a"}], Policy())
        self.assertFalse((outside / "new-project").exists())

    def test_relative_workspace_and_parent_traversal_rejected(self):
        self.assertCode("UNSAFE_WORKSPACE", project_manifest, "relative")
        self.assertCode("UNSAFE_PATH", reject_links, self.root / "missing" / ".." / "escape")

    @unittest.skipUnless(os.name == "nt", "Windows junction inspection test")
    def test_windows_junction_reparse_rejected_without_target_mutation(self):
        self.project.mkdir()
        outside = self.root / "junction-target"
        outside.mkdir()
        (outside / "keep.py").write_text("unchanged")
        link = self.project / "junction"
        result = subprocess.run(["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(outside)],
                                capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            self.skipTest("This filesystem/account does not permit creating junctions.")
        self.assertCode("UNSAFE_LINK", project_manifest, self.project)
        self.assertCode("UNSAFE_LINK", reject_links, link / "keep.py")
        self.assertCode("UNSAFE_LINK", write_project_files, self.project, [{"path": "safe.py", "content": "pass"}], Policy())
        self.assertEqual((outside / "keep.py").read_text(), "unchanged")

    @unittest.skipUnless(os.name == "nt", "Windows protected-marker short-name test")
    def test_windows_short_name_cannot_alias_controller_owner_marker(self):
        import ctypes
        from ctypes import wintypes
        self.project.mkdir()
        marker = self.project / ".sage-workspace.json"
        marker.write_text('{"owner":"controller"}', encoding="utf-8")
        function = ctypes.WinDLL("kernel32", use_last_error=True).GetShortPathNameW
        function.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
        function.restype = wintypes.DWORD
        output = ctypes.create_unicode_buffer(32768)
        length = function(str(marker), output, len(output))
        if not length:
            self.skipTest("Short-name metadata is not available on this filesystem.")
        short_name = Path(output.value).name
        if short_name.casefold() == marker.name.casefold():
            self.skipTest("8.3 aliases are disabled on this filesystem.")
        with self.assertRaises(SageError):
            write_project_files(self.project, [{"path": short_name, "content": "untrusted source data"}], Policy())
        self.assertEqual(marker.read_text(encoding="utf-8"), '{"owner":"controller"}')


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.store = RunStore(self.root / "state")
        self.run = self.store.create({"status": "CREATED", "model_calls": 0, "policy": {"max_model_calls": 12}})

    def tearDown(self):
        self.temp.cleanup()

    def assertCode(self, code, fn, *args, **kwargs):
        with self.assertRaises(SageError) as caught:
            fn(*args, **kwargs)
        self.assertEqual(caught.exception.code, code)

    def test_create_load_save_and_reopen_preserve_reserved_budget(self):
        self.assertEqual(len(self.run), 32)
        state = self.store.load(self.run)
        state["model_calls"] += 1
        state["status"] = "CALL_RESERVED"
        self.store.save(self.run, state)
        reopened = RunStore(self.root / "state")
        self.assertEqual(reopened.load(self.run), state)
        self.assertTrue(reopened.verify(self.run))
        changed = reopened.load(self.run)
        changed["model_calls"] = 0
        self.assertEqual(reopened.load(self.run)["model_calls"], 1)

    def test_checkpoint_ledger_binds_state_and_append_only_events(self):
        before = (self.store.run_dir(self.run) / "ledger.jsonl").read_bytes()
        record = self.store.event(self.run, "MODEL_RESERVED", {"call": 1})
        after = (self.store.run_dir(self.run) / "ledger.jsonl").read_bytes()
        self.assertTrue(after.startswith(before))
        self.assertEqual(record["seq"], 2)
        self.assertEqual(record["previous_hash"], self.store.events(self.run)[0]["hash"])
        self.assertTrue(self.store.verify(self.run))

    def test_same_thread_nested_lock_and_other_store_instance(self):
        other = RunStore(self.root / "state")
        with self.store.lock(self.run):
            self.assertEqual(other.load(self.run)["status"], "CREATED")
            other.event(self.run, "NESTED", {"safe": True})
        self.assertTrue(self.store.verify(self.run))

    def test_other_thread_cannot_take_lock(self):
        results = []
        def attempt():
            try:
                self.store.load(self.run)
            except SageError as error:
                results.append(error.code)
        with self.store.lock(self.run):
            thread = threading.Thread(target=attempt)
            thread.start()
            thread.join(3)
            self.assertFalse(thread.is_alive())
        self.assertEqual(results, ["RUN_LOCKED"])

    def test_actual_process_lock_released_after_termination_without_takeover(self):
        child_code = (
            "import os,sys,time; from sage_runtime.storage import RunStore; "
            "s=RunStore(sys.argv[1]); "
            "ctx=s.lock(sys.argv[2]); ctx.__enter__(); print('LOCKED',os.getpid(),flush=True); time.sleep(30)"
        )
        env = dict(os.environ)
        env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
        # Windows venv python.exe can be a redirector whose child owns the lock.
        # Terminate/wait must address the actual Python owner, not its wrapper.
        executable = getattr(sys, "_base_executable", None) or sys.executable
        process = subprocess.Popen([executable, "-c", child_code, str(self.store.base), self.run],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        try:
            self.assertEqual(process.stdout.readline().strip().split(), ["LOCKED", str(process.pid)])
            self.assertCode("RUN_LOCKED", self.store.load, self.run)
            process.terminate()
            process.wait(timeout=5)
            self.assertIsNotNone(process.returncode)
            # Observe bounded OS cleanup only after confirmed process exit.
            # Never force unlock, remove the lock file or take over a live owner.
            deadline = time.monotonic() + 3.0
            while True:
                try:
                    restored = self.store.load(self.run)
                    break
                except SageError as error:
                    if error.code != "RUN_LOCKED" or time.monotonic() >= deadline:
                        raise
                    time.sleep(min(0.05, max(0.0, deadline - time.monotonic())))
            self.assertEqual(restored["model_calls"], 0)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)
            process.stdout.close()
            process.stderr.close()

    def test_orphan_snapshot_from_interrupted_save_is_not_committed(self):
        directory = self.store.run_dir(self.run) / "checkpoints"
        (directory / ("cp-" + "f" * 32 + ".json")).write_text('{"status":"not committed"}')
        self.assertEqual(self.store.load(self.run)["status"], "CREATED")
        self.assertTrue(self.store.verify(self.run))

    def test_failed_ledger_append_keeps_previous_committed_checkpoint(self):
        with patch.object(self.store, "_append", side_effect=SageError("STORE_WRITE", "simulated interruption")):
            self.assertCode("STORE_WRITE", self.store.save, self.run, {"status": "UNCOMMITTED", "model_calls": 9})
        self.assertEqual(self.store.load(self.run)["status"], "CREATED")

    def test_committed_snapshot_tamper_detected_even_when_not_latest(self):
        old = self.store.events(self.run)[0]["data"]["snapshot"]
        self.store.save(self.run, {"status": "NEXT", "model_calls": 1})
        path = self.store.run_dir(self.run) / "checkpoints" / old
        path.write_text('{"altered":true}')
        self.assertCode("INTEGRITY_ERROR", self.store.verify, self.run)
        self.assertCode("INTEGRITY_ERROR", self.store.load, self.run)
        self.assertCode("INTEGRITY_ERROR", self.store.save, self.run, {"status": "MUST_NOT_HIDE_TAMPER"})

    def test_ledger_content_tamper_detected(self):
        self.store.event(self.run, "MODEL_RESERVED", {"call": 1})
        path = self.store.run_dir(self.run) / "ledger.jsonl"
        path.write_bytes(path.read_bytes().replace(b'"call":1', b'"call":0'))
        self.assertCode("INTEGRITY_ERROR", self.store.verify, self.run)

    def test_torn_final_record_fails_closed_without_truncation(self):
        path = self.store.run_dir(self.run) / "ledger.jsonl"
        before = path.read_bytes() + b'{"seq":2'
        path.write_bytes(before)
        self.assertCode("INTEGRITY_ERROR", self.store.load, self.run)
        self.assertEqual(path.read_bytes(), before)

    def test_duplicate_json_keys_in_ledger_rejected(self):
        path = self.store.run_dir(self.run) / "ledger.jsonl"
        content = path.read_bytes()
        path.write_bytes(content.replace(b'"seq":1', b'"seq":1,"seq":1'))
        self.assertCode("INTEGRITY_ERROR", self.store.verify, self.run)

    def test_reserved_checkpoint_events_and_invalid_payloads_rejected(self):
        self.assertCode("INVALID_EVENT", self.store.event, self.run, "checkpoint", {})
        self.assertCode("INVALID_EVENT", self.store.event, self.run, "\nunsafe", {})
        self.assertCode("INVALID_EVENT", self.store.event, self.run, "BAD", [])
        self.assertCode("INVALID_STATE", self.store.save, self.run, {"nan": float("nan")})
        self.assertCode("INVALID_STATE", self.store.save, self.run, {"not_json": Path("a")})
        self.assertCode("INVALID_STATE", self.store.save, self.run, {3: "not string"})
        cycle = {}
        cycle["cycle"] = cycle
        self.assertCode("STATE_LIMIT", self.store.save, self.run, cycle)
        self.assertTrue(self.store.verify(self.run))

    def test_oversized_event_and_state_have_no_committed_side_effect(self):
        before = self.store.events(self.run)
        self.assertCode("STATE_LIMIT", self.store.event, self.run, "BIG", {"value": "x" * 65536})
        with patch("sage_runtime.storage._MAX_STATE_BYTES", 128):
            self.assertCode("STATE_LIMIT", self.store.save, self.run, {"value": "x" * 129})
        self.assertEqual(self.store.events(self.run), before)

    def test_run_id_traversal_and_cross_run_snapshot_not_allowed(self):
        for run_id in ("../escape", self.run.upper(), "", "a" * 33, "../../" + self.run):
            self.assertCode("INVALID_RUN_ID", self.store.run_dir, run_id)

    def test_missing_checkpoint_and_empty_ledger_are_not_valid_runs(self):
        path = self.store.run_dir(self.run) / "ledger.jsonl"
        path.write_bytes(b"")
        self.assertCode("INTEGRITY_ERROR", self.store.load, self.run)

    def test_hardlinked_ledger_is_rejected(self):
        path = self.store.run_dir(self.run) / "ledger.jsonl"
        try:
            os.link(path, self.root / "alias-ledger")
        except OSError:
            self.skipTest("The filesystem does not support hardlinks.")
        self.assertCode("UNSAFE_LINK", self.store.verify, self.run)


if __name__ == "__main__":
    unittest.main()
