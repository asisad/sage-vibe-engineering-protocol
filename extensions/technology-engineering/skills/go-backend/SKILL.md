---
name: go-backend
description: Use for Go networking, reliable services, command-line tools and microservices.
---

Adapted from the supplied v0.2 blueprint. Before implementation, read
[the specialist contract](../../docs/specialist-contract.md) and the task's
technology decision. This workflow does not choose its own authority or run
an optional SENS integration.


# go-backend

Use this skill only when its stated scope matches the user's task. Load the minimal supporting context needed, not the entire reference corpus.

## Procedure
1. Inspect `go.mod`, target Go version, package layout and build environment.
2. Prefer standard library for straightforward services; use contexts, deadlines, cancellation and bounded worker pools.
3. Run `go test ./...`, `go vet ./...`, `go test -race ./...` when supported. Race detector is not exhaustive.
4. Track allocation, pprof, CPU and memory under realistic load before language/perf decisions.
5. Treat production config/secrets/deploy as gated operations.

## Reporting
List source links and version; changed files; executed verification with actual outcomes; unresolved assumptions; release/deploy actions requiring human approval. Never state a check passed unless it ran.
