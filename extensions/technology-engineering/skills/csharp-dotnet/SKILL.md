---
name: csharp-dotnet
description: Use for C#/.NET applications, Unity code and Windows integration.
---

Adapted from the supplied v0.2 blueprint. Before implementation, read
[the specialist contract](../../docs/specialist-contract.md) and the task's
technology decision. This workflow does not choose its own authority or run
an optional SENS integration.


# csharp-dotnet

Use this skill only when its stated scope matches the user's task. Load the minimal supporting context needed, not the entire reference corpus.

## Procedure
1. Determine exact .NET SDK, target framework and if project uses Unity/Mono/IL2CPP.
2. Prefer idiomatic async and cancellation, nullability, typed contracts and consistent DI.
3. Validate installed `dotnet build`, `dotnet test`, analyzers; use Unity test runner if applicable.
4. Verify engine-specific APIs from matching official docs; Unity C# compatibility is not identical to latest .NET.
5. Avoid untested engine-specific scene mutation.

## Reporting
List source links and version; changed files; executed verification with actual outcomes; unresolved assumptions; release/deploy actions requiring human approval. Never state a check passed unless it ran.
