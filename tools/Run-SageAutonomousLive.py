#!/usr/bin/env python3
"""Explicit opt-in, max-12-call live acceptance on newly owned temporary projects.

Not run by CI. Never downloads images, copies auth, deploys, commits or pushes.
The root-approved 2026-10-24 scope authorizes these bounded representative jobs.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime/autonomous/src"))

from sage_runtime.engine import Engine
from sage_runtime.providers import CodexProvider, SandboxRunner
from sage_runtime.safety import SageError, Policy, project_manifest, write_project_files
from sage_runtime.ruflo import load_binding, DockerCoordinator


@contextmanager
def budget_lock(folder):
    """The delivery cap is shared across processes and released by the OS."""
    descriptor = os.open(folder / "delivery-budget.lock", os.O_RDWR | os.O_CREAT, 0o600)
    stream = os.fdopen(descriptor, "r+b", buffering=0)
    try:
        if not stream.read(1):
            stream.write(b"0")
        stream.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise SageError("BUDGET_LOCKED", "Another acceptance process owns the shared budget.") from None
        yield
    finally:
        stream.close()


def save_budget(path, value):
    temporary = path.with_suffix(".new")
    with temporary.open("wb") as stream:
        stream.write(json.dumps(value, indent=2).encode("utf-8"))
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


class DeliveryBudget:
    def __init__(self, provider, folder):
        self.provider = provider
        self.path = folder / "live-budget.json"
        self.cancel_check = None
        with budget_lock(folder):
            if not self.path.exists():
                if (folder / "runs").exists() or any(folder.glob("*-run.json")):
                    raise SageError("DELIVERY_BUDGET", "Previous runs exist but their shared budget is missing; no reset.")
                save_budget(self.path, {"limit": 12, "reserved_calls": 0, "stages": []})

    def generate(self, stage, prompt, schema, workspace, timeout_seconds):
        with budget_lock(self.path.parent):
            if self.path.is_symlink() or self.path.stat().st_size > 65536:
                raise SageError("DELIVERY_BUDGET", "Budget state is invalid.")
            budget = json.loads(self.path.read_text(encoding="utf-8"))
            count = budget.get("reserved_calls")
            if budget.get("limit") != 12 or type(count) is not int or not 0 <= count <= 12 or len(budget.get("stages", [])) != count:
                raise SageError("DELIVERY_BUDGET", "Budget state is invalid; no automatic reset.")
            if count >= 12:
                raise SageError("DELIVERY_BUDGET", "The approved twelve-call live acceptance budget is exhausted.")
            budget["reserved_calls"] += 1
            budget["stages"].append({"stage": stage, "attempt": budget["reserved_calls"]})
            save_budget(self.path, budget)  # Charge durably before the provider.
        self.provider.cancel_check = self.cancel_check
        return self.provider.generate(stage, prompt, schema, workspace, timeout_seconds)


class OracleRunner:
    def __init__(self, runner, oracle):
        self.runner, self.oracle = runner, oracle
        self.cancel_check = None
        self.receipts = []

    def run(self, profile, workspace, timeout_seconds):
        self.runner.cancel_check = self.cancel_check
        receipt = self.runner.run(profile, workspace, timeout_seconds / 2)
        if receipt["status"] != "PASS":
            self.receipts.append(receipt)
            return receipt
        # Independent test code is controller-owned and absent from model output.
        # It runs against a fresh exact source copy in the SAME hardened sandbox.
        folder = Path(tempfile.mkdtemp(prefix="sage-independent-oracle-")).resolve()
        project = folder / "project"
        project.mkdir()
        files = [{"path": item["path"], "content": (workspace / item["path"]).read_text(encoding="utf-8")}
                 for item in project_manifest(workspace)]
        oracle_path = ("tests/" if any(item["path"].startswith("tests/") for item in files) else "") + "test_sage_acceptance_oracle.py"
        if any(item["path"] == oracle_path for item in files):
            raise SageError("ACCEPTANCE_ORACLE", "Generated source cannot replace the independent oracle path.")
        files.append({"path": oracle_path, "content": self.oracle})
        write_project_files(project, files, Policy())
        oracle_receipt = self.runner.run(profile, project, timeout_seconds / 2)
        combined = dict(oracle_receipt, project_check=receipt,
                        independent_oracle_sha256=hashlib.sha256(self.oracle.encode()).hexdigest(),
                        independent_oracle_path=oracle_path,
                        oracle_source_snapshot=project_manifest(workspace))
        self.receipts.append(combined)
        return combined


def assert_independent_acceptance(state, oracle):
    """A resumed terminal run cannot borrow a newly supplied oracle's name."""
    verification = state.get("verification") or {}
    project_check = verification.get("project_check") or {}
    actual = project_manifest(Path(state["workspace"]))
    bad_process = ("timed_out", "cancelled", "output_truncated", "launch_error", "unsandboxed_fallback")
    if (verification.get("status") != "PASS" or verification.get("exit_code") != 0
            or verification.get("independent_oracle_sha256") != hashlib.sha256(oracle.encode()).hexdigest()
            or verification.get("oracle_source_snapshot") != actual or state.get("manifest") != actual
            or project_check.get("status") != "PASS" or project_check.get("exit_code") != 0
            or any(verification.get(key) or project_check.get(key) for key in bad_process)
            or verification.get("sandbox") not in ("docker-isolated", "codex-native-restricted-read")
            or project_check.get("sandbox") != verification.get("sandbox")
            or (verification.get("summary") or {}).get("tests_run", 0)
               < (project_check.get("summary") or {}).get("tests_run", 0) + 2):
        raise SageError("ACCEPTANCE_ORACLE", "DONE lacks the expected independent oracle bound to this source.")


