"""JSON-first CLI. Live work is opt-in; no subprocesses originate here."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

from . import __version__


class UsageError(Exception):
    pass


class Parser(argparse.ArgumentParser):
    def error(self, message):
        # argparse may echo arbitrary values (including an accidental secret).
        raise UsageError("Invalid arguments; use 'sage --help' or 'sage COMMAND --help'.")


def default_kit_root() -> Path:
    """Prefer this source checkout, otherwise the wheel's attributed closure."""
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        if ((ancestor / "extensions/ecc/catalog.json").is_file()
                and (ancestor / "SAGE_v0.8_EXECUTION_PROTOCOL_AND_SKILL_CONTRACT.md").is_file()):
            return ancestor
    return here.parent / "_kit"


def default_state_root() -> Path:
    local = os.environ.get("LOCALAPPDATA") if os.name == "nt" else None
    if local:
        return Path(local) / "SAGE/autonomous/runs"
    return Path.home() / ".local/state/sage/autonomous/runs"


def make_parser() -> Parser:
    parser = Parser(prog="sage", description="SAGE bounded autonomous runtime; live execution requires explicit authorization.")
    parser.add_argument("--version", action="version", version="sage-runtime " + __version__)

    def locations(target, *, nested=False):
        default = argparse.SUPPRESS if nested else None
        target.add_argument("--kit-root", type=Path, default=default, help="Explicit trusted SAGE kit resource root")
        target.add_argument("--state-root", type=Path, default=default, help="Private run evidence root outside generated projects")
        target.add_argument("--json", action="store_true", default=argparse.SUPPRESS, help="Emit JSON (the default)")

    locations(parser)
    sub = parser.add_subparsers(dest="command", required=True, parser_class=Parser)

    def command(name, help_text):
        child = sub.add_parser(name, help=help_text)
        locations(child, nested=True)
        return child

    command("doctor", "Inspect local provider and kit readiness; no model call")
    build = command("build", "Create a durable bounded build; default does not invoke a model")
    build.add_argument("idea", help="Your software idea/requirements (not a shell command)")
    build.add_argument("--output", type=Path, required=True, help="Absolute path for a NEW generated project")
    build.add_argument("--source", type=Path, default=None, help="Existing local source snapshot; original remains unchanged, fixes go to NEW output")
    build.add_argument("--approval-id", default=None, help="Task-specific execution authorization record")
    build.add_argument("--live", action="store_true", help="Invoke the authorized provider and native sandbox checks")
    build.add_argument("--auto-approve-plan", action="store_true", help="Preauthorize only a low-risk R1 local plan; no external actions")
    build.add_argument("--max-model-calls", type=int, default=12)
    build.add_argument("--max-repairs", type=int, default=2)
    build.add_argument("--max-seconds", type=int, default=900)
    build.add_argument("--profile", choices=("python-stdlib", "node-stdlib", "static-web"))
    build.add_argument("--pause-after", type=str.upper, choices=("PLAN", "IMPLEMENT", "VERIFY"), help="Pause after a durable stage for stop/resume")
    for name, help_text in (
        ("resume", "Resume the same durable run and remaining budget"),
        ("status", "Read durable run state and evidence"),
        ("approve", "Approve exactly the displayed plan hash"),
        ("clarify", "Record an answer for an intake clarification"),
        ("cancel", "Cancel a run without deleting generated source or evidence"),
    ):
        child = command(name, help_text)
        child.add_argument("run_id")
        if name == "resume":
            child.add_argument("--live", action="store_true")
            child.add_argument("--pause-after", type=str.upper, choices=("PLAN", "IMPLEMENT", "VERIFY"))
        elif name == "approve":
            child.add_argument("--plan-hash", required=True)
        elif name == "clarify":
            child.add_argument("--answer", required=True)
    return parser


def dispatch(args: argparse.Namespace) -> dict:
    from .safety import SageError

    kit_root = (args.kit_root or default_kit_root()).absolute()
    state_root = (args.state_root or default_state_root()).absolute()
    if args.command == "build":
        if args.live and (not args.approval_id or not args.approval_id.strip()):
            raise SageError("APPROVAL_REQUIRED", "Live build needs a task-specific --approval-id.")
        if args.auto_approve_plan and not args.live:
            raise SageError("LIVE_REQUIRED", "--auto-approve-plan is meaningful only for an explicitly authorized --live run.")
    if args.command == "doctor":
        from .providers import CodexProvider

        readiness = CodexProvider().doctor()
        available = ((kit_root / "extensions/ecc/catalog.json").is_file()
                     and (kit_root / "SAGE_v0.8_EXECUTION_PROTOCOL_AND_SKILL_CONTRACT.md").is_file())
        return {"status": "READY" if available and readiness.get("ready") else "BLOCKED",
                "runtime_version": __version__, "kit_root": str(kit_root),
                "kit_available": available, "state_root": str(state_root),
                "provider": readiness, "model_invocations": 0,
                "sandbox_readiness": "NOT_PROBED", "live_acceptance": "NOT_RUN",
                "limits": ["Only provider and kit presence were inspected; the actual check sandbox was not probed.",
                           "Readiness does not prove a live build or sandbox check."]}
    from .engine import Engine

    engine = Engine(kit_root, state_root)
    if args.command == "build":
        options = {"live": args.live, "auto_approve_plan": args.auto_approve_plan,
                   "max_model_calls": args.max_model_calls, "max_repairs": args.max_repairs,
                   "max_seconds": args.max_seconds, "profile": args.profile}
        if args.source is not None:
            options["source"] = args.source
        state = engine.create(args.idea, args.output, args.approval_id, **options)
        return engine.run(state["run_id"], live=True, pause_after=args.pause_after) if args.live else state
    if args.command == "resume":
        return engine.run(args.run_id, live=args.live, pause_after=args.pause_after)
    if args.command == "approve":
        return engine.approve(args.run_id, args.plan_hash)
    if args.command == "clarify":
        return engine.clarify(args.run_id, args.answer)
    if args.command == "cancel":
        return engine.cancel(args.run_id)
    return engine.status(args.run_id)


def result_exit_code(result: dict) -> int:
    status = str(result.get("status", result.get("state", ""))).upper()
    if status.startswith("BLOCKED") or status in {
        "NEEDS_AUTHORIZATION", "NEEDS_CLARIFICATION", "AWAITING_PLAN_APPROVAL", "WAITING_APPROVAL", "ESCALATED",
        "BUDGET_EXHAUSTED", "FAILED", "CANCELLED", "CANCEL_REQUESTED", "PAUSED",
    }:
        return 2
    return 0


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        args = make_parser().parse_args(argv)
        result = dispatch(args)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return result_exit_code(result)
    except UsageError as exc:
        result = {"status": "ERROR", "error": {"code": "INVALID_ARGUMENT", "message": str(exc)}}
    except Exception as exc:
        from .safety import SageError

        if isinstance(exc, SageError):
            result = {"status": "ERROR", "error": {"code": exc.code, "message": str(exc)}}
        else:
            result = {"status": "ERROR", "error": {"code": "INTERNAL_ERROR", "message": "The runtime could not complete this request; no success is claimed."}}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 1
