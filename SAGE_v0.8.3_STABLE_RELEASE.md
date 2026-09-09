# SAGE v0.8.3 — Stable Release

SAGE is a provider-neutral Vibe Engineering Protocol & Runtime Kit. This release packages the complete, auditable lifecycle:

`Intake → Discover → Plan → Implement → Verify`

The runtime is offline-first and DRY_RUN by default. A discovered capability does not grant authority. Live adapters, external targets and mutating actions require an explicit scope, approval, review and independent evidence.

## Included

- Formalized protocol, schemas and policies
- Reference orchestrator, workflow/state-machine and evidence ledger
- Generic Provider/Tool/Agent discovery and routing
- Five canonical SAGE skills
- Production delivery and operations contracts
- Dependency-free Python SDK and PowerShell CLI
- Public GPS-map demonstrator and bilingual documentation
- Reproducible validation and release checks

## Verification

Run `./sage.ps1 ci` from PowerShell 7. The expected result is PASS for all release checks.
