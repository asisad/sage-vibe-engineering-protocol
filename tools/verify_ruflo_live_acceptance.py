#!/usr/bin/env python3
"""Independent SAGE acceptance gate for a real coding-agent run.

Never starts a model or grants authority. Runs *after* an approved executor has
operated in a disposable workspace. Does not infer success from MCP tool replies.
"""
import argparse
import datetime as dt
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile


# Read unittest's structured result; exit code 0 also includes all-skipped runs.
_TEST_RUNNER = """
import json
import pathlib
import sys
import unittest

result_path = pathlib.Path(sys.argv[1])
suite = unittest.defaultTestLoader.discover('tests', pattern='test_calc.py')
result = unittest.TextTestRunner().run(suite)
result_path.write_text(json.dumps({
    'tests_run': result.testsRun,
    'tests_skipped': len(result.skipped),
    'successful': result.wasSuccessful(),
}), encoding='utf-8')
raise SystemExit(0 if result.wasSuccessful() else 1)
"""

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--workspace", required=True)
    p.add_argument("--task-id", required=True)
    p.add_argument("--baseline", required=True, help="SHA256 of original target file")
    p.add_argument("--target", default="src/calc.py")
    p.add_argument("--test", default="tests/test_calc.py")
    p.add_argument("--engine", choices=("direct","ruflo","openhands"), required=True)
    p.add_argument("--output", required=True)
    a=p.parse_args()
    root=pathlib.Path(a.workspace).expanduser().absolute()
    output=pathlib.Path(a.output).expanduser().absolute()
    report={"schema":"sage-ruflo-acceptance/1","task_id":a.task_id,"engine":a.engine,
        "timestamp":dt.datetime.now(dt.timezone.utc).isoformat(),
        "status":"BLOCKED","verified":False,"checks":{}}
    try:
        if not root.is_dir() or root.is_symlink() or root==pathlib.Path.home() or root==pathlib.Path(root.anchor):
            raise ValueError("Disallowed workspace")
        def checked(relative):
            path=pathlib.Path(relative)
            if path.is_absolute() or ".." in path.parts or not path.parts:
                raise ValueError("Invalid relative path")
            resolved=(root/path).resolve(strict=True)
            if not resolved.is_relative_to(root.resolve()):
                raise ValueError("Path escapes workspace")
            return resolved
        target=checked(a.target)
        test=checked(a.test)
        before=a.baseline.lower()
        if len(before)!=64 or any(c not in "0123456789abcdef" for c in before):
            raise ValueError("Invalid baseline digest")
        after=sha(target.read_bytes())
        report["checks"]["target_changed"]=before!=after
        report["checks"]["target_sha256"]=after
        # Execute only the exact fixture test in the explicitly provided workspace.
        # No shell, no arbitrary test runner or package installation.
        if a.test!="tests/test_calc.py" or a.target!="src/calc.py":
            raise ValueError("Only the bounded calculator fixture is supported")
        with tempfile.TemporaryDirectory(prefix="sage-acceptance-pycache-") as cache:
            result_path=pathlib.Path(cache)/"unittest-result.json"
            run=subprocess.run([sys.executable,"-X",f"pycache_prefix={cache}","-c",_TEST_RUNNER,str(result_path)],
                cwd=root,timeout=45,capture_output=True,text=True)
            report["checks"]["test_exit_code"]=run.returncode
            report["checks"]["test_output_sha256"]=sha((run.stdout+"\n"+run.stderr).encode())
            report["checks"]["test_passed"]=False
            result=json.loads(result_path.read_text(encoding="utf-8"))
        if not isinstance(result,dict):
            raise ValueError("Invalid unittest result")
        tests_run=result.get("tests_run")
        tests_skipped=result.get("tests_skipped")
        successful=result.get("successful")
        if (type(tests_run) is not int or type(tests_skipped) is not int
                or not 0 <= tests_skipped <= tests_run
                or type(successful) is not bool):
            raise ValueError("Invalid unittest result")
        report["checks"]["tests_run"]=tests_run
        report["checks"]["tests_skipped"]=tests_skipped
        report["checks"]["tests_executed"]=tests_run-tests_skipped
        report["checks"]["test_passed"]=bool(
            run.returncode==0 and successful and tests_run>tests_skipped)
        report["verified"]=bool(report["checks"]["target_changed"] and report["checks"]["test_passed"])
        report["status"]="PASS" if report["verified"] else "FAIL"
    except (ValueError,OSError,subprocess.TimeoutExpired) as e:
        report["error"]=type(e).__name__+": "+str(e)[:180]
    if not output.parent.is_dir():
        raise SystemExit("Output parent must already exist")
    if output.is_relative_to(root):
        raise SystemExit("Report output must be outside executor workspace")
    output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))
    return 0 if report["verified"] else 1

if __name__=="__main__":
    raise SystemExit(main())
