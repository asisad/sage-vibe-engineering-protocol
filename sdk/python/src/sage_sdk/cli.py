"""Command line entry point for the SAGE SDK."""

import argparse
import json
import sys

from .contracts import load_json, validate_deployment_contract


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="sage-sdk", description="SAGE contract SDK")
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate", help="validate a deployment contract")
    validate.add_argument("path")
    args = parser.parse_args(argv)
    if args.command == "validate":
        issues = validate_deployment_contract(load_json(args.path))
        print(json.dumps({"status": "PASS" if not issues else "FAIL", "issues": issues}, indent=2))
        return 0 if not issues else 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
