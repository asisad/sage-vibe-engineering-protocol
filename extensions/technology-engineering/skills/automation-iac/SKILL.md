---
name: automation-iac
description: Bash, PowerShell, CI YAML, Terraform HCL, Ansible and provisioning automation.
---

Adapted from the supplied v0.2 blueprint. Before implementation, read
[the specialist contract](../../docs/specialist-contract.md) and the task's
technology decision. This workflow does not choose its own authority or run
an optional SENS integration.


# automation-iac

Use only for the selected task scope. This is an on-demand workflow, not a running agent.

## Procedure
1. Identify shell, OS, provider, environment and desired/no-op behaviors.
2. Minimize privileges and side effects; avoid hard-coded secrets or unsafe remote shell execution.
3. Prefer static lint/format/type checks and isolated dry-runs. Distinguish mere validation from plans that read remote state or create locks.
4. Provide rollback, idempotency and least-privilege rationale for infrastructure changes.
5. Require approval before apply/destroy/deploy, enabling CI release workflows or accessing production credentials.
6. Log only a bounded, sanitized operation summary to SENS through SAGE event contract.

## Deliverable
Return target fingerprint, changed files, tool versions, source URLs/revisions, PASS/FAIL/NOT RUN for checks, safe rollback conditions and actions awaiting approval.
