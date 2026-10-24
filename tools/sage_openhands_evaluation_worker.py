"""Issue #4 evaluation transport, never registered as a production SAGE engine.

Exactly one real SDK LLM response per SAGE worker job. No SDK shell/file tools,
hooks, skills, memory, fallback, retries or independent acceptance authority.
SAGE's existing provider contract cannot silently become an unmetered agent loop.
"""
from __future__ import annotations
import base64
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime/autonomous/src"))
from sage_runtime.process import minimal_environment, run_bounded
from sage_runtime.providers import ModelResult
from sage_runtime.safety import SageError, reject_links, _read_regular, _reject_credentials
from sage_runtime.schemas import validate

APPROVAL = "SAGE-OHSDK-20261024-APPROVED"
MODEL = "gpt-6.1-sol"
SENTINEL = "SAGE_OPENHANDS_RESULT:"
PHASE = "input"


def subscription_grant():
    """Read only the existing account's short-lived access credential.

    Never copy/cache/refresh the native login or delegate its refresh token.
    The SDK receives this credential in memory, not in source, argv or tool data.
    """
    folder = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    path = reject_links(folder / "auth.json")
    data = json.loads(_read_regular(path, 262144))
    token = (data.get("tokens") or {}).get("access_token")
    if data.get("auth_mode") not in (None, "chatgpt") or not isinstance(token, str):
        raise SageError("SDK_AUTH_REQUIRED", "An existing subscription access credential is required; API keys are not allowed.")
    try:
        claims = json.loads(base64.urlsafe_b64decode(token.split(".")[1] + "==="))
        expiry = int(claims["exp"])
    except (ValueError, IndexError, KeyError):
        raise SageError("SDK_AUTH_REQUIRED", "Cannot bound the existing subscription credential lifetime.") from None
    if expiry - time.time() < 1200:
        raise SageError("SDK_AUTH_REQUIRED", "Subscription credential must remain valid for this bounded experiment.")
    return path, hashlib.sha256(path.read_bytes()).hexdigest(), {"access": token, "expiry_ms": expiry * 1000}


