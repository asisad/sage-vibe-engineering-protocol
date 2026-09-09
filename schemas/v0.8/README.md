# Reference contract coverage

Status: draft.3 reference implementation; not production authorization enforcement.

`sage-contracts.schema.json` validates 14 record types through local `$defs`. Three run fixtures exercise Task Packet, Risk Assessment, Gate Plan, Runtime Engineering Brief, Evidence and Security Scope. سه fixture ثبتی نیز Agent Capability، Tool Descriptor و Provider Adapter کامل را پوشش می‌دهند. `sage-policies.schema.json` دو policy مرجع را اعتبارسنجی می‌کند.

The normative architecture describes the full conceptual contract. The current JSON schemas are reduced transport projections. Fields omitted from a projection must remain in the authoritative registry/task record; they must never be silently discarded in a production adapter. A production implementation must finish and test the mapping before claiming full SAGE conformance.

| Projection | Remaining full-model work |
|---|---|
| Agent Capability | Freshness policy for health/capability evidence and benchmark trust |
| Tool / Provider | Runtime verification of native bindings, timeouts and mapping behavior |
| Skill | Nested input/output/retry/compatibility objects currently accept object structure without full semantic validation |
| Approval | Identity verification, revocation, time validity and scope-subset enforcement at invocation |
| Workflow Package | Installer implementation, conflict resolution, ownership proof and removal tests |
| Evidence | Freshness, artifact hash linkage, gate/claim semantics and cryptographic trust |
| Security | Target canonicalization, ownership verification, live limits and budget enforcement |

The PowerShell validator additionally checks selected cross-object invariants: task identity, risk/authority preservation, forbidden/restricted scope preservation, evidence reference existence and R4 review requirements. Negative tests demonstrate rejection of dropped restrictions, downgraded risk, expanded authority and scope-losing adapters.

Schema-valid does not mean authorized, complete, safe to execute, or production-ready. A denied or expired authorization may be a valid record describing a blocked task. All fixture evidence is illustrative.

Run from the project root: `./tools/Test-SageContracts.ps1` (PowerShell with `Test-Json -SchemaFile` support).
