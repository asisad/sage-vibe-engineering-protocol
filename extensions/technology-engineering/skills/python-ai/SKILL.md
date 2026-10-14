---
name: python-ai
description: Use for Python AI, model evaluation, RAG, ETL, scientific pipelines and Blender Python automation.
---

Adapted from the supplied v0.2 blueprint. Before implementation, read
[the specialist contract](../../docs/specialist-contract.md) and the task's
technology decision. This workflow does not choose its own authority or run
an optional SENS integration.


# python-ai

Use this skill only when its stated scope matches the user's task. Load the minimal supporting context needed, not the entire reference corpus.

## Procedure
1. Inspect `pyproject.toml`, lockfile, Python version, tensor framework and target OS.
2. Select maintained libraries and APIs from official docs; separate inference, orchestration and memory persistence.
3. Require reproducible installs, typed data contracts, test fixtures, deterministic seeds where applicable and bounded memory.
4. Treat model output as untrusted; validate schemas, avoid leaking secrets, log safely.
5. Run installed project commands such as `ruff check`, `pytest`, `mypy/pyright` if configured; document skipped checks.
6. Benchmark critical loops before considering rewrite in Rust; use stable FFI boundary (e.g. PyO3) only if measured gain exceeds complexity.

## Reporting
List source links and version; changed files; executed verification with actual outcomes; unresolved assumptions; release/deploy actions requiring human approval. Never state a check passed unless it ran.