class EvaluationProvider:
    def __init__(self, codex_budget, executable, auth_root, folder, allowed):
        if executable is None or auth_root is None:
            raise SageError("SDK_CONFIG", "Explicit isolated SDK Python and private persistence root are required.")
        self.codex_budget, self.executable = codex_budget, reject_links(Path(executable).absolute())
        self.auth_root, self.folder = reject_links(Path(auth_root).absolute()), Path(folder)
        if self.auth_root.resolve() != (self.folder.parent / "private").resolve():
            raise SageError("SDK_CONFIG", "Use only this evaluation's separate private persistence directory.")
        self.cancel_check = None

    def generate(self, stage, prompt, schema, workspace, timeout_seconds):
        if stage not in ("implementer", "repairer"):
            self.codex_budget.cancel_check = self.cancel_check
            return self.codex_budget.generate(stage, prompt, schema, workspace, timeout_seconds)
        if self.cancel_check and self.cancel_check():
            raise SageError("CANCELLED", "Cancelled before SDK bootstrap.")
        self.codex_budget.reserve("openhands-" + stage)
        reservation = json.loads(self.codex_budget.path.read_text())["reserved_calls"]
        native, checksum, credential = subscription_grant()
        with tempfile.TemporaryDirectory(prefix="sage-sdk-response-") as temporary:
            job = Path(temporary)
            packet = {"approval": APPROVAL, "model": MODEL, "stage": stage,
                      "prompt": prompt, "schema": schema, "credential": credential,
                      "budget_root": str(self.folder), "reservation": reservation,
                      "cwd": str(job), "timeout": min(timeout_seconds, 300)}
            env = minimal_environment()
            env.update(OH_PERSISTENCE_DIR=str(self.auth_root), OTEL_SDK_DISABLED="true",
                       DO_NOT_TRACK="1", OPENHANDS_SUPPRESS_BANNER="1", LITELLM_LOCAL_MODEL_COST_MAP="True",
                       LOG_LEVEL="ERROR", LOG_DIR=str(job / "logs"), LMNR_LOG_LEVEL="ERROR",
                       USERPROFILE=str(job), HOME=str(job), APPDATA=str(job / "appdata"),
                       LOCALAPPDATA=str(job / "localappdata"))
            process = run_bounded([str(self.executable), "-B", str(Path(__file__).resolve()), "--sdk-worker"],
                                  cwd=job, env=env, input_text=json.dumps(packet),
                                  timeout_seconds=min(timeout_seconds, 300), max_output_bytes=1048576,
                                  cancel_check=self.cancel_check)
            # Neither the SDK nor a generated tool gets the native refresh token.
            if hashlib.sha256(native.read_bytes()).hexdigest() != checksum:
                raise SageError("SDK_AUTH_INTEGRITY", "The native login changed during a serialized SDK experiment.")
            if process["cancelled"]:
                error = SageError("CANCELLED", "The owned SDK process was cancelled.")
                error.safe_receipt = {"provider": "openhands-sdk", "status": "CANCELLED", "cancelled": True}
                raise error
            if process["timed_out"] or process["cancelled"] or process["exit_code"] != 0 or process["output_truncated"]:
                import re
                details, safe_failure = "", {}
                for line in process["stdout"].splitlines():
                    if line.startswith(SENTINEL):
                        try:
                            failure = json.loads(line[len(SENTINEL):])
                            text = str(failure.get("phase", "")) + "/" + str(failure.get("error_type", ""))
                            if re.fullmatch(r"[A-Za-z_]{1,60}/[A-Za-z_]{1,60}", text):
                                details = " (" + text + ")"
                            safe_failure = {k: failure[k] for k in ("phase", "error_type", "conversation_status", "sdk_model_jobs", "event_shapes", "sdk_errors") if k in failure}
                        except ValueError:
                            pass
                error = SageError("PROVIDER_FAILED", "The isolated SDK response failed or exceeded its deadline" + details + "; no fallback.")
                error.safe_receipt = dict(safe_failure, provider="openhands-sdk", status="FAILED",
                                          duration_seconds=process["duration_seconds"],
                                          timed_out=process["timed_out"], cancelled=process["cancelled"],
                                          logs_included=False, paid_api_access=False)
                raise error
            lines = [line[len(SENTINEL):] for line in process["stdout"].splitlines() if line.startswith(SENTINEL)]
            if len(lines) != 1:
                raise SageError("SDK_EVIDENCE", "No unique actual SDK completion receipt.")
            result = json.loads(lines[0])
            fields = {"status", "conversation_status", "sdk_model_jobs", "payload", "model", "endpoint_class", "usage",
                      "sdk_estimated_cost_not_billing", "actual_monetary_cost", "event_shapes", "persistence_readback",
                      "credential_not_in_persistence", "product_acceptance", "finish_tool_is_not_product_done", "response_format"}
            if set(result) != fields or result.get("product_acceptance") is not False:
                raise SageError("SDK_EVIDENCE", "Unrecognized or synthetic SDK completion receipt.")
            _reject_credentials(json.dumps(result, ensure_ascii=True))
            if (result.get("status") != "COMPLETED" or result.get("sdk_model_jobs") != 1
                    or result.get("conversation_status") != "finished"):
                raise SageError("SDK_EVIDENCE", "The SDK did not finish exactly one bounded model response.")
            payload = result.pop("payload")
            validate(payload, schema)
            # The unchanged SAGE Engine applies its approved plan/path checks.
            # Do not introduce a competing SDK permission or routing system.
            result.update(provider="openhands-sdk", stage=stage, version="1.58.1", invocations=1,
                          tools_executed=1 if result["response_format"] == "sdk_finish_schema" else 0,
                          native_mutating_tools_executed=0,
                          sdk_finish_schema_tool_executed=1 if result["response_format"] == "sdk_finish_schema" else 0,
                          duration_seconds=process["duration_seconds"],
                          native_login_unchanged=True, credential_cached=False,
                          credential_transport="MEMORY_ONLY_NO_REFRESH_TOKEN", paid_api_access=False,
                          prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest())
            return ModelResult(payload, result)


