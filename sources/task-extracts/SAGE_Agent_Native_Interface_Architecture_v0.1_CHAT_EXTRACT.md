# Agent-Native Architecture — conversation extract

Provenance: the supplied `SAGE_Agent_Native_Interface_Architecture_v0.1.md`
was read in this task on 2026-09-09 from a temporary preview path. That original
path is unavailable on 2026-10-06. This is a labeled extract of reviewed
conversation content, not a byte-identical original or independent authority.
Acceptance was explicit: `تأیید ادغام Agent-Native Interface`.

The proposal defined complementary Native API, thin Bridge/Adapter, CLI, MCP,
Agent Skills and CI layers. SAGE owns interface choice, structured outputs,
security/version/compatibility rules, contract tests and reuse decisions,
without application-specific logic.

CLI requirements: deterministic exit codes, `--json`, stable command groups,
machine-readable errors, version/help metadata, mutation dry-run, timeout and
correlation IDs. MCP requirements: typed tools/schemas, stable naming, danger
classification/approval, version handshake, capability discovery, timeout,
cancellation, error taxonomy, client compatibility and context/token review.

Bridge requirements: application main-thread constraints, lifecycle, framing,
reconnect, timeout, crash isolation, host compatibility, localhost/network
security, request limits, logging and safe shutdown. Typed APIs are preferred
to arbitrary generated code; an expert escape hatch remains explicitly gated.

CI should verify schemas/help/JSON, unit/contract/integration behavior,
compatibility, installation, smoke, failure handling, license and dependency
security. GUI integrations need headless contract CI and host smoke CI.

Reuse choices: ADOPT sound code when license/maintenance/tests/security fit;
ADAPT useful existing foundations with bounded changes; BUILD for unsuitable
architecture, blocking license/security or higher adaptation cost.

CLI-Anything was proposed as an ADAPT methodological reference rather than a
mandatory SAGE dependency. Interface Skills and verification scripts should
enforce separated responsibilities, versioned outputs, evidence and security.

Current disposition and implementation coverage are in the v0.8.4 delta and
verification report; this extract does not grant execution authority.