def assert_ruflo_acceptance(state):
    """Fresh actual MCP process + persisted records, not self-reported success."""
    configuration = state.get("coordinator")
    if not configuration:
        raise SageError("ACCEPTANCE_RUFLO", "This run did not use a Ruflo coordinator.")
    receipts = [item["receipt"] for item in state["receipts"] if item["stage"] != "verification"]
    if len(receipts) < 3 or any(not receipt.get("coordination") for receipt in receipts):
        raise SageError("ACCEPTANCE_RUFLO", "Every successful worker job must have an actual Ruflo assignment.")
    with DockerCoordinator(ROOT, configuration, state["run_id"], state["approval_id"], 45) as session:
        for receipt in receipts:
            coordination = receipt["coordination"]
            expected = {"result_kind": "MODEL_RESPONSE_VALIDATED_NOT_PRODUCT_ACCEPTANCE",
                        "worker_id": coordination["worker_id"], "payload_sha256": coordination["payload_sha256"],
                        "model_provider": "codex-cli", "product_acceptance": False}
            for record in (session.call("task_status", {"taskId": coordination["task_id"]}),
                           session.persisted(coordination["task_id"])):
                if (record.get("status") != "completed" or record.get("result") != expected
                        or record.get("assignedTo") != [coordination["worker_id"]]):
                    raise SageError("ACCEPTANCE_RUFLO", "Fresh Ruflo readback did not match model-worker receipts.")


