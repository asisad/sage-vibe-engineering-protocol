---
name: devops-containers
description: Docker, Dockerfile, Compose, Kubernetes, container packaging, CI/CD infrastructure checks and security.
---

Adapted from the supplied v0.2 blueprint. Before implementation, read
[the specialist contract](../../docs/specialist-contract.md) and the task's
technology decision. This workflow does not choose its own authority or run
an optional SENS integration.


# devops-containers

Use only for the selected task scope. This is an on-demand workflow, not a running agent.

## Procedure
1. Identify environment (`dev`, `staging`, `prod`), affected project scope, service topology, registry and privilege level.
2. Inspect Dockerfile/Compose, lockfiles, pinned base images, networks, volume mounts, health checks, and secrets handling.
3. Prefer reproducible multi-stage builds, minimal privileges, proper `.dockerignore`, resource caps and image provenance.
4. Validate syntax with compatible tools, e.g. `docker compose config --quiet` if supported; record exit status; avoid daemon actions on untrusted repositories.
5. Propose only scoped edits. Treat `compose up/down`, Docker daemon access, pull/push, cluster apply and deployment as privileged and approval-gated.
6. If SAGE invokes SENS monitoring, emit only asynchronous bounded and redacted logs, never Docker credentials.

## Deliverable
Return target fingerprint, changed files, tool versions, source URLs/revisions, PASS/FAIL/NOT RUN for checks, safe rollback conditions and actions awaiting approval.
