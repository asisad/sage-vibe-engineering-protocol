#!/usr/bin/env python3
"""Explicit, isolated Issue #4 experiments. No engine installation or default change.

Uses existing SAGE budgets, source validation, checks, state and Ruflo binding.
This is an evaluation harness, not an independently authoritative runtime.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime/autonomous/src"))
from sage_runtime.engine import Engine
from sage_runtime.providers import CodexProvider, SandboxRunner
from sage_runtime.safety import Policy, SageError, project_manifest, write_project_files, reject_links
from sage_runtime.schemas import FILES_SCHEMA, validate

spec = importlib.util.spec_from_file_location("sage_existing_live_acceptance", ROOT / "tools/Run-SageAutonomousLive.py")
live = importlib.util.module_from_spec(spec)
spec.loader.exec_module(live)

APPROVAL = "SAGE-OHSDK-20261024-APPROVED"
MODEL = "gpt-6.1-sol"
IMAGE = "sha256:6a0e06f5ba0b373d051aabd3fffb9b873f27f9a2a3a14bcbe37dee6f0e3bbc70"
RUFLO_IMAGE = "sha256:2129e1830c6f94ba5ab60682eed9cc62ec536bb7435de462358f111814b78782"
GATE_TASK = """Fix the existing bounded calculator acceptance verifier in
tools/verify_ruflo_live_acceptance.py. Preserve its CLI and current safety checks.
A modified calculator plus an empty test suite or an entirely skipped suite
must NOT be verified. A genuine changed calculator with executed passing tests
must still pass. Use Python stdlib only, no shell=True, network, installations
or services. Keep the repair limited to the verifier; preserve supplied tests.
Use python-stdlib, root unittest tests and a short README. All requirements are
specified; no clarification needed. SAGE performs independent final checking.
"""

# Controller-owned oracle never supplied as editable model output.
GATE_ORACLE = '''import hashlib,json,pathlib,subprocess,sys,tempfile,unittest
VERIFIER=pathlib.Path(__file__).resolve().parent/'tools'/'verify_ruflo_live_acceptance.py'
class IndependentGateAcceptance(unittest.TestCase):
 def check_fixture(self,test_code):
  with tempfile.TemporaryDirectory() as d:
   base=pathlib.Path(d); root=base/'project'
   (root/'src').mkdir(parents=True); (root/'tests').mkdir()
   (root/'src/__init__.py').write_text('')
   target=root/'src/calc.py'; target.write_text('def add(a,b): return a-b\\n')
   baseline=hashlib.sha256(target.read_bytes()).hexdigest()
   target.write_text('def add(a,b): return a+b\\n')
   (root/'tests/test_calc.py').write_text(test_code)
   output=base/'receipt.json'
   p=subprocess.run([sys.executable,str(VERIFIER),'--workspace',str(root),'--task-id','eval.gate.001','--engine','direct','--baseline',baseline,'--output',str(output)],capture_output=True,text=True,timeout=15)
   return p.returncode,json.loads(output.read_text())
 def test_real_test_passes(self):
  code,receipt=self.check_fixture('import unittest\\nfrom src.calc import add\\nclass T(unittest.TestCase):\\n def test_sum(self): self.assertEqual(add(2,3),5)\\n')
  self.assertEqual(code,0,receipt); self.assertTrue(receipt['verified'])
 def test_empty_suite_never_passes(self):
  code,receipt=self.check_fixture('# no executable tests\\n')
  self.assertNotEqual(code,0,receipt); self.assertFalse(receipt['verified'])
 def test_entirely_skipped_suite_never_passes(self):
  code,receipt=self.check_fixture('import unittest\\n@unittest.skip("not executed")\\nclass T(unittest.TestCase):\\n def test_skip(self): pass\\n')
  self.assertNotEqual(code,0,receipt); self.assertFalse(receipt['verified'])
'''


def save(path, value):
    reject_links(path)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def case(scenario):
    if scenario == "slug":
        return live.SLUG_IDEA, live.SLUG_ORACLE, [], {"slug.py", "test_slug.py", "README.md"}
    if scenario == "divide":
        source = [{"path": "calc.py", "content": "def divide(a, b):\n    return a * b\n"}]
        return live.DIVIDE_IDEA, live.DIVIDE_ORACLE, source, {"calc.py", "test_calc.py", "README.md"}
    if scenario != "gate":
        raise SageError("EVALUATION_SCOPE", "Unknown evaluation scenario.")
    source = [{"path": "tools/verify_ruflo_live_acceptance.py", "content":
               (ROOT / "tools/verify_ruflo_live_acceptance.py").read_text(encoding="utf-8")},
              {"path": "test_gate_contract.py", "content": GATE_ORACLE}]
    return GATE_TASK, GATE_ORACLE, source, {"tools/verify_ruflo_live_acceptance.py", "test_gate_contract.py", "README.md"}


def setup(folder):
    folder = reject_links(folder.absolute())
    if folder == Path.home() or folder.parent == folder or folder.is_relative_to(ROOT) or ROOT.is_relative_to(folder):
        raise SageError("EVALUATION_SCOPE", "Use a separate owned evaluation root outside the SAGE checkout.")
    if not folder.parent.is_dir():
        raise SageError("EVALUATION_SCOPE", "Evaluation parent must exist.")
    folder.mkdir(exist_ok=True)
    budget = live.DeliveryBudget(None, folder, limit=30)
    authority = {"approval_id": APPROVAL, "source": "User approved Issue #4 proposal in the SAGE task",
                 "model": MODEL, "model_jobs": 30, "seconds_per_run": 900,
                 "paid_api_access": False, "default_engine_change": False}
    path = folder / "evaluation-authority.json"
    if path.exists():
        if json.loads(path.read_text(encoding="utf-8")) != authority:
            raise SageError("EVALUATION_SCOPE", "Existing evaluation authority differs; no reset.")
    else:
        save(path, authority)
    return folder, budget


def run_direct(folder, scenario, budget):
    idea, oracle, source, allowed = case(scenario)
    output = folder / ("direct-" + scenario + "-project")
    if output.exists():
        raise SageError("EVALUATION_SCOPE", "Output exists; no replay of an uncertain model job.")
    prompt = idea + "\nExisting source data:\n" + json.dumps(source, ensure_ascii=False)
    prompt += "\nReturn complete file contents only within these paths: " + json.dumps(sorted(allowed))
    prompt += "\nDo not edit supplied tests or claim tests ran. No tool or command authority."
    budget.provider = CodexProvider(model=MODEL)
    started = time.monotonic()
    result = budget.generate("implementer", prompt, FILES_SCHEMA, folder, 300)
    validate(result.payload, FILES_SCHEMA)
    files = result.payload["files"]
    if not files or any(item["path"] not in allowed for item in files):
        raise SageError("EVALUATION_SCOPE", "Direct worker returned out-of-scope files.")
    baseline = {item["path"]: item["content"] for item in source}
    baseline.update({item["path"]: item["content"] for item in files})
    # Pre-existing tests are immutable to the model, irrespective of success.
    for item in source:
        if item["path"].startswith("test_") and baseline[item["path"]] != item["content"]:
            raise SageError("EVALUATION_SCOPE", "Worker attempted to weaken supplied tests.")
    baseline["test_sage_acceptance_oracle.py"] = oracle
    write_project_files(output, [{"path": p, "content": c} for p, c in baseline.items()], Policy())
    check = SandboxRunner(docker_image=IMAGE).run("python-stdlib", output, 120)
    summary = check.get("summary") or {}
    verified = check["status"] == "PASS" and summary.get("tests_run", 0) >= (3 if scenario == "gate" else 2)
    return {"status": "PASS_INDEPENDENT_CHECK" if verified else "FAIL", "route": "direct", "scenario": scenario,
            "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(), "worker": result.receipt,
            "check": check, "source_manifest": project_manifest(output),
            "duration_seconds": time.monotonic()-started, "product_workflow_review": "NOT_PRESENT_IN_DIRECT_BASELINE"}


def run_sage(folder, scenario, budget, route, sdk_python=None, auth_root=None, pause_after=None):
    idea, oracle, source, allowed = case(scenario)
    pointer = folder / (route + "-" + scenario + "-run.json")
    output = folder / (route + "-" + scenario + "-project")
    raw = CodexProvider(model=MODEL)
    budget.provider = raw
    provider = budget
    if route == "openhands":
        from sage_openhands_evaluation_worker import EvaluationProvider
        provider = EvaluationProvider(budget, sdk_python, auth_root, folder, allowed)
    runner = live.OracleRunner(SandboxRunner(docker_image=IMAGE), oracle)
    engine = Engine(ROOT, folder / "runs", provider=provider, runner=runner)
    if pointer.exists():
        run_id = json.loads(pointer.read_text())["run_id"]
    else:
        snapshot = None
        if source:
            snapshot = folder / (route + "-" + scenario + "-snapshot")
            write_project_files(snapshot, source, Policy())
            precondition = SandboxRunner(docker_image=IMAGE).run("python-stdlib", snapshot, 60)
            save(folder / (route + "-" + scenario + "-before.json"), precondition)
        coordinator = ({"schema_version": "sage-ruflo-worker/0.1", "image_id": RUFLO_IMAGE,
                        "coordination_root": str(folder / "coordinator")} if route == "ruflo" else None)
        created = engine.create(idea, output, APPROVAL, live=True, auto_approve_plan=True,
                                max_model_calls=6, max_repairs=0, max_seconds=900,
                                profile="python-stdlib", source=snapshot, coordinator=coordinator)
        run_id = created["run_id"]
        save(pointer, {"run_id": run_id})
    started = time.monotonic()
    result = engine.run(run_id, live=True, pause_after=pause_after)
    state = engine.store.load(run_id)
    if result["status"] == "DONE":
        live.assert_independent_acceptance(state, oracle)
        if route == "ruflo":
            live.assert_ruflo_acceptance(state)
    return dict(result, route=route, scenario=scenario, total_observed_seconds=time.monotonic()-started,
                source_manifest=state["manifest"], worker_receipts=state["receipts"], verification=state["verification"],
                ledger_verified=engine.store.verify(run_id))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--route", choices=("direct", "ruflo", "openhands"), required=True)
    p.add_argument("--scenario", choices=("slug", "divide", "gate"), required=True)
    p.add_argument("--sdk-python", type=Path)
    p.add_argument("--auth-root", type=Path)
    p.add_argument("--pause-after", choices=("PLAN", "IMPLEMENT", "VERIFY"))
    p.add_argument("--live", action="store_true")
    a = p.parse_args()
    if not a.live:
        p.error("Explicit --live is required; this experiment uses the separately approved 30-job budget")
    folder, budget = setup(a.root)
    receipt = folder / (a.route + "-" + a.scenario + "-result.json")
    if receipt.exists():
        old = json.loads(receipt.read_text(encoding="utf-8"))
        if old["status"] in ("DONE", "PASS_INDEPENDENT_CHECK"):
            print(json.dumps({"status": "EXISTING_RESULT_NOT_REPEATED", "receipt": str(receipt)}))
            return 0
    try:
        result = (run_direct(folder, a.scenario, budget) if a.route == "direct" else
                  run_sage(folder, a.scenario, budget, a.route, a.sdk_python, a.auth_root, a.pause_after))
    except SageError as exc:
        result = {"status": "BLOCKED", "route": a.route, "scenario": a.scenario,
                  "reason": exc.code + ": " + str(exc)}
    result.update(model_requested=MODEL, approval_id=APPROVAL,
                  budget=json.loads(budget.path.read_text()), paid_api_access=False,
                  peak_worker_resources="NOT_VERIFIED", default_engine_changed=False)
    save(receipt, result)
    print(json.dumps({k:result[k] for k in ("status", "route", "scenario", "budget")}, ensure_ascii=True))
    return 0 if result["status"] in ("DONE", "PASS_INDEPENDENT_CHECK", "PAUSED") else 1


if __name__ == "__main__":
    raise SystemExit(main())
