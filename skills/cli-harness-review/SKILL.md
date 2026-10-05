---
name: cli-harness-review
description: Review a SAGE CLI harness's JSON output, exit codes, help, version, installation and failure semantics against its declared contract.
---

# CLI Harness Review

Review a CLI for deterministic exit codes, stable commands, `--json`, version,
help metadata, machine-readable errors, dry-run, timeout and correlation IDs.
Verify packaging, smoke tests and secret hygiene before registration.

Inputs: descriptor, executable/version, approved test directory and expected
command/response schema. Read `docs/architecture/cli-standard.md`. Exercise
help, version, valid JSON, invalid input and timeout using disposable fixtures;
verify dry-run leaves state unchanged for mutating commands. Use only approved
commands and paths. Stateful REPLs are conditional, not a universal requirement.

Output: review status, tested command/version, exit code and parsed-output
receipts, uncovered behaviors and rollback result. A file-existence test does
not establish CLI conformance. Finish when the declared contract is matched by
behavioral evidence or explicit gaps. Never echo credentials into evidence.
