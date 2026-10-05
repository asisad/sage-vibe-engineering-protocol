# SAGE v0.8.4 Phase Plan and Review Loop

Date: 2026-10-06
Scope: the approved Agent-Native integration and a concise Persian PDR report
in chat. No PDF is requested. No new publication or Strix activation is inferred.

| Phase | Owner | Delivery | Completion evidence |
|---|---|---|---|
| 1 Architecture and formalization | root coordinator | normative delta, standards, ADRs, provenance, diagram, eight Skills | preserved baseline; release metadata, Skill validation and diagram checks |
| 2 Descriptor/runtime integration | interface_runtime Sub-Agent | typed schema, fixtures, validation, advisory discovery; coordinator registers descriptors and CLI | positive/negative schema, selection, registration and Discovery regression tests |
| 3 Package and release | release_audit Sub-Agent | candidate manifest, historical manifest preservation, SDK version, eight-Skill release checks | release checker and isolated SDK install/smoke |
| 4 Independent verification | completion_audit Sub-Agent + root | adversarial review, repair feedback, full CI and final PDR | all findings disposition and rerun receipts |

Phases 1-3 progress in parallel with disjoint file ownership. Phase 4 reviews
merged behavior, not the executor's intended result. The root coordinates the
cluster and records authoritative acceptance evidence.

Loop: implement -> independent review -> reproducible finding -> return to
owning Agent -> fix with regression test -> rerun focused checks -> unified CI.
Unresolved permission or target decisions are reported separately. No endless
retry loop substitutes for stronger evidence.

## Review feedback observed

- R1: unresolved schema refs accepted; returned to runtime Agent for local
  reference resolution, containment checks and JSON Pointer regression tests.
- R2: null descriptor input aborted selection; returned for structured rejection.
- R3: malformed generic provider/tool descriptors routed or raised an exception;
  returned for schema validation before routing.
- R4: bundle listed only five Skills; coordinator added all eight, metadata,
  inputs/outputs and scoped acceptance criteria; release Agent verifies routing.
- R5: historical 0.8.3 manifest modified; restored and new 0.8.4 candidate created
  with consistent versions and explicit pending security evidence.
- R6: completion claims overstated production coverage; replaced with actual
  descriptor/reference-runtime coverage boundaries.

Final phase status and receipts are in `SAGE_v0.8.4_VERIFICATION.md`.
External scan and publication remain separately tracked in current delivery status.

Final local status (2026-10-06): phases 1-4 COMPLETE; independent review PASS;
R1-R6 CLOSED within this scope; unified CI PASS 17/17. This completion does not
claim universal transport/host or security certification.
