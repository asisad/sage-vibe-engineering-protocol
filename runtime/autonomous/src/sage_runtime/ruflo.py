"""Real isolated Ruflo task coordination, with SAGE-owned Codex workers.

Ruflo never receives source, prompts, credentials, arbitrary commands or the
generated project mount. Its completed tasks describe validated model responses,
NOT product acceptance. SAGE's independent source/check/review gates stay final.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import queue
import re
import shutil
import time
import uuid

from .process import minimal_environment, run_bounded
from .providers import ModelResult
from .safety import SageError, reject_links, _read_regular, _reject_credentials
from .schemas import validate

TOOLS = frozenset({"task_create", "task_assign", "task_status", "task_complete", "task_cancel"})
STAGES = frozenset({"planner", "implementer", "reviewer", "repairer"})
VERSION = "sage-ruflo-worker/0.1"


def container_user():
    if os.name == "nt":
        return "65534:65534"
    # A private 0700 bind directory must remain accessible to its actual owner,
    # without chmod widening or root inside the container.
    if os.getuid() <= 0:
        raise SageError("RUFLO_CONFIG", "Use an unprivileged host account for private coordinator bind mounts.")
    return str(os.getuid()) + ":" + str(os.getgid())


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def binding(value, *, kit_root=None, state_root=None, output=None, source=None):
    """Pure bounded configuration validation; never starts Docker or a model."""
    if (not isinstance(value, dict) or set(value) != {"schema_version", "image_id", "coordination_root"}
            or value["schema_version"] != VERSION
            or not isinstance(value["image_id"], str)
            or not re.fullmatch(r"sha256:[a-f0-9]{64}", value["image_id"])):
        raise SageError("RUFLO_CONFIG", "Use an immutable image ID and a compatible closed coordinator configuration.")
    raw = value["coordination_root"]
    if (not isinstance(raw, str) or not Path(raw).is_absolute() or ".." in Path(raw).parts
            or "," in raw or any(ord(char) < 32 for char in raw)):
        raise SageError("RUFLO_CONFIG", "Coordination root must be an explicit absolute private directory.")
    root = reject_links(Path(raw))
    if root.parent == root or root.resolve() == Path.home().resolve():
        raise SageError("RUFLO_CONFIG", "Home and filesystem roots cannot hold disposable coordination state.")
    for protected in (kit_root, state_root, output, source):
        if protected is not None:
            other = Path(protected).resolve()
            if root.resolve().is_relative_to(other) or other.is_relative_to(root.resolve()):
                raise SageError("RUFLO_CONFIG", "Coordinator, kit, evidence and generated source must be separate trees.")
    if not root.exists() and not root.parent.is_dir():
        raise SageError("RUFLO_CONFIG", "The coordinator parent must already exist.")
    if root.exists() and not root.is_dir():
        raise SageError("RUFLO_CONFIG", "Coordinator root is not a directory.")
    return {"schema_version": VERSION, "image_id": value["image_id"], "coordination_root": str(root.resolve())}


def load_binding(path):
    target = reject_links(Path(path).absolute())
    try:
        return binding(json.loads(_read_regular(target, 8192)))
    except (ValueError, UnicodeError, TypeError):
        raise SageError("RUFLO_CONFIG", "Coordinator configuration is not bounded valid JSON.") from None


def _client(kit_root):
    path = reject_links(Path(kit_root) / "extensions/ruflo/sage_ruflo.py")
    if not path.is_file():
        raise SageError("RUFLO_UNAVAILABLE", "The SAGE-authored Ruflo MCP adapter is missing.")
    spec = importlib.util.spec_from_file_location("sage_runtime_ruflo_client", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _tool_value(client, result):
    if not isinstance(result, dict) or result.get("isError") is True or client.is_synthetic(result):
        raise SageError("RUFLO_EVIDENCE", "Errored or synthetic MCP output is not execution evidence.")
    value = result.get("structuredContent")
    if value is None:
        content = result.get("content")
        if (not isinstance(content, list) or len(content) != 1 or not isinstance(content[0], dict)
                or content[0].get("type") != "text" or not isinstance(content[0].get("text"), str)):
            raise SageError("RUFLO_EVIDENCE", "Expected one structured Ruflo task result.")
        try:
            value = json.loads(content[0]["text"])
        except ValueError:
            raise SageError("RUFLO_EVIDENCE", "Ruflo task output is not structured JSON.") from None
    if (not isinstance(value, dict) or value.get("success") is False or value.get("error")
            or client.is_synthetic(value)):
        raise SageError("RUFLO_EVIDENCE", "The upstream task operation did not succeed.")
    return value


class DockerCoordinator:
    """Lifecycle-owned stdio MCP server; only one private metadata mount."""
    def __init__(self, kit_root, configuration, run_id, approval_id, timeout, cancel_check=None):
        self.configuration = binding(configuration)
        self.client = _client(kit_root)
        self.run_id, self.approval_id = run_id, approval_id
        self.timeout, self.cancel_check = timeout, cancel_check
        self.docker = shutil.which("docker")
        if not self.docker or Path(self.docker).suffix.lower() in {".cmd", ".bat", ".ps1"}:
            raise SageError("RUFLO_UNAVAILABLE", "A native Docker CLI is required; no shell fallback.")
        if (not re.fullmatch(r"[a-f0-9]{32}", run_id) or not isinstance(approval_id, str)
                or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", approval_id)):
            raise SageError("RUFLO_AUTHORITY", "A controller run and explicit task approval are required.")
        if type(timeout) not in (int, float) or not math.isfinite(timeout) or not 1 <= timeout <= 300:
            raise SageError("RUFLO_CONFIG", "Coordinator timeout must be finite and bounded by 300 seconds.")
        self.name = "sage-ruflo-" + uuid.uuid4().hex
        self.user = container_user()
        self.nonce = uuid.uuid4().hex
        self.volume = Path(self.configuration["coordination_root"]) / run_id / "runtime"
        self.private = self.volume.parent / "grants"
        self.calls = []
        self.session = None

    def _control(self, arguments, timeout=10):
        return run_bounded([self.docker, *arguments], cwd=self.volume,
                           env=minimal_environment(), timeout_seconds=timeout,
                           max_output_bytes=131072)

    def __enter__(self):
        if self.cancel_check and self.cancel_check():
            raise SageError("CANCELLED", "Cancelled before Ruflo starts.")
        reject_links(self.volume)
        self.volume.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.private.mkdir(exist_ok=True, mode=0o700)
        reject_links(self.private)
        marker = self.volume.parent / "owner.json"
        owner = {"run_id": self.run_id, "approval_id": self.approval_id, "binding_sha256": digest(self.configuration)}
        reject_links(marker)
        if marker.exists():
            try:
                matched = json.loads(_read_regular(marker, 1024)) == owner
            except ValueError:
                matched = False
            if not matched:
                raise SageError("RUFLO_INTEGRITY", "Coordinator ownership changed.")
        else:
            marker.write_text(json.dumps(owner, sort_keys=True), encoding="utf-8")
        image = self._control(["image", "inspect", self.configuration["image_id"], "--format", "{{json .Config.Labels}}"])
        try:
            labels = json.loads(image["stdout"])
            if (image["exit_code"] != 0 or labels.get("sage.ruflo.version") != "3.61.1"
                    or labels.get("sage.ruflo.role") != "coordination-only"):
                raise ValueError()
        except (ValueError, AttributeError):
            raise SageError("RUFLO_UNAVAILABLE", "The pinned local coordination image is missing or not labeled correctly.") from None
        grant_id = "sage." + self.run_id + "." + self.nonce
        self.approval = self.private / (self.nonce + ".approval.json")
        self.contract = self.private / (self.nonce + ".contract.json")
        authority = {"status": "GRANTED", "approval_id": self.approval_id,
                     "source": "SAGE explicit live task and isolated metadata binding", "scope": [".claude-flow/"]}
        grant = {"record_type": "sage_ruflo_approval", "schema_version": "sage-ruflo/0.1",
                 "task_id": grant_id, "authority": authority, "workspace_root": str(self.volume),
                 "allowed_tools": sorted(TOOLS), "mode": "MUTATING",
                 "expires_at": (datetime.now(timezone.utc) + timedelta(seconds=self.timeout)).isoformat(),
                 "max_timeout_seconds": max(1, min(300, math.ceil(self.timeout)))}
        contract = {"record_type": "sage_run_contract", "schema_version": "sage-contracts/0.8",
                    "task_packet": {"task_id": grant_id, "authority": authority,
                                    "change_scope": {"allowed_paths": authority["scope"]}},
                    "risk_assessment": {"task_id": grant_id, "risk_level": "R1"},
                    "gate_plan": {"task_id": grant_id, "gates": [
                        {"id": "explicit-isolated-metadata-binding", "state": "ACTIVE", "blocking": True, "status": "PASS"}]}}
        self.approval.write_text(json.dumps(grant), encoding="utf-8")
        self.contract.write_text(json.dumps(contract), encoding="utf-8")
        argv = [self.docker, "run", "--rm", "-i", "--name", self.name,
                "--label", "sage.ruflo.nonce=" + self.nonce, "--pull=never", "--network", "none",
                "--read-only", "--cap-drop", "ALL", "--security-opt", "no-new-privileges:true",
                "--memory", "512m", "--cpus", "1", "--pids-limit", "64", "--user", self.user,
                "--tmpfs", "/tmp:rw,noexec,nosuid,size=32m", "--workdir", "/workspace",
                "--mount", "type=bind,source=" + str(self.volume) + ",target=/workspace",
                "--entrypoint", "/usr/bin/timeout", self.configuration["image_id"],
                "--signal=KILL", str(math.ceil(self.timeout) + 10), "/usr/local/bin/node",
                "/opt/ruflo/node_modules/ruflo/bin/ruflo.js", "mcp", "start"]
        outer = self
        class Session(self.client.McpSession):
            def rpc(self, name, arguments):
                self.sequence += 1
                reqid = self.sequence
                self._send({"jsonrpc": "2.0", "id": reqid, "method": name, "params": arguments})
                while True:
                    if outer.cancel_check and outer.cancel_check():
                        raise SageError("CANCELLED", "Cancelled while waiting for Ruflo.")
                    remain = self.deadline - time.monotonic()
                    if remain <= 0:
                        raise SageError("RUFLO_UNAVAILABLE", "The isolated Ruflo task coordinator timed out.")
                    try:
                        line = self.incoming.get(timeout=min(0.1, remain))
                    except queue.Empty:
                        continue
                    if isinstance(line, Exception):
                        raise SageError("RUFLO_UNAVAILABLE", "Ruflo stdio closed or exceeded its frame limit.")
                    try:
                        msg = json.loads(line)
                    except ValueError:
                        raise SageError("RUFLO_EVIDENCE", "Ruflo returned a non-JSON frame.") from None
                    if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0":
                        raise SageError("RUFLO_EVIDENCE", "Invalid RPC envelope.")
                    if "id" not in msg:
                        continue
                    if type(msg["id"]) is not int or msg["id"] != reqid or "method" in msg or "error" in msg or "result" not in msg:
                        raise SageError("RUFLO_EVIDENCE", "Unexpected or errored RPC response.")
                    return msg["result"]
        self.session = Session(argv, self.volume, minimal_environment(), self.timeout)
        self.session.incoming = queue.Queue(maxsize=32)
        try:
            self.session.__enter__()
            available = {row["name"] for row in self.session.tools()}
            if not TOOLS.issubset(available):
                raise SageError("RUFLO_UNAVAILABLE", "The pinned runtime lacks required task lifecycle tools.")
            actual = self._control(["inspect", self.name, "--format", "{{json .}}"])
            info = json.loads(actual["stdout"])
            host = info["HostConfig"]
            if (actual["exit_code"] != 0 or info["Image"] != self.configuration["image_id"]
                    or host["NetworkMode"] != "none" or not host["ReadonlyRootfs"]
                    or host["CapDrop"] != ["ALL"] or info["Config"]["User"] != self.user
                    or len(info["Mounts"]) != 1 or info["Mounts"][0]["Destination"] != "/workspace"):
                raise SageError("RUFLO_ISOLATION", "Actual container isolation did not match the requested policy.")
            self.inventory_hash = digest(sorted(available))
            self.contract_hash = self.client.validate_run_contract(str(self.contract), grant)
            return self
        except BaseException as exc:
            self.__exit__(None, None, None)
            if isinstance(exc, self.client.BoundaryError):
                raise SageError("RUFLO_UNAVAILABLE", "Ruflo could not establish the required bounded MCP task session.") from None
            raise

    def call(self, tool, arguments):
        if tool not in TOOLS:
            raise SageError("RUFLO_AUTHORITY", "This binding only permits metadata task lifecycle tools.")
        try:
            grant = self.client.approval_for(str(self.approval), self.volume, tool)
            self.client.validate_run_contract(str(self.contract), grant)
            result = self.session.call(tool, arguments)
        except self.client.BoundaryError:
            raise SageError("RUFLO_AUTHORITY", "A Ruflo call failed its native SAGE grant/contract or protocol check.") from None
        value = _tool_value(self.client, result)
        self.calls.append({"tool": tool, "arguments_sha256": digest(arguments), "response_sha256": digest(result)})
        return value

    def persisted(self, task_id):
        path = reject_links(self.volume / ".claude-flow/tasks/store.json")
        try:
            value = json.loads(_read_regular(path, 2097152))["tasks"][task_id]
        except (ValueError, KeyError, TypeError):
            raise SageError("RUFLO_EVIDENCE", "Task lifecycle was not independently persisted by Ruflo.") from None
        return value

    def reconcile(self):
        """The caller holds SAGE's run lock; no previous worker may own a job.

        Cancel only our own unfinished metadata after a failed/interrupted call.
        Never reinterpret an old queue completion as new product acceptance.
        """
        path = reject_links(self.volume / ".claude-flow/tasks/store.json")
        if not path.exists():
            return
        try:
            tasks = json.loads(_read_regular(path, 2097152))["tasks"]
            if not isinstance(tasks, dict) or len(tasks) > 64:
                raise ValueError()
        except (ValueError, KeyError, TypeError):
            raise SageError("RUFLO_INTEGRITY", "Unbounded or invalid persisted task store.") from None
        prefix = "SAGE structured model job " + self.run_id + " "
        for task_id, record in tasks.items():
            if (isinstance(record, dict) and str(record.get("description", "")).startswith(prefix)
                    and record.get("status") in ("pending", "in_progress")):
                self.call("task_cancel", {"taskId": task_id, "reason": "SAGE resumed after interrupted or failed worker"})
                if self.call("task_status", {"taskId": task_id}).get("status") != "cancelled":
                    raise SageError("RUFLO_EVIDENCE", "The interrupted task could not be reconciled.")

    def __exit__(self, *_):
        try:
            if self.session:
                self.session.__exit__(None, None, None)
        finally:
            # Exact generated name AND nonce; never remove an unrelated container.
            check = self._control(["inspect", self.name, "--format", '{{index .Config.Labels "sage.ruflo.nonce"}}'], 5)
            if check["exit_code"] == 0 and check["stdout"].strip() == self.nonce:
                self._control(["rm", "--force", self.name], 5)


class RufloProvider:
    """A real task must be assigned before the actual model worker may run."""
    def __init__(self, provider, kit_root, configuration, run_id, approval_id, session_factory=DockerCoordinator):
        self.provider, self.kit_root = provider, Path(kit_root)
        self.configuration = binding(configuration)
        self.run_id, self.approval_id = run_id, approval_id
        self.session_factory, self.cancel_check = session_factory, None

    def generate(self, stage, prompt, schema, workspace, timeout_seconds):
        if stage not in STAGES:
            raise SageError("RUFLO_AUTHORITY", "Unknown worker role; no task was dispatched.")
        if self.cancel_check and self.cancel_check():
            raise SageError("CANCELLED", "Cancelled before any coordinator or model worker starts.")
        deadline = time.monotonic() + timeout_seconds
        self.provider.cancel_check = self.cancel_check
        with self.session_factory(self.kit_root, self.configuration, self.run_id, self.approval_id,
                                  timeout_seconds, self.cancel_check) as session:
            session.reconcile()
            worker = "sage-codex-" + self.run_id + "-" + stage
            description = "SAGE structured model job " + self.run_id + " " + stage + " " + uuid.uuid4().hex
            task = session.call("task_create", {"type": "research" if stage == "planner" else "feature",
                                               "description": description, "priority": "normal", "tags": ["sage-controlled", stage]})
            task_id = task.get("taskId")
            if (not isinstance(task_id, str) or not re.fullmatch(r"task-[A-Za-z0-9-]{3,100}", task_id)
                    or task.get("status") != "pending" or task.get("description") != description):
                raise SageError("RUFLO_EVIDENCE", "Ruflo did not create the expected pending task.")
            try:
                assigned = session.call("task_assign", {"taskId": task_id, "agentIds": [worker]})
                active = session.call("task_status", {"taskId": task_id})
                if (assigned.get("taskId") != task_id or active.get("taskId") != task_id
                        or active.get("status") != "in_progress" or active.get("assignedTo") != [worker]
                        or active.get("description") != description):
                    raise SageError("RUFLO_EVIDENCE", "Task assignment was not confirmed; model execution is denied.")
                if self.cancel_check and self.cancel_check():
                    raise SageError("CANCELLED", "Cancelled before the assigned worker starts.")
                remaining = deadline - time.monotonic() - 5
                if remaining <= 0:
                    raise SageError("RUFLO_UNAVAILABLE", "No model budget time remains after coordination.")
                result = self.provider.generate(stage, prompt, schema, workspace, remaining)
                validate(result.payload, schema)
                if (result.receipt.get("provider") != "codex-cli" or result.receipt.get("status") != "COMPLETED"
                        or result.receipt.get("invocations") != 1 or result.receipt.get("tools_executed") != 0):
                    raise SageError("RUFLO_EVIDENCE", "This binding requires the bounded actual Codex worker receipt.")
                if self.cancel_check and self.cancel_check():
                    raise SageError("CANCELLED", "Cancelled before publishing the model response receipt.")
                result_data = {"result_kind": "MODEL_RESPONSE_VALIDATED_NOT_PRODUCT_ACCEPTANCE",
                               "worker_id": worker, "payload_sha256": digest(result.payload),
                               "model_provider": "codex-cli", "product_acceptance": False}
                session.call("task_complete", {"taskId": task_id, "result": result_data})
                finished = session.call("task_status", {"taskId": task_id})
                persisted = session.persisted(task_id)
                for observed in (finished, persisted):
                    if (observed.get("taskId") != task_id or observed.get("status") != "completed"
                            or observed.get("result") != result_data or observed.get("assignedTo") != [worker]):
                        raise SageError("RUFLO_EVIDENCE", "Ruflo completion/readback did not match the actual model result.")
                receipt = dict(result.receipt, coordination={
                    "engine": "ruflo", "version": "3.61.1", "execution_mode": "SAGE_CODEX_EXTERNAL_WORKER",
                    "native_ruflo_llm_executed": False, "task_id": task_id, "worker_id": worker,
                    "status": "completed", "payload_sha256": result_data["payload_sha256"],
                    "binding_sha256": digest(self.configuration), "contract_sha256": session.contract_hash,
                    "image_id": self.configuration["image_id"], "sandbox": "docker-network-none-metadata-only",
                    "protocol_version": session.session.version, "inventory_sha256": session.inventory_hash,
                    "independent_persisted_readback": True, "calls": session.calls,
                    "product_acceptance": False})
                return ModelResult(result.payload, receipt)
            except BaseException:
                try:
                    session.call("task_cancel", {"taskId": task_id, "reason": "SAGE worker stopped; no product acceptance"})
                except Exception:
                    pass
                raise


def probe(kit_root, configuration, approval_id):
    """Real isolated handshake, no task execution and no model call."""
    with DockerCoordinator(kit_root, configuration, uuid.uuid4().hex, approval_id, 45) as session:
        return {"status": "CONNECTED_MODEL_NOT_TESTED", "model_invocations": 0,
                "execution_mode": "SAGE_CODEX_EXTERNAL_WORKER", "native_ruflo_llm_executed": False,
                "upstream_version": "3.61.1", "protocol_version": session.session.version,
                "required_tools_present": sorted(TOOLS), "inventory_sha256": session.inventory_hash,
                "image_id": configuration["image_id"], "sandbox": "docker-network-none-metadata-only"}