def sdk_worker():
    global PHASE
    packet = json.loads(sys.stdin.read(4194304))
    if (packet.get("approval") != APPROVAL or packet.get("model") != MODEL
            or packet.get("stage") not in ("implementer", "repairer")):
        raise RuntimeError("Invalid evaluation grant")
    PHASE = "sdk_import"
    import importlib.metadata
    if importlib.metadata.version("openhands-sdk") != "1.58.1":
        raise RuntimeError("SDK version mismatch")
    from openhands.sdk import Agent, Conversation, LLM, Tool
    from openhands.sdk.context import AgentContext
    from openhands.sdk.llm.auth.credentials import CredentialStore, OAuthCredentials
    from openhands.sdk.llm.auth.openai import OpenAISubscriptionAuth
    from openhands.sdk.tool.builtins.finish import FinishTool
    from openhands.sdk.tool.registry import register_tool
    from openhands.sdk.event import ActionEvent, MessageEvent
    spec = __import__("importlib.util", fromlist=["util"]).spec_from_file_location(
        "sage_sdk_existing_budget", ROOT / "tools/Run-SageAutonomousLive.py")
    live = __import__("importlib.util", fromlist=["util"]).module_from_spec(spec)
    spec.loader.exec_module(live)
    budget = live.DeliveryBudget(None, Path(packet["budget_root"]), limit=30)
    calls, output, shapes, errors, formats = [], [], [], [], []
    # Agent 1.58.1 calls generate/agenerate, which route to Responses or Chat
    # Completions. Meter that public boundary, not just the older Chat API.
    original, original_async = LLM.generate, LLM.agenerate
    def reserve():
        if calls:
            raise RuntimeError("One response per existing SAGE worker job; no hidden SDK iteration")
        if packet.get("probe_only") is True:
            raise RuntimeError("Preflight does not authorize a model request")
        stored = json.loads(budget.path.read_text())
        index = packet.get("reservation")
        if (type(index) is not int or not 1 <= index <= stored["reserved_calls"]
                or stored["stages"][index-1] != {"stage": "openhands-" + packet["stage"], "attempt": index}):
            raise RuntimeError("Missing parent-owned SAGE model-job reservation")
        calls.append({"reserved": True})
    def metered(self, *args, **kwargs):
        reserve()
        kwargs["tool_choice"] = "required"
        return original(self, *args, **kwargs)
    async def ametered(self, *args, **kwargs):
        reserve()
        kwargs["tool_choice"] = "required"
        return await original_async(self, *args, **kwargs)
    LLM.generate, LLM.agenerate = metered, ametered
    PHASE = "subscription_configuration"
    credential = OAuthCredentials(vendor="openai", access_token=packet["credential"]["access"],
                                  refresh_token="", expires_at=packet["credential"]["expiry_ms"])
    auth = OpenAISubscriptionAuth(CredentialStore(Path(os.environ["OH_PERSISTENCE_DIR"]) / "unused-auth-cache"))
    llm = auth.create_llm(model=MODEL, credentials=credential, num_retries=0, timeout=90, caching_prompt=False)
    if str(llm.base_url).rstrip("/") != "https://chatgpt.com/backend-api/codex":
        raise RuntimeError("Unexpected subscription endpoint")
    wrapper_schema = {"type": "object", "properties": {"result": packet["schema"]},
                      "required": ["result"], "additionalProperties": False}
    finish = FinishTool.create()[0].set_response_schema(wrapper_schema)
    register_tool("SageStructuredFinish", finish)
    context = AgentContext(**{k: False for k in AgentContext.model_fields if k.startswith("load_")})
    PHASE = "agent_configuration"
    agent = Agent(llm=llm, tools=[Tool(name="SageStructuredFinish")], include_default_tools=[],
                  agent_context=context, condenser=None, critic=None, mcp_config={}, tool_concurrency_limit=1)
    def observe(event):
        shapes.append(type(event).__name__)
        if isinstance(event, ActionEvent) and event.action is not None and event.tool_name == finish.name:
            structured = getattr(event.action, "structured_output", None)
            if structured is None:
                # The persisted SDK Event keeps raw tool arguments but excludes
                # the Action's private structured-output cache.
                structured = json.loads(event.tool_call.function.arguments)
            if "result" in structured:
                validate(structured["result"], packet["schema"])
                output.append(structured["result"])
                formats.append("sdk_finish_schema")
        if isinstance(event, MessageEvent) and event.source == "agent":
            text = "".join(getattr(part, "text", "") for part in event.llm_message.content).strip()
            if text.startswith("```json\n") and text.endswith("\n```"):
                text = text[8:-4]
            try:
                candidate = json.loads(text)
                if isinstance(candidate, dict) and set(candidate) == {"result"}:
                    candidate = candidate["result"]
                validate(candidate, packet["schema"])
                if not output:
                    output.append(candidate)
                    formats.append("assistant_json")
            except (ValueError, SageError):
                pass
        if type(event).__name__ == "ConversationErrorEvent":
            classification = getattr(event, "classification", None)
            errors.append({"code": str(getattr(event, "code", ""))[:80],
                           "classification": classification.model_dump(mode="json") if classification else None})
    private = Path(packet["cwd"]) / "conversation-state"
    PHASE = "conversation_configuration"
    conversation = Conversation(agent=agent, workspace=packet["cwd"], persistence_dir=private,
                                callbacks=[observe], plugins=[], max_iteration_per_run=1,
                                visualizer=None, delete_on_close=False)
    if packet.get("probe_only") is True:
        conversation.pause()
        paused = conversation.state.execution_status.value == "paused"
        identifier = conversation.id
        conversation.close()
        reopened = Conversation(agent=agent, workspace=packet["cwd"], persistence_dir=private,
                                conversation_id=identifier, plugins=[], max_iteration_per_run=1,
                                visualizer=None, delete_on_close=False)
        restored = reopened.state.execution_status.value == "paused"
        reopened.close()
        print(SENTINEL + json.dumps({"status": "PROBE_ONLY_NO_MODEL", "model_jobs": len(calls),
              "pause": paused, "persistence_restore": restored, "sdk": "1.58.1",
              "subscription_configured": llm.is_subscription,
              "native_mutating_tools_enabled": False}), flush=True)
        return
    conversation.send_message(packet["prompt"] + "\nProvide complete file contents using the finish tool's result object. You have no shell or file tools. Never claim tests ran.")
    PHASE = "model_response"
    conversation.run()
    PHASE = "completion_readback"
    status = conversation.state.execution_status.value
    metrics = llm.metrics.model_dump(mode="json") if llm.metrics else {}
    if len(output) != 1 or len(calls) != 1 or status != "finished":
        conversation.close()
        print(SENTINEL + json.dumps({"status": "BLOCKED", "phase": PHASE, "error_type": "RuntimeError",
              "conversation_status": status, "sdk_model_jobs": len(calls),
              "event_shapes": shapes, "sdk_errors": errors}), flush=True)
        sys.exit(1)
    validate(output[0], packet["schema"])
    conversation_id = conversation.id
    conversation.close()
    # Real fresh Conversation readback, no rerun/model call.
    restored = Conversation(agent=agent, workspace=packet["cwd"], persistence_dir=private,
                            conversation_id=conversation_id, plugins=[], max_iteration_per_run=1,
                            visualizer=None, delete_on_close=False)
    persisted = restored.state.execution_status.value == status
    restored.close()
    token = packet["credential"]["access"].encode()
    no_credential_persistence = all(token not in p.read_bytes() for p in private.rglob("*") if p.is_file())
    if not no_credential_persistence:
        raise RuntimeError("Credential persisted unexpectedly")
    result = {"status": "COMPLETED", "conversation_status": status, "sdk_model_jobs": len(calls),
              "payload": output[0], "model": MODEL, "endpoint_class": "CHATGPT_SUBSCRIPTION",
              "usage": metrics.get("accumulated_token_usage"),
              "sdk_estimated_cost_not_billing": metrics.get("accumulated_cost"),
              "actual_monetary_cost": None, "event_shapes": shapes,
              "response_format": formats[0],
              "persistence_readback": persisted, "credential_not_in_persistence": no_credential_persistence,
              "product_acceptance": False, "finish_tool_is_not_product_done": True}
    print(SENTINEL + json.dumps(result, ensure_ascii=True), flush=True)


if __name__ == "__main__":
    try:
        if sys.argv[1:] != ["--sdk-worker"]:
            raise RuntimeError("Only an explicitly granted controller worker can call this helper")
        sdk_worker()
    except Exception as exc:
        # Authentication exceptions can contain headers; never print their text.
        import traceback
        trace = [{"file": Path(f.filename).name, "line": f.lineno} for f in traceback.extract_tb(exc.__traceback__)[-8:]]
        # Before importing SDK auth, no credential has reached any SDK code.
        diagnostic = str(exc)[:240] if PHASE == "sdk_import" else None
        print(SENTINEL + json.dumps({"status": "BLOCKED", "error_type": type(exc).__name__, "phase": PHASE,
                                   "import_diagnostic": diagnostic, "frames": trace}), flush=True)
        sys.exit(1)
