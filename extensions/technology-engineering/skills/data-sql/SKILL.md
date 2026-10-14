---
name: data-sql
description: Use for SQL schema, PostgreSQL, data pipelines, provenance, RAG metadata and UEG.
---

Adapted from the supplied v0.2 blueprint. Before implementation, read
[the specialist contract](../../docs/specialist-contract.md) and the task's
technology decision. This workflow does not choose its own authority or run
an optional SENS integration.


# data-sql

Use this skill only when its stated scope matches the user's task. Load the minimal supporting context needed, not the entire reference corpus.

## Procedure
1. Identify engine/version and source-of-truth, ownership and retention rules.
2. Design primary keys, versioned entities, provenance/citation, immutable observations and separate derived interpretations.
3. For migrations provide reversible upgrade/downgrade plans and dry-run on non-production data.
4. Use `EXPLAIN` on safe environments, verify indexes and transaction behavior.
5. Any destructive SQL, migrations on live databases or exports need explicit approval.

## Reporting
List source links and version; changed files; executed verification with actual outcomes; unresolved assumptions; release/deploy actions requiring human approval. Never state a check passed unless it ran.
