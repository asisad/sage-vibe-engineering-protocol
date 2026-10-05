# SAGE Agent-Native Interface Architecture

This is the normative addendum for exposing capabilities to coding agents.
SAGE keeps the following layers distinct:

```text
Agent → Skill/Procedure → MCP or CLI → Thin Bridge → Native API → Target
```

The interface choice is risk- and capability-driven. Discovery can recommend an
interface, but it never grants authority. Every invocation carries the resolved
task identity, scope, authority, timeout and evidence destination.

Bridge is optional for a direct native binding. CLI and MCP are alternatives or
complementary surfaces; neither both surfaces nor a physical bridge is required
for every task. Apply host/thread/transport constraints when selecting layers.

## Layer responsibilities

- **Native API:** the target application's typed, versioned API.
- **Bridge:** a thin lifecycle and transport boundary; it does not add authority.
- **CLI/MCP:** typed, deterministic callable surfaces with machine-readable output.
- **Skill:** guidance for when and how an agent should use a callable surface.
- **CI:** verifies schemas, compatibility, packaging and failure semantics.

Arbitrary generated code is an explicitly gated expert escape hatch, never the
default integration path.

## Interface selection

Select the smallest stable surface that satisfies the task. Record the decision
as `ADOPT`, `ADAPT` or `BUILD` and link it to the Evidence Ledger.

ADOPT requires architecture, license, maintenance, tests and security suitability.
ADAPT requires a useful core and bounded changes with continuing reuse value.
BUILD requires an unsuitable core, blocking license/security constraints or
documented adaptation cost exceeding replacement. Preserve decision rationale.

## Implementation coverage / پوشش اجرا

Package v0.8.4 validates, registers and discovers descriptors as advisory
candidates. It does not implement every target's native API, MCP server or
bridge. Descriptor checks cannot establish live transport/host conformance.
Require actual CLI/MCP client tests, installation receipts, failure handling,
dependency/license review and host smoke tests where applicable.

برای هر اتصال، مسئولیت لایه‌ها، نسخه و دلیل انتخاب ثبت می‌شود. این نسخه
انتخاب و اعتبارسنجی را اجرا می‌کند؛ اتصال واقعی هر ابزار شواهد مستقل می‌خواهد.

See the companion standards in this directory and the interface schema at
`schemas/v0.8/sage-agent-interface.schema.json`.

Normative composition: `SAGE_v0.8.4_AGENT_NATIVE_INTERFACE_DELTA.md`.
