---
name: docs-knowledge
description: Use for official documentation retrieval, ADRs, RAG entries, version tracking and lessons learned.
---

Adapted from the supplied v0.2 blueprint. Before implementation, read
[the specialist contract](../../docs/specialist-contract.md) and the task's
technology decision. This workflow does not choose its own authority or run
an optional SENS integration.


# docs-knowledge

Use this skill only when its stated scope matches the user's task. Load the minimal supporting context needed, not the entire reference corpus.

## Procedure
1. Search local source-of-truth and official docs first; version API results.
2. Store claim + citation + version/commit + fetched-on date + test result + confidence + expiration trigger.
3. Keep raw observations and interpretations separate; preserve contradictions and supersession history.
4. Avoid storing private code in a public vector store.
5. Update knowledge artifacts only in approved scope; memory entries must not be misrepresented as model fine-tuning.

## Reporting
List source links and version; changed files; executed verification with actual outcomes; unresolved assumptions; release/deploy actions requiring human approval. Never state a check passed unless it ran.
