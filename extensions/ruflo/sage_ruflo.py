#!/usr/bin/env python3
"""SAGE <-> Ruflo: opt-in, version-pinned, tool-allowlisted MCP stdio adapter.

This is a real JSON-RPC MCP client, NOT an agent simulator. External execution
requires --live, a narrow approval file and an operator-chosen workspace.
The adapter does NOT provide OS sandboxing; use a separately isolated host
for mutating tools. No hooks, daemon, global config or npm download is enabled.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
PROTOCOL = "2025-11-25"
MAX_MESSAGE = 1024 * 1024
MAX_TOOL_PAGES = 30
DEFAULT_COMMAND = ["npx", "--no-install", "ruflo@3.61.1", "mcp", "start"]
# Only these exact upstream names are provisionally read-only. An MCP server's
# annotations and self-reported capabilities cannot grant authority.
READ_ONLY = frozenset({
    "memory_search", "memory_retrieve", "memory_list", "memory_stats",
    "agent_list", "agent_status", "swarm_status", "swarm_health",
    "task_list", "task_status", "neural_status", "mcp_status", "hooks_list",
})
ENV_BASE = (
    "PATH", "PATHEXT", "SYSTEMROOT", "WINDIR", "COMSPEC", "HOME",
    "USERPROFILE", "APPDATA", "LOCALAPPDATA", "TMP", "TEMP",
    "TMPDIR", "LANG", "LC_ALL", "NODE_EXTRA_CA_CERTS",
)
ENV_OPT_IN = frozenset({
    "ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY",
    "GOOGLE_API_KEY", "OPENROUTER_API_KEY",
})
NAME = re.compile(r"^[a-zA-Z][a-zA-Z0-9_.-]{1,99}$")
TASK = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._:-]{2,127}$")


class BoundaryError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def digest(obj: Any) -> str:
    data = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def utcnow() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def fail(code: str, message: str) -> None:
    raise BoundaryError(code, message)


def workspace_path(value: str) -> Path:
    if not value:
        fail("WORKSPACE_REQUIRED", "An explicit --workspace is required.")
    raw = Path(value).expanduser()
    if not raw.is_absolute() or ".." in raw.parts:
        fail("INVALID_SCOPE", "Workspace must be an absolute, non-traversing path.")
    if not raw.is_dir():
        fail("INVALID_SCOPE", "Workspace directory does not exist.")
    path = raw.resolve(strict=True)
    if raw != path or path == Path(path.anchor) or path == Path.home().resolve():
        fail("INVALID_SCOPE", "Workspace cannot be a link, home directory or filesystem root.")
    if any(p.is_symlink() for p in (raw, *raw.parents)):
        fail("INVALID_SCOPE", "Symlinked workspace components are not permitted.")
    return path


def approval_for(path: str, workspace: Path, tool: str) -> dict[str, Any]:
    if not path:
        fail("UNAUTHORIZED", "A reviewed --approval-file is required for tool invocation.")
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        fail("INVALID_APPROVAL", "Approval file could not be read as JSON.")
    if not isinstance(data, dict) or data.get("record_type") != "sage_ruflo_approval":
        fail("INVALID_APPROVAL", "Wrong approval document type.")
    if data.get("schema_version") != "sage-ruflo/0.1":
        fail("INVALID_APPROVAL", "Unsupported approval version.")
    if not TASK.fullmatch(str(data.get("task_id", ""))):
        fail("INVALID_APPROVAL", "Invalid task identity.")
    auth = data.get("authority")
    if not isinstance(auth, dict) or auth.get("status") != "GRANTED":
        fail("UNAUTHORIZED", "Authority is not GRANTED.")
    if not auth.get("approval_id") or not auth.get("source") or not isinstance(auth.get("scope"), list) or not auth["scope"]:
        fail("UNAUTHORIZED", "Approval ID, source and workspace-relative scope are required.")
    for p in auth["scope"]:
        if not isinstance(p, str) or not p or p.startswith(("/", "\\")) or ":" in p or ".." in p.replace("\\", "/").split("/"):
            fail("INVALID_SCOPE", "Authority scope must contain only relative paths.")
    if data.get("workspace_root") != str(workspace):
        fail("SCOPE_MISMATCH", "Approval workspace does not match --workspace.")
    allow = data.get("allowed_tools")
    if not isinstance(allow, list) or not allow or len(allow) != len(set(map(str, allow))):
        fail("INVALID_APPROVAL", "A nonempty, nonduplicate tool allowlist is required.")
    if any(not isinstance(t, str) or not NAME.fullmatch(t) for t in allow):
        fail("INVALID_APPROVAL", "Tool names must be exact MCP identifiers.")
    if tool not in allow:
        fail("UNAUTHORIZED", "Tool is not covered by approved allowlist.")
    if data.get("mode") not in ("READ_ONLY", "MUTATING"):
        fail("INVALID_APPROVAL", "Approval mode must be READ_ONLY or MUTATING.")
    try:
        expiry = dt.datetime.fromisoformat(str(data["expires_at"]).replace("Z", "+00:00"))
        if expiry.tzinfo is None or expiry <= dt.datetime.now(dt.timezone.utc):
            fail("EXPIRED_APPROVAL", "Approval is expired or missing a timezone.")
    except (KeyError, TypeError, ValueError):
        fail("INVALID_APPROVAL", "Invalid expires_at timestamp.")
    timeout = data.get("max_timeout_seconds")
    if type(timeout) is not int or timeout < 1 or timeout > 300:
        fail("INVALID_APPROVAL", "max_timeout_seconds must be 1..300.")
    return data


def validate_run_contract(path: str | None, approval: dict[str, Any]) -> str:
    """Bind mutation to the approved native SAGE task/risk/gate triad."""
    if not path:
        fail("RUN_CONTRACT_REQUIRED", "Mutation requires an approved SAGE --run-contract.")
    try:
        contract = json.loads(Path(path).read_text(encoding="utf-8"))
        packet = contract["task_packet"]
        risk = contract["risk_assessment"]
        gates = contract["gate_plan"]
        authority = packet["authority"]
        scope = packet["change_scope"]["allowed_paths"]
    except (OSError, KeyError, TypeError, ValueError):
        fail("INVALID_RUN_CONTRACT", "SAGE run contract is incomplete or unreadable.")
    task_id = approval["task_id"]
    if contract.get("record_type") != "sage_run_contract" or contract.get("schema_version") != "sage-contracts/0.8":
        fail("INVALID_RUN_CONTRACT", "Unsupported SAGE run contract version.")
    if any(item.get("task_id") != task_id for item in (packet, risk, gates)):
        fail("RUN_IDENTITY_MISMATCH", "Task, risk and gate plan must share approved task ID.")
    if authority.get("status") != "GRANTED" or authority.get("approval_id") != approval["authority"]["approval_id"]:
        fail("UNAUTHORIZED", "Task Packet does not contain matching GRANTED authority.")
    if (authority.get("scope") != approval["authority"]["scope"]
            or not isinstance(scope, list)
            or not set(authority["scope"]).issubset(set(scope))
            or "." in scope):
        fail("SCOPE_MISMATCH", "Native SAGE scope must match the narrow approved paths.")
    gate_list = gates.get("gates")
    if (not isinstance(gate_list, list) or not gate_list or
        any(not isinstance(g, dict) for g in gate_list)):
        fail("INVALID_RUN_CONTRACT", "A nonempty gate plan is required.")
    if any(g.get("state") == "ACTIVE" and g.get("blocking") is True
           and g.get("status") != "PASS" for g in gate_list):
        fail("GATE_BLOCKED", "SAGE blocking gates are not PASS.")
    return digest(contract)


def command_for(raw: str | None) -> list[str]:
    if raw is None:
        return DEFAULT_COMMAND[:]
    try:
        command = json.loads(raw)
    except ValueError:
        fail("INVALID_COMMAND", "Custom MCP command must be a JSON array.")
    if (not isinstance(command, list) or not command or len(command) > 16
            or any(not isinstance(x, str) or not x or len(x) > 1024 for x in command)):
        fail("INVALID_COMMAND", "Invalid custom MCP argv.")
    # A custom command is trusted local code, not a shell snippet. The user
    # must also pass --ack-custom-command to execute it.
    return command


def environment(pass_env: list[str]) -> dict[str, str]:
    if any(x not in ENV_OPT_IN for x in pass_env):
        fail("INVALID_ENV", "Only explicitly approved model-credential names are allowed.")
    env = {k: os.environ[k] for k in ENV_BASE if k in os.environ}
    for k in pass_env:
        if k not in os.environ:
            fail("MISSING_CREDENTIAL", "Requested credential is absent from the environment.")
        env[k] = os.environ[k]
    return env


class McpSession:
    def __init__(self, command: list[str], cwd: Path, env: dict[str, str], timeout: int):
        self.command, self.cwd, self.env, self.timeout = command, cwd, env, timeout
        self.proc: subprocess.Popen[bytes] | None = None
        self.incoming: queue.Queue[bytes | Exception] = queue.Queue()
        self.sequence = 0
        self.server: dict[str, Any] = {}
        self.version = ""
        self.deadline = 0.0

    def __enter__(self) -> "McpSession":
        try:
            self.proc = subprocess.Popen(
                self.command, cwd=str(self.cwd), env=self.env, stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, shell=False,
                creationflags=(subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0),
                start_new_session=(os.name != "nt"),
            )
        except (OSError, ValueError):
            fail("SERVER_UNAVAILABLE", "Could not start the pinned MCP server executable.")
        threading.Thread(target=self._reader, daemon=True).start()
        self.deadline = time.monotonic() + self.timeout
        try:
            result = self.rpc("initialize", {
                "protocolVersion": PROTOCOL,
                "capabilities": {},
                "clientInfo": {"name": "sage-ruflo-adapter", "version": "0.1.0"},
            })
            if not isinstance(result, dict):
                fail("VERSION_MISMATCH", "Invalid MCP initialize response.")
            self.version = str(result.get("protocolVersion", ""))
            if self.version != PROTOCOL:
                fail("VERSION_MISMATCH", "MCP server selected protocol " + self.version + " (client offered " + PROTOCOL + ").")
            self.server = result.get("serverInfo") if isinstance(result.get("serverInfo"), dict) else {}
            self.notify("notifications/initialized")
            return self
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def _reader(self) -> None:
        assert self.proc and self.proc.stdout
        try:
            while True:
                line = self.proc.stdout.readline(MAX_MESSAGE + 1)
                if not line:
                    self.incoming.put(EOFError("MCP server closed stdout"))
                    break
                if len(line) > MAX_MESSAGE or not line.endswith(b"\n"):
                    self.incoming.put(ValueError("Oversize or malformed MCP frame"))
                    break
                self.incoming.put(line)
        except Exception as exc:
            self.incoming.put(exc)

    def _send(self, payload: dict[str, Any]) -> None:
        assert self.proc and self.proc.stdin
        blob = (json.dumps(payload, separators=(",", ":"), ensure_ascii=False) + "\n").encode()
        if len(blob) > MAX_MESSAGE:
            fail("PAYLOAD_TOO_LARGE", "MCP request exceeds the size limit.")
        try:
            self.proc.stdin.write(blob)
            self.proc.stdin.flush()
        except (OSError, ValueError):
            fail("SERVER_UNAVAILABLE", "MCP server stdin is unavailable.")

    def notify(self, name: str) -> None:
        self._send({"jsonrpc": "2.0", "method": name})

    def rpc(self, name: str, arguments: dict[str, Any]) -> Any:
        self.sequence += 1
        reqid = self.sequence
        self._send({"jsonrpc": "2.0", "id": reqid, "method": name, "params": arguments})
        deadline = self.deadline
        while True:
            remain = deadline - time.monotonic()
            if remain <= 0:
                fail("TIMEOUT", "MCP response timed out; child will be terminated.")
            try:
                line = self.incoming.get(timeout=remain)
            except queue.Empty:
                fail("TIMEOUT", "MCP response timed out; child will be terminated.")
            if isinstance(line, Exception):
                fail("PROTOCOL_ERROR", "MCP transport terminated or returned an invalid frame.")
            try:
                msg = json.loads(line)
            except (ValueError, UnicodeDecodeError):
                fail("PROTOCOL_ERROR", "MCP stdout must contain JSON-RPC frames only.")
            if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0":
                fail("PROTOCOL_ERROR", "Invalid JSON-RPC envelope.")
            if "id" not in msg:  # notifications are not responses
                continue
            if msg["id"] != reqid:
                fail("PROTOCOL_ERROR", "Out-of-sequence MCP response ID.")
            if "error" in msg:
                fail("UPSTREAM_ERROR", "MCP server reported an RPC error.")
            if "result" not in msg:
                fail("PROTOCOL_ERROR", "MCP response lacks result.")
            return msg["result"]

    def tools(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        cursor = None
        seen: set[str] = set()
        for _ in range(MAX_TOOL_PAGES):
            params = {"cursor": cursor} if cursor else {}
            response = self.rpc("tools/list", params)
            if not isinstance(response, dict) or not isinstance(response.get("tools"), list):
                fail("PROTOCOL_ERROR", "MCP tool discovery response is malformed.")
            for tool in response["tools"]:
                name = tool.get("name") if isinstance(tool, dict) else None
                if not isinstance(name, str) or not NAME.fullmatch(name) or name in seen:
                    fail("PROTOCOL_ERROR", "Invalid or duplicated MCP tool name.")
                seen.add(name)
                out.append({"name": name, "read_only_policy": name in READ_ONLY})
            next_cursor = response.get("nextCursor")
            if not next_cursor:
                return out
            if not isinstance(next_cursor, str) or next_cursor == cursor:
                fail("PROTOCOL_ERROR", "Invalid pagination cursor.")
            cursor = next_cursor
        fail("PROTOCOL_ERROR", "MCP tool enumeration exceeded the page budget.")

    def call(self, name: str, args: dict[str, Any]) -> Any:
        return self.rpc("tools/call", {"name": name, "arguments": args})

    def __exit__(self, *_: Any) -> None:
        if not self.proc:
            return
        if self.proc.poll() is None:
            try:
                if os.name == "nt":
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(self.proc.pid)],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
                else:
                    import signal
                    os.killpg(self.proc.pid, signal.SIGKILL)
            except (OSError, subprocess.TimeoutExpired):
                self.proc.kill()
        try:
            self.proc.communicate(timeout=3)
        except (OSError, subprocess.TimeoutExpired, ValueError):
            self.proc.kill()
            self.proc.wait(timeout=3)


def is_synthetic(value: Any, level: int = 0) -> bool:
    if level > 8:
        return False
    if isinstance(value, dict):
        if value.get("synthetic") is True:
            return True
        return any(is_synthetic(v, level + 1) for v in value.values())
    if isinstance(value, list):
        return any(is_synthetic(v, level + 1) for v in value[:100])
    if isinstance(value, str) and value.startswith("{") and len(value) < 100000:
        try:
            return is_synthetic(json.loads(value), level + 1)
        except ValueError:
            return False
    return False


def write_receipt(workspace: Path, data: dict[str, Any]) -> str:
    base = workspace / ".sage" / "ruflo-receipts"
    for part in (workspace / ".sage", base):
        if part.is_symlink():
            fail("INVALID_SCOPE", "Receipt directory may not be a symlink.")
        part.mkdir(mode=0o700, exist_ok=True)
    dst = base / (data["receipt_id"] + ".json")
    data["receipt_sha256"] = digest(data)
    with dst.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, indent=2, ensure_ascii=False)
    return str(dst)


def preview(value: Any, depth: int = 0) -> Any:
    """Best-effort display protection; never store previews in audit receipts."""
    if depth > 6:
        return "[DEPTH_LIMIT]"
    if isinstance(value, dict):
        out = {}
        for k, v in list(value.items())[:100]:
            if re.search(r"(token|secret|password|key|authorization|credential)", str(k), re.I):
                out[k] = "[REDACTED]"
            else:
                out[k] = preview(v, depth + 1)
        return out
    if isinstance(value, list):
        return [preview(v, depth + 1) for v in value[:100]]
    if isinstance(value, str):
        text = value[:4096]
        text = re.sub(r"(?i)\b(sk-[a-z0-9_-]{12,}|Bearer\s+\S{12,})", "[REDACTED]", text)
        return text
    return value


def planned_steps(options: argparse.Namespace) -> list[dict[str, Any]]:
    if options.action == "invoke":
        try:
            value = json.loads(options.args_json)
        except ValueError:
            fail("INVALID_INPUT", "--args-json must contain valid JSON.")
        result = [{"tool": options.tool, "arguments": value}]
    else:
        if not options.batch_file:
            fail("INVALID_INPUT", "A --batch-file is required.")
        try:
            obj = json.loads(Path(options.batch_file).read_text(encoding="utf-8"))
            result = obj["steps"]
        except (OSError, KeyError, ValueError, TypeError):
            fail("INVALID_INPUT", "Batch file must be JSON with a steps array.")
    if not isinstance(result, list) or not 1 <= len(result) <= 12:
        fail("INVALID_INPUT", "Batch contains an invalid number of steps (1..12).")
    for item in result:
        if (not isinstance(item, dict) or set(item) != {"tool", "arguments"}
                or not isinstance(item["tool"], str) or not NAME.fullmatch(item["tool"])
                or not isinstance(item["arguments"], dict)):
            fail("INVALID_INPUT", "Every step needs a valid tool and object arguments.")
    if len(json.dumps(result, ensure_ascii=False).encode()) > MAX_MESSAGE:
        fail("PAYLOAD_TOO_LARGE", "Batch plan exceeds the size budget.")
    return result


def run(options: argparse.Namespace) -> dict[str, Any]:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    if options.action == "status":
        return {"status": "AVAILABLE_NOT_ACTIVATED", "executed": False, "manifest": manifest,
                "runtime_connected": False, "installed_on_host": False}
    workspace = workspace_path(options.workspace)
    if not options.live:
        fail("LIVE_OPT_IN_REQUIRED", "No Ruflo process is started without --live.")
    cmd = command_for(options.command_json)
    if options.command_json is None:
        executable = shutil.which(cmd[0])
        if executable:
            cmd[0] = executable
    if options.command_json is not None and not options.ack_custom_command:
        fail("UNAUTHORIZED", "Custom executable requires --ack-custom-command.")
    if options.show_result and not options.ack_result_disclosure:
        fail("UNAUTHORIZED", "Displaying untrusted tool text requires --ack-result-disclosure.")

    batch = options.action in ("invoke", "batch")
    steps = planned_steps(options) if batch else []
    if batch:
        approval = approval_for(options.approval_file, workspace, steps[0]["tool"])
        for step in steps[1:]:
            approval_for(options.approval_file, workspace, step["tool"])
        mutating = any(step["tool"] not in READ_ONLY for step in steps)
        if mutating and approval["mode"] != "MUTATING":
            fail("UNAUTHORIZED", "Unknown/mutating tools require MUTATING authority.")
        if mutating and not (options.allow_mutation and options.ack_host_access):
            fail("UNAUTHORIZED", "Mutation requires --allow-mutation and --ack-host-access.")
        contract_digest = validate_run_contract(options.run_contract, approval) if mutating else None
        timeout = approval["max_timeout_seconds"]
        task_id = approval["task_id"]
    else:
        timeout, task_id, mutating, approval, contract_digest = 20, None, False, None, None
    env = environment(options.pass_env)
    started = time.monotonic()
    result_previews: list[dict[str, Any]] = []
    with McpSession(cmd, workspace, env, timeout) as session:
        if options.action == "probe":
            tools = session.tools()
            output = {"tool_count": len(tools), "tool_inventory_sha256": digest(tools)}
            state = "CONNECTED"
        elif options.action == "list":
            tools = session.tools()
            output = {"tools": tools, "tool_count": len(tools)}
            state = "CONNECTED"
        else:
            available = {t["name"] for t in session.tools()}
            if any(step["tool"] not in available for step in steps):
                fail("TOOL_NOT_FOUND", "Approved tool is not advertised by this MCP server.")
            replies: list[dict[str, Any]] = []
            state = "EXECUTED_UNVERIFIED"
            for index, step in enumerate(steps):
                tool_result = session.call(step["tool"], step["arguments"])
                synthetic = is_synthetic(tool_result)
                upstream_error = (isinstance(tool_result, dict)
                                  and tool_result.get("isError") is True)
                replies.append({
                    "index": index, "tool": step["tool"],
                    "response_sha256": digest(tool_result),
                    "response_bytes": len(json.dumps(tool_result, ensure_ascii=False).encode()),
                    "synthetic": synthetic, "upstream_error": upstream_error,
                    "evidence_acceptable": not synthetic and not upstream_error,
                })
                if options.show_result:
                    result_previews.append({"index": index, "tool": step["tool"],
                                            "preview": preview(tool_result)})
                if synthetic or upstream_error:
                    state = "BLOCKED"
                    break
            output = {"steps": replies, "completed_steps": len(replies),
                      "planned_steps": len(steps), "evidence_acceptable": state != "BLOCKED"}
            if len(steps) == 1:
                output.update(replies[0])
        receipt = {
            "receipt_id": "ruflo." + uuid.uuid4().hex, "record_type": "sage_ruflo_receipt",
            "schema_version": "sage-ruflo/0.1", "task_id": task_id, "status": state,
            "timestamp": utcnow(), "adapter": "sage.ruflo.mcp",
            "server_name": str(session.server.get("name", ""))[:128],
            "server_version": str(session.server.get("version", ""))[:64],
            "protocol_version": session.version,
            "upstream_package": manifest["upstream"]["npm_package"],
            "workspace_sha256": hashlib.sha256(str(workspace).encode()).hexdigest(),
            "command_sha256": digest(cmd), "mode": "MUTATING" if mutating else "READ_ONLY",
            "approval_id": approval["authority"]["approval_id"] if approval else None,
            "run_contract_sha256": contract_digest,
            "elapsed_milliseconds": int((time.monotonic() - started) * 1000),
            "result": output, "host_sandbox_verified": False,
            "model_task_verified": False,
        }
        location = write_receipt(workspace, receipt)
        response = {"status": state, "executed": True, "receipt_path": location,
                    "receipt_id": receipt["receipt_id"], "receipt_sha256": receipt["receipt_sha256"],
                    "result": output, "host_sandbox_verified": False, "model_task_verified": False}
        if options.show_result:
            response["untrusted_redacted_previews"] = result_previews
        return response


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("status", "probe", "list", "invoke", "batch"))
    parser.add_argument("--workspace")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--tool")
    parser.add_argument("--args-json", default="{}")
    parser.add_argument("--batch-file")
    parser.add_argument("--show-result", action="store_true")
    parser.add_argument("--ack-result-disclosure", action="store_true")
    parser.add_argument("--approval-file")
    parser.add_argument("--run-contract")
    parser.add_argument("--allow-mutation", action="store_true")
    parser.add_argument("--ack-host-access", action="store_true")
    parser.add_argument("--command-json")
    parser.add_argument("--ack-custom-command", action="store_true")
    parser.add_argument("--pass-env", action="append", default=[])
    args = parser.parse_args()
    try:
        result = run(args)
    except BoundaryError as exc:
        result = {"status": "BLOCKED", "executed": False,
                  "error_code": exc.code, "message": str(exc)}
        print(json.dumps(result, ensure_ascii=False))
        return 2
    except KeyboardInterrupt:
        print(json.dumps({"status": "CANCELLED", "executed": False}))
        return 130
    except Exception:
        print(json.dumps({"status": "BLOCKED", "executed": False,
                          "error_code": "INTERNAL_ERROR", "message": "Adapter failed safely."}))
        return 3
    print(json.dumps(result, ensure_ascii=False))
    return 4 if result["status"] == "BLOCKED" else 0


if __name__ == "__main__":
    sys.exit(main())
