---
name: typescript-web
description: Use for TypeScript frontend/backend, dashboards, WebGL and Three.js.
---

Adapted from the supplied v0.2 blueprint. Before implementation, read
[the specialist contract](../../docs/specialist-contract.md) and the task's
technology decision. This workflow does not choose its own authority or run
an optional SENS integration.


# typescript-web

Use this skill only when its stated scope matches the user's task. Load the minimal supporting context needed, not the entire reference corpus.

## Procedure
1. Inspect package manager and lockfile, framework and browser targets.
2. Use strict typing, domain boundary validation, server-only secrets and accessible UI.
3. Check WebGL/GPU resource lifecycle, dispose textures/geometries, avoid per-frame allocations.
4. Verify official docs for Three.js/react-three-fiber versions and browser support.
5. Run configured lint, `tsc --noEmit`, unit tests and production build; never claim a page was visually inspected unless renderer/browser was actually used.

## Reporting
List source links and version; changed files; executed verification with actual outcomes; unresolved assumptions; release/deploy actions requiring human approval. Never state a check passed unless it ran.
