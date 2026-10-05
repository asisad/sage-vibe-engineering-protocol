---
name: mcp-review
description: Review a SAGE MCP integration's typed tools, protocol compatibility, failure behavior and authority mapping before acceptance.
---

# MCP Review

Review typed tools, naming, schemas, dangerous-operation policy,
approval/scope mapping, cancellation, version handshake, error taxonomy and
client compatibility. Reject unrestricted execution and missing receipts.

Inputs: descriptor, selected MCP protocol revision, client/host compatibility
matrix, tool schemas and actual contract/integration receipts. Read
`docs/architecture/mcp-standard.md`. Check initialization/version negotiation,
capability discovery, invalid inputs, cancellation, timeout and typed tool
errors. Review context/token cost. For a GUI target require a host smoke receipt.

Output: PASS/FAIL/REVIEW_REQUIRED with evidence links and uncovered behaviors.
Do not count a schema or mock test as an actual MCP client/server test.
Finish only when each applicable obligation is evidenced or marked unresolved.
Execution requires the existing task approval and scope; this review grants none.
