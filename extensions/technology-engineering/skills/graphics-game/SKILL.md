---
name: graphics-game
description: Use for Blender/Godot scripting, shaders, real-time 3D and game pipelines.
---

Adapted from the supplied v0.2 blueprint. Before implementation, read
[the specialist contract](../../docs/specialist-contract.md) and the task's
technology decision. This workflow does not choose its own authority or run
an optional SENS integration.


# graphics-game

Use this skill only when its stated scope matches the user's task. Load the minimal supporting context needed, not the entire reference corpus.

## Procedure
1. Read scene geometry or source files before editing; preserve source layout and camera constraints.
2. Pin target Blender, Godot, Unity/Unreal, Three.js version and shader language.
3. Separate 3D asset transformations from rendered image generation; request appropriate file/scene tooling.
4. Check shader compilation, resource lifecycle, performance and device compatibility where test environment exists.
5. Never claim visual similarity or production-ready FPS without actual renders/profiling.

## Reporting
List source links and version; changed files; executed verification with actual outcomes; unresolved assumptions; release/deploy actions requiring human approval. Never state a check passed unless it ran.
