"""Runtime-owned verification harness. Run only inside the approved sandbox.

This script is never copied from a model response and accepts no command string.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import uuid
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

MARKER = "SAGE_VERIFY_RESULT:"

# The trusted outer interpreter never imports project modules. A separate child
# runs project tests; a generic forged outer receipt or an early os._exit cannot
# complete this protocol. This is not cryptographic attestation of hostile tests:
# a deliberately malicious test can inspect its own interpreter. Independent
# review and task-specific external oracles are still required for adequacy.
_PYTHON_WORKER = r'''
import json, os, pathlib, sys, unittest
def run():
    root, nonce = sys.argv[1:]
    sys.argv = sys.argv[:1]
    sys.path.insert(0, root)
    start = str(pathlib.Path(root) / "tests") if (pathlib.Path(root) / "tests").is_dir() else root
    suite = unittest.defaultTestLoader.discover(start, pattern="test*.py", top_level_dir=start)
    count = suite.countTestCases()
    if count < 1:
        raise ValueError("At least one discovered unittest test is required")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    passed = result.wasSuccessful() and not result.skipped and not result.expectedFailures
    summary = {"status": "PASS" if passed else "FAIL", "tests_run": result.testsRun,
               "failures": len(result.failures), "errors": len(result.errors),
               "skipped": len(result.skipped), "expected_failures": len(result.expectedFailures)}
    print("SAGE_WORKER_COMPLETE_" + nonce + ":" + json.dumps(summary, sort_keys=True), flush=True)
    return 0 if passed else 1
raise SystemExit(run())
'''


def _files(root: Path) -> list[Path]:
    result = []
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError("Project links are not permitted")
        if path.is_file() and not any(part in {".git", "__pycache__"} for part in path.parts):
            result.append(path)
    return sorted(result)


def python_stdlib(root: Path) -> dict:
    paths = [path for path in _files(root) if path.suffix == ".py"]
    if not paths:
        raise ValueError("python-stdlib needs Python source and unittest tests")
    for path in paths:
        compile(path.read_text(encoding="utf-8"), str(path.relative_to(root)), "exec")
    nonce = uuid.uuid4().hex
    prefix = "SAGE_WORKER_COMPLETE_" + nonce + ":"
    # Both parent and child are within the same OS sandbox/container. Stream
    # bounded child logs to stderr so only the outer process emits stdout receipt.
    child = subprocess.Popen([sys.executable, "-I", "-S", "-B", "-c", _PYTHON_WORKER, str(root), nonce],
                             cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             env=dict(os.environ))
    captured = bytearray()
    try:
        while True:
            block = child.stdout.read(4096)
            if not block:
                break
            captured.extend(block)
            if len(captured) > 131072:
                raise ValueError("Project test output exceeded its bounded ceiling")
            if MARKER.encode() in captured:
                raise ValueError("Project test attempted to forge an outer verification receipt")
            sys.stderr.write(block.decode("utf-8", errors="replace"))
            sys.stderr.flush()
        code = child.wait()
    finally:
        if child.poll() is None:
            child.kill()
            child.wait()
        child.stdout.close()
    records = [line[len(prefix):] for line in captured.decode("utf-8", errors="replace").splitlines()
               if line.startswith(prefix)]
    if len(records) != 1:
        raise ValueError("Project test worker exited without one completed result")
    summary = json.loads(records[0])
    if (not isinstance(summary, dict) or type(summary.get("tests_run")) is not int or
            summary["tests_run"] < 1 or summary.get("status") not in {"PASS", "FAIL"}):
        raise ValueError("Project test worker returned an invalid result")
    if code != 0 or any(summary.get(key) != 0 for key in ("failures", "errors", "skipped", "expected_failures")):
        summary["status"] = "FAIL"
    return {**summary, "profile": "python-stdlib", "worker_completed": True,
            "source_files_checked": len(paths), "coverage": "syntax-and-project-unittest",
            "limits": ["Project tests are untrusted; independent review and task-specific external oracles remain required"]}


class _Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs = []
        self.seen_html = False

    def handle_starttag(self, tag, attrs):
        self.seen_html = self.seen_html or tag == "html"
        for name, value in attrs:
            if name in {"src", "href"} and value:
                self.refs.append(value)


def static_web(root: Path) -> dict:
    paths = _files(root)
    if not (root / "index.html").is_file():
        raise ValueError("static-web requires index.html")
    checked = 0
    for path in paths:
        if path.suffix.lower() != ".html":
            continue
        page = _Page()
        page.feed(path.read_text(encoding="utf-8"))
        page.close()
        if not page.seen_html:
            raise ValueError("HTML entry must contain an html element")
        for ref in page.refs:
            url = urlsplit(ref)
            if url.scheme or url.netloc:
                raise ValueError("Static offline profile does not permit remote resource references")
            relative = unquote(url.path)
            if not relative:
                continue
            target = (root / relative.lstrip("/") if relative.startswith("/") else path.parent / relative).resolve()
            if not target.is_relative_to(root.resolve()) or not target.is_file():
                raise ValueError("HTML local resource is missing or outside the project")
        checked += 1
    return {"status": "PASS", "profile": "static-web", "tests_run": checked,
            "source_files_checked": checked,
            "coverage": "offline-html-and-local-resource-check-only",
            "limits": ["No browser, rendering, accessibility or JavaScript behavioral proof"]}


def node_stdlib(root: Path) -> dict:
    paths = _files(root)
    tests = [path for path in paths if path.name.endswith((".test.js", ".test.mjs", ".test.cjs"))]
    if not tests:
        raise ValueError("node-stdlib requires at least one *.test.js/mjs/cjs file")
    executable = os.environ.get("SAGE_VERIFIER_NODE")
    if not executable or not Path(executable).is_absolute():
        raise ValueError("Trusted Node executable was not provisioned")
    # Fixed node --test arguments, never package scripts or model-selected shell.
    completed = subprocess.run([executable, "--test", *[str(path) for path in tests]], check=False)
    return {"status": "PASS" if completed.returncode == 0 else "FAIL",
            "profile": "node-stdlib", "tests_run": len(tests),
            "source_files_checked": len(tests), "coverage": "node-native-test-runner"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=("python-stdlib", "node-stdlib", "static-web"), required=True)
    parser.add_argument("--workspace", required=True)
    args = parser.parse_args()
    root = Path(args.workspace).resolve()
    try:
        os.chdir(root)
        result = {"python-stdlib": python_stdlib, "node-stdlib": node_stdlib,
                  "static-web": static_web}[args.profile](root)
    except (Exception, SystemExit) as exc:
        result = {"status": "FAIL", "profile": args.profile,
                  "error": type(exc).__name__, "message": str(exc)[:1000]}
    print(MARKER + json.dumps(result, ensure_ascii=True, sort_keys=True), flush=True)
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
