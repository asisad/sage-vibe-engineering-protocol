---
name: cpp-native
description: Use for C++/C native plugins, Unreal integration and ABI-sensitive libraries.
---

Adapted from the supplied v0.2 blueprint. Before implementation, read
[the specialist contract](../../docs/specialist-contract.md) and the task's
technology decision. This workflow does not choose its own authority or run
an optional SENS integration.


# cpp-native

Use this skill only when its stated scope matches the user's task. Load the minimal supporting context needed, not the entire reference corpus.

## Procedure
1. Pin compiler/toolchain, standard, platform, ABI and dependency manager.
2. Document ownership and lifetimes; prefer RAII and testable abstractions.
3. Run build, unit tests, sanitizers and relevant static analyzers when available.
4. Carefully review memory corruption, data races and unsafe FFI; no speculative performance claims.
5. For Unreal verify engine version and official subsystem documentation.

## Reporting
List source links and version; changed files; executed verification with actual outcomes; unresolved assumptions; release/deploy actions requiring human approval. Never state a check passed unless it ran.
