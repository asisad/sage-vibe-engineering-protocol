# SAGE v0.8 Provider/Tool Boundary

`SageAdapters.psm1` is the provider-neutral boundary for connecting SAGE to tools and providers.

The current production-boundary implementation intentionally supports **DRY_RUN only**. It imports and checks adapter/tool descriptors, preserves authority and scope, creates a deterministic request digest, and emits a planned receipt. It does not contact networks, invoke Strix, mutate repositories, or execute a target.

To add a live adapter later, it must be introduced as a separately reviewed adapter with explicit authority, allowlist, timeout/budget, cancellation, evidence normalization, and an independent live-test gate. Enabling `LIVE` cannot be achieved by changing a request flag in this module.

Validation:

```powershell
.\tools\Test-SageProductionAdapters.ps1
```
