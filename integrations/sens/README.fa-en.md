# SENS Integration — جایگاه اتصال SENS به SAGE

Protocol/package: `sage-sens/0.1` / `0.1.0`.
Delivery: source-branch contract, examples and offline reference preview.
Default: DISABLED. No SENS implementation, endpoint, credential or service is connected.

## فارسی

این پوشه جایگاه رسمی اتصال پروژهٔ مستقل SENS است، نه پوشهٔ انتقال کل کد
آن و نه محل اجرای سرور در GitHub. SAGE تصمیم و مجوز را نگه می‌دارد؛ SENS
فقط رویدادهای محدود را دریافت می‌کند و تحلیل/ارجاع شواهد برمی‌گرداند.

۱) ابتدا `docs/CONNECTING_SENS.fa-en.md` را به تیم/Agent سازندهٔ SENS بدهید.
۲) SENS قرارداد `schemas/sage-sens.schema.json` را با نسخهٔ مشخص پیاده کند.
۳) از `registration.example.json` یک معرفی با وضعیت PROPOSED بسازد؛ دریافت
   یا Commit آن به معنی تصویب، اعتماد، نصب یا اتصال خودکار نیست.
۴) تغییر ثبت پیشنهادی در `registrations/` و `registry.json` بازبینی شود.
۵) اتصال واقعی، endpoint/auth، تست مستقل، بودجه و Rollback، مرحلهٔ جداست.

## Files / نقشهٔ اتصال

| Path | Purpose |
|---|---|
| `manifest.json` | ownership, protocol and explicit implementation limits |
| `schemas/sage-sens.schema.json` | registration, proposal registry, config, event and finding |
| `registration.example.json` | unconnected proposal template; no invented SENS repository |
| `registry.json`, `registrations/` | reviewed proposal location; no live instances |
| `config.example.json` | disabled, allowlisted, bounded, credential-reference-only config |
| `examples/event.json`, `examples/finding.json` | synthetic metadata, not evidence of completed work |
| `SageSens.psm1` | pure validation/context review and local batch preview; no transport |

## Local commands / آزمون محلی

Run from the SAGE repository root in PowerShell 7:

```powershell
.\sage.ps1 sens
.\sage.ps1 sens -InputPath integrations/sens/registration.example.json
.\sage.ps1 sens -InputPath integrations/sens/examples/event.json
.\sage.ps1 sens -InputPath integrations/sens/examples/event.json -Preview
.\tools\Test-SageSensIntegration.ps1
```

`-Preview` changes only an in-memory preview setting. It cannot contact a URL,
resolve credentials or activate SENS. A finding supplied through the CLI is
UNBOUND_OBSERVATION until the host explicitly checks its project/task/revision/
SENS identity using `Get-SageSensFindingReview`. Even after matching, it remains
unverified advice, not approved architecture, proof of success or an instruction.

## English — runtime and safety boundary

SENS remains an independent implementation and deployment. The source slot is
ready for its team to implement against; neither a repository Push nor a JSON
registration deploys a service. There is no HTTP server/client, background worker,
queue persistence, environment-variable resolution or automatic installation here.

The offline preview enforces project scope, serialized UTF-8 event size, duplicate
IDs and batch/queue capacity. Inspection/rejection details are capped at 256 input
events. Rate-window enforcement and timed retention are declared requirements for
a future transport, NOT implemented preview features (`rate_window_enforced=false`).

Metadata-only fields, known credential-pattern rejection and no raw payload reduce
exposure; this is not a complete DLP system or a claim that arbitrary IDs cannot
contain private data. The real emitter/receiver must apply approved redaction and
data-minimization rules. Raw source, prompts, secrets and exploit payloads are not
part of this public contract.

Optional telemetry may be dropped when unavailable. Scope/approval, security,
mandatory verification and the local SAGE Evidence Ledger must never fail open.
No SENS finding is executed automatically. Live activation needs separately
approved transport/auth details and target-specific receipts.
