# SAGE — Vibe Engineering Protocol & Runtime Kit

SAGE is a provider-neutral protocol and runtime kit for turning vibe-coding intent into scoped, reviewable, evidence-backed engineering work. It is not a code generator or a domain-specific application.

## فارسی

SAGE یک پروتکل و کیت Runtime برای تبدیل وایب‌کدینگ به کار مهندسیِ دارای Scope، تست، امنیت، شواهد و قابلیت Rollback است.

## What it provides

- deterministic intake, clarification and risk classification (R0–R4)
- architecture modeling and Diagram-as-Code contracts
- generic Agent/Skill/Tool/Provider discovery and routing
- authority, scope, security and approval gates
- workflow state machine and tamper-evident evidence ledger
- convergence checks between specification, implementation and observed reality

## Quick start

Use PowerShell 7:

```powershell
.\sage.ps1 validate
.\sage.ps1 demo
.\sage.ps1 discover -Capability json-schema-validation
.\sage.ps1 operations
.\sage.ps1 interfaces -Capability json-schema-validation
.\sage.ps1 lifecycle

# Optional Python SDK
python -m pip install ./sdk/python
python -m sage_sdk validate ./fixtures/v0.8.2/deployment-contract.json
```

The demo is intentionally domain-neutral and does not contact networks or execute external tools. Live adapters require a separately reviewed target, scope and approval.

`interfaces` validates/discovers the synthetic reference descriptors and returns
advisory candidates. Use `-RegistryPath` for an owned descriptor directory;
selection is not evidence of a functioning live CLI/MCP/host connection.

## Repository map

- `SAGE_v0.8_EXECUTION_PROTOCOL_AND_SKILL_CONTRACT.md` — formalized protocol baseline
- `schemas/` and `policies/` — machine-readable contracts
- `runtime/reference/` — executable reference behavior
- `runtime/production/` — controlled production boundary (DRY_RUN by default)
- `runtime/production/SageOperations.psm1` — deployment-plan and operations-gate runtime (DRY_RUN by default)
- `skills/` — SAGE lifecycle Skill Pack (`intake → discover → plan → implement → verify`)
- `skills/registry.json` — ordered lifecycle registry and authority boundaries for the Skill Pack
- `bundles/` — versioned role/workflow bundles
- `examples/` — public demonstrators
- `docs/diagrams/` — editable Diagram-as-Code architecture model for SAGE
- `docs/architecture/` — Agent-Native interface standards for API, Bridge, CLI and MCP
- `docs/decisions/` — recorded interface-selection and reuse decisions
- `SAGE_v0.8.4_AGENT_NATIVE_INTERFACE_DELTA.md` — normative Agent-Native extension to the preserved protocol baseline
- `tools/` — validation and CI entrypoints
- `sdk/python/` — installable, dependency-free contract SDK
- `schemas/v0.8/sage-agent-interface.schema.json` — typed Agent-Native interface descriptor
- `SAGE_v0.8.1_AGENTIC_ENGINEERING_ENHANCEMENTS_DELTA.md` — approved enhancement delta (Context, Workflow, Sensors, Evaluation, AI-SSDF)
- `SAGE_v0.8.2_PRODUCTION_DELIVERY_OPERATIONS_DELTA.md` — production delivery and operations contracts
- `docs/RELEASE_READINESS.fa-en.md` — bilingual release gates, delivery status and acceptance criteria
- `docs/INFOGRAPHIC_HANDOFF.fa-en.md` — bilingual brief for architecture/process infographic production

## Status

GitHub delivery: `v0.8.4` is a **pre-release / Review Candidate**, not a
security-certified stable release. A complete Strix scan is still pending;
interrupted historical scans are not security evidence. See
`SAGE_v0.8.4_AGENT_NATIVE_RELEASE.md` for the release scope and limitations.

انتشار GitHub نسخهٔ `v0.8.4` از نوع **پیش‌انتشار / نامزد بازبینی** است.
اسکن کامل Strix هنوز انجام نشده و این نسخه تأییدیهٔ امنیتی ندارد.

Version `0.8.0` remains the preserved Formalized Baseline; `0.8.3` remains the historical package. The current local `0.8.4` Review Candidate adds Agent-Native descriptor validation/discovery and eight bundled Skills. The Python SDK provides deployment-contract validation; lifecycle and invocation planning remain reference/Dry-Run. A general autonomous product-building runtime and all live CLI/MCP/host bindings are not established by these tests. External integrations require their own evidence.

The lifecycle bundle is deliberately ordered: discovery is advisory and cannot authorize execution; implementation requires an approved plan; verification returns `DONE`, `BLOCKED` or `ESCALATED` from evidence. Agent-facing interfaces follow `Native API → Thin Bridge → Typed CLI/MCP → Skill`; capability discovery never grants authority. The bundle and `skills/registry.json` must agree before release.
