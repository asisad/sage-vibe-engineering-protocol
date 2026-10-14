---
name: emerging-language-research
description: Use to investigate fast-changing languages such as Mojo, Zig or a niche DSL.
---

Adapted from the supplied v0.2 blueprint. Before implementation, read
[the specialist contract](../../docs/specialist-contract.md) and the task's
technology decision. This workflow does not choose its own authority or run
an optional SENS integration.


# emerging-language-research

Use this skill only when its stated scope matches the user's task. Load the minimal supporting context needed, not the entire reference corpus.

## Procedure
1. Start with the language's official versioned docs and toolchain notes; record current stability and platform support.
2. Build a minimal reproducible spike in an isolated sandbox.
3. Check package ecosystem, deployment portability, runtime performance and support horizon against Rust/Go/C++/Python baseline.
4. Label unsupported or unstable APIs explicitly and propose a containment strategy.
5. Do not recommend production adoption based only on a marketing benchmark or a plausible-looking code sample.

## Reporting
List source links and version; changed files; executed verification with actual outcomes; unresolved assumptions; release/deploy actions requiring human approval. Never state a check passed unless it ran.
