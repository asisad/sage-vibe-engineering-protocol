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

# Optional Python SDK
python -m pip install ./sdk/python
python -m sage_sdk validate ./fixtures/v0.8.2/deployment-contract.json
```

The demo is intentionally domain-neutral and does not contact networks or execute external tools. Live adapters require a separately reviewed target, scope and approval.

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
- `tools/` — validation and CI entrypoints
- `sdk/python/` — installable, dependency-free contract SDK
- `SAGE_v0.8.1_AGENTIC_ENGINEERING_ENHANCEMENTS_DELTA.md` — approved enhancement delta (Context, Workflow, Sensors, Evaluation, AI-SSDF)
- `SAGE_v0.8.2_PRODUCTION_DELIVERY_OPERATIONS_DELTA.md` — production delivery and operations contracts

## Status

Version `0.8.0` remains the preserved Formalized Baseline; version `0.8.1` is the Formalized Agentic Engineering Enhancement Baseline. Version `0.8.2` was the Release Candidate package. Version `0.8.3` is the stable package with the complete lifecycle Skill Pack, production delivery/operations contracts and an installable SDK. External live adapters remain opt-in and separately authorized.

The lifecycle bundle is deliberately ordered: discovery is advisory and cannot authorize execution; implementation requires an approved plan; verification returns `DONE`, `BLOCKED` or `ESCALATED` from evidence. The bundle and `skills/registry.json` must agree before release.