SLUG_IDEA = """Build a tiny dependency-free Python library in slug.py with function
slugify(text: str)->str. Preserve Unicode letters/digits including Persian,
lowercase Latin, strip whitespace, turn whitespace and underscore into a single
hyphen, discard other punctuation, and collapse existing/repeated hyphens.
Empty or punctuation-only input returns ''. Raise TypeError for non-string.
Include root-level unittest tests and README.md. No CLI, server, database,
dependency, network, install or deployment. Use python-stdlib. All requirements
are specified: do not ask clarification questions. Keep plan/files small.
"""
SLUG_ORACLE = """import unittest
from slug import slugify
class IndependentSlugAcceptance(unittest.TestCase):
    def test_cases(self):
        for value, expected in [(' Hello World ', 'hello-world'), ('a___b', 'a-b'),
            ('Hello, World!', 'hello-world'), ('a---b', 'a-b'), ('', ''), ('!!!', ''),
            ('سلام دنیا', 'سلام-دنیا'), ('A  _ B', 'a-b')]:
            with self.subTest(value=value): self.assertEqual(slugify(value), expected)
    def test_invalid(self):
        with self.assertRaises(TypeError): slugify(None)
"""
DIVIDE_IDEA = """Fix the supplied dependency-free Python snapshot. calc.py exports
divide(a,b), which must return a/b, currently mistakenly returns a*b.
Preserve input files, retain the existing tests, add regression coverage and
document zero division as Python ZeroDivisionError. No dependencies, network,
server, install, or deployment. Use python-stdlib; root-level unittest tests.
No essential requirement is missing; keep the approved file plan small.
"""
DIVIDE_ORACLE = """import unittest
from calc import divide
class IndependentDivideAcceptance(unittest.TestCase):
    def test_values(self):
        for a,b,answer in [(6,3,2), (-9,3,-3), (1,4,.25), (0,2,0)]:
            self.assertEqual(divide(a,b), answer)
    def test_zero(self):
        with self.assertRaises(ZeroDivisionError): divide(1,0)
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--approval-id", required=True)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--docker-image", required=True)
    parser.add_argument("--ruflo-config", type=Path)
    parser.add_argument("--scenario", choices=("build", "repair", "all"), default="all")
    parser.add_argument("--resume-run")
    parser.add_argument("--restart-failed", action="store_true",
                        help="Start a new approved attempt only for a pre-source blocked run; shared budget is retained")
    parser.add_argument("--pause-after", choices=("PLAN", "IMPLEMENT", "VERIFY"))
    args = parser.parse_args()
    if not args.live:
        parser.error("--live is mandatory; this script invokes the approved account")
    if args.resume_run and args.scenario == "all":
        parser.error("--resume-run requires exactly one --scenario")
    if args.resume_run and args.restart_failed:
        parser.error("Explicit resume and restart are mutually exclusive")
    folder = args.evidence_root.resolve()
    if folder.is_relative_to(ROOT):
        parser.error("Acceptance evidence/projects must be outside the SAGE source checkout")
    folder.mkdir(parents=True, exist_ok=True)
    provider = DeliveryBudget(CodexProvider(), folder)
    configuration = load_binding(args.ruflo_config) if args.ruflo_config else None
    runner = SandboxRunner(docker_image=args.docker_image)
    results = []
    scenarios = ("build", "repair") if args.scenario == "all" else (args.scenario,)
    for scenario in scenarios:
        oracle = SLUG_ORACLE if scenario == "build" else DIVIDE_ORACLE
        checked_runner = OracleRunner(runner, oracle)
        engine = Engine(ROOT, folder / "runs", provider, checked_runner)
        run_pointer = folder / (scenario + "-run.json")
        restarting = False
        if args.restart_failed and run_pointer.is_file():
            previous_id = json.loads(run_pointer.read_text(encoding="utf-8"))["run_id"]
            previous = engine.store.load(previous_id)
            if previous["status"] != "BLOCKED" or previous["workspace_created"] or Path(previous["workspace"]).exists():
                raise SageError("ACCEPTANCE_RESTART", "Restart is restricted to a blocked pre-source attempt.")
            (folder / (scenario + "-previous-run-" + previous_id + ".json")).write_text(
                json.dumps({"run_id": previous_id, "calls_used": previous["calls_used"], "status": previous["status"]}), encoding="utf-8")
            restarting = True
        if args.resume_run:
            run_id = args.resume_run
        elif run_pointer.is_file() and not restarting:
            run_id = json.loads(run_pointer.read_text(encoding="utf-8"))["run_id"]
        else:
            source = None
            if scenario == "repair":
                source = folder / "defective-snapshot"
                if not source.exists():
                    write_project_files(source, [
                        {"path": "calc.py", "content": "def divide(a, b):\n    return a * b\n"},
                        {"path": "test_calc.py", "content": "import unittest\nfrom calc import divide\nclass Division(unittest.TestCase):\n    def test_divide(self):\n        self.assertEqual(divide(6,3),2)\n"},
                        {"path": "README.md", "content": "# Division snapshot\nThe regression currently fails.\n"}], Policy())
                before = runner.run("python-stdlib", source, 90)
                (folder / "repair-before.json").write_text(json.dumps(before, indent=2), encoding="utf-8")
                summary = before.get("summary") or {}
                if before["status"] != "FAIL" or summary.get("tests_run", 0) < 1 or summary.get("failures", 0) < 1:
                    raise SageError("ACCEPTANCE_PRECONDITION", "The known broken seed must fail an actual sandbox test.")
                (folder / "repair-source-before.json").write_text(json.dumps(project_manifest(source)), encoding="utf-8")
            created = engine.create(SLUG_IDEA if scenario == "build" else DIVIDE_IDEA,
                                    folder / (scenario + "-project"), args.approval_id,
                                    live=True, auto_approve_plan=True, max_model_calls=8,
                                    max_repairs=2, max_seconds=900, profile="python-stdlib", source=source,
                                    coordinator=configuration)
            run_id = created["run_id"]
            run_pointer.write_text(json.dumps({"run_id": run_id}), encoding="utf-8")
        bound = engine.store.load(run_id)
        expected_idea = SLUG_IDEA if scenario == "build" else DIVIDE_IDEA
        if (bound["idea"] != expected_idea.strip() or Path(bound["workspace"]) != folder / (scenario + "-project")
                or bound.get("coordinator") != configuration):
            raise SageError("ACCEPTANCE_BINDING", "Run does not belong to the selected scenario/workspace.")
        result = engine.run(run_id, live=True, pause_after=args.pause_after)
        if result["status"] == "DONE":
            assert_independent_acceptance(engine.store.load(run_id), oracle)
            if configuration:
                assert_ruflo_acceptance(engine.store.load(run_id))
        if scenario == "repair":
            original = project_manifest(folder / "defective-snapshot")
            saved = json.loads((folder / "repair-source-before.json").read_text(encoding="utf-8"))
            if original != saved:
                raise SageError("ACCEPTANCE_SOURCE_CHANGED", "The original defective project was modified.")
        result["scenario"] = scenario
        results.append(result)
        (folder / (scenario + "-result.json")).write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps(result, ensure_ascii=True), flush=True)
        if result["status"] != "DONE":
            break
    budget = json.loads((folder / "live-budget.json").read_text(encoding="utf-8"))
    print(json.dumps({"reserved_calls": budget["reserved_calls"], "limit": budget["limit"], "results": results}), flush=True)
    return 0 if all(result["status"] == "DONE" for result in results) else 2


if __name__ == "__main__":
    raise SystemExit(main())
