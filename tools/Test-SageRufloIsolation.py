#!/usr/bin/env python3
"""Explicit live MCP/isolation acceptance with ZERO model calls."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime/autonomous/src"))
from sage_runtime.ruflo import DockerCoordinator, load_binding


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", required=True, type=Path)
    p.add_argument("--approval-id", required=True)
    p.add_argument("--live", action="store_true")
    p.add_argument("--evidence-path", required=True, type=Path)
    a = p.parse_args()
    if not a.live:
        p.error("Explicit --live is required even though this test never invokes a model")
    cfg = load_binding(a.config)
    run_id = uuid.uuid4().hex
    report = {"model_invocations": 0, "scope": "REAL_MCP_TASK_METADATA_AND_CONTAINER_CANARIES_ONLY"}
    with DockerCoordinator(ROOT, cfg, run_id, a.approval_id, 60) as session:
        created = session.call("task_create", {"type": "research", "description": "SAGE controller-only task persistence canary"})
        task_id = created["taskId"]
        assert created["status"] == "pending"
        session.call("task_assign", {"taskId": task_id, "agentIds": ["sage-controller-canary"]})
        active = session.call("task_status", {"taskId": task_id})
        assert active["status"] == "in_progress" and active["assignedTo"] == ["sage-controller-canary"]
        assert session.persisted(task_id)["status"] == "in_progress"
        session.call("task_cancel", {"taskId": task_id, "reason": "No model worker is part of this canary"})
        assert session.call("task_status", {"taskId": task_id})["status"] == "cancelled"
        orphan = session.call("task_create", {"type": "research", "description": "SAGE structured model job " + run_id + " planner interrupted-canary"})
        session.call("task_assign", {"taskId": orphan["taskId"], "agentIds": ["sage-controller-canary"]})
        js = r'''const fs=require('node:fs'),net=require('node:net');
let result={package_version:JSON.parse(fs.readFileSync('/opt/ruflo/node_modules/ruflo/package.json')).version,
 credential_environment_absent:!['OPENAI_API_KEY','OPENROUTER_API_KEY','ANTHROPIC_API_KEY','LLM_API_KEY'].some(k=>process.env[k]),
 host_auth_absent:!fs.existsSync('/root/.codex/auth.json'),root_write_denied:false};
try{fs.writeFileSync('/opt/ruflo/sage-denied','no')}catch(e){result.root_write_denied=['EROFS','EACCES'].includes(e.code)}
const s=net.connect({host:'198.51.100.1',port:443});let done=false;
function finish(denied){if(done)return;done=true;result.network_denied=denied;s.destroy();console.log(JSON.stringify(result));}
s.on('connect',()=>finish(false));s.on('error',()=>finish(true));s.setTimeout(1200,()=>finish(true));'''
        check = session._control(["exec", "--user", "65534:65534", session.name, "node", "-e", js], 10)
        assert check["exit_code"] == 0
        canaries = json.loads(check["stdout"])
        assert canaries["package_version"] == "3.61.1"
        assert all(canaries[key] is True for key in ("credential_environment_absent", "host_auth_absent", "root_write_denied", "network_denied"))
        report.update(canaries=canaries, protocol=session.session.version, inventory_sha256=session.inventory_hash,
                      first_process_calls=session.calls, persisted_task_id=task_id)
    with DockerCoordinator(ROOT, cfg, run_id, a.approval_id, 45) as resumed:
        observed = resumed.call("task_status", {"taskId": task_id})
        assert observed["status"] == "cancelled" and resumed.persisted(task_id)["status"] == "cancelled"
        resumed.reconcile()
        assert resumed.call("task_status", {"taskId": orphan["taskId"]})["status"] == "cancelled"
    report.update(status="PASS", fresh_process_persistence=True, interrupted_metadata_reconciled=True, image_id=cfg["image_id"],
                  lockfile_sha256=hashlib.sha256((ROOT / "extensions/ruflo/runtime/package-lock.json").read_bytes()).hexdigest())
    a.evidence_path.parent.mkdir(parents=True, exist_ok=True)
    a.evidence_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
