---
name: engineering-qa
description: Use for independent code verification, security review, CI/evaluation and performance checks.
---

Adapted from the supplied v0.2 blueprint. Before implementation, read
[the specialist contract](../../docs/specialist-contract.md) and the task's
technology decision. This workflow does not choose its own authority or run
an optional SENS integration.


# engineering-qa

Use this skill only when its stated scope matches the user's task. Load the minimal supporting context needed, not the entire reference corpus.

## Procedure
1. Independently inspect task acceptance criteria, code diff, compiled outputs and logs.
2. Run native quality gates; check network permissions, dependency provenance and embedded secrets.
3. Probe edge cases, concurrency failures, retry storms, cancellation and resource exhaustion.
4. For SENS measure its own CPU/memory/network/latency overhead and the observed app overhead separately; detect telemetry recursion.
5. Classify each result as pass/fail/not-run; never infer correctness merely from previous agent's confidence.
6. Escalate high-severity findings or lack of safe test environment before approving release.

## Reporting
List source links and version; changed files; executed verification with actual outcomes; unresolved assumptions; release/deploy actions requiring human approval. Never state a check passed unless it ran.
