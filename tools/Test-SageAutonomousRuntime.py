#!/usr/bin/env python3
"""Offline controller/transport/policy/package regression; never calls a model."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime/autonomous/src"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-path", type=Path)
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.discover(str(ROOT / "runtime/autonomous/tests"), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    receipt = {"status": "PASS" if result.wasSuccessful() and result.testsRun >= 100 else "FAIL",
               "tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
               "skipped": [{"test": str(test), "reason": reason} for test, reason in result.skipped],
               "real_model_invocations": 0, "live_acceptance": "NOT_RUN",
               "completed_at": datetime.now(timezone.utc).isoformat()}
    if args.evidence_path:
        args.evidence_path.parent.mkdir(parents=True, exist_ok=True)
        args.evidence_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=True))
    return 0 if receipt["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
