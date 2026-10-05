# ADR: Agent Interface Selection

- **Status:** Accepted
- **Decision:** Prefer `Native API → Thin Bridge → Typed MCP/CLI → Skill`.
- **Rationale:** typed, auditable surfaces reduce arbitrary execution and keep
  provider-specific behavior outside the SAGE control plane.
- **Safety:** capability discovery is advisory; Authority, Scope and Approval
  gates remain authoritative.
- **Evidence:** interface descriptor, contract tests and invocation receipt.
