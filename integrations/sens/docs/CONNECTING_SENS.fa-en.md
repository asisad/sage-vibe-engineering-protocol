# Handoff for the SENS implementation / راهنمای پیوستن SENS

SAGE-side seam: `integrations/sens/`, protocol `sage-sens/0.1`.
SENS repository: not supplied yet; `source_ref=null` is intentional.
This document is an interface handoff, not authority to deploy or publish.

## Required compatibility

۱) پیاده‌سازی اصلی SENS در مخزن خودش بماند. نام Repository، نسخه/Commit،
capabilityهای واقعی و نسخهٔ پروتکل در معرفی ثبت شوند؛ قابلیت نصب‌نشده را
به‌صورت VERIFIED یا سرویس فعال معرفی نکنید.

۲) SAGE -> SENS: فقط eventهای schema-validated، metadata-only و Projectهای
مجاز. Task/Run/Step/Actor ID، Revision و ارجاع شواهد حفظ شوند. هیچ کد منبع،
Secret، Prompt کامل یا دستور اجرایی از این کانال منتقل نشود.

۳) SENS -> SAGE: Finding از نوع OBSERVED با provenance، confidence و ارجاع
شواهد. گیرنده باید Project/Task/Revision/SENS ID را با Context مورد انتظار
تطبیق دهد. تطابق Context، صدق مشاهده یا تصویب تغییر را اثبات نمی‌کند.

۴) ثبت معرفی فقط PROPOSED است. SENS حق تغییر مجوزهای SAGE، فعال‌کردن خودش،
Flash، Deploy، اجرای فرمان یا تصویب اصلاحات را از این قرارداد نمی‌گیرد.

## Future transport acceptance checklist

- A separately reviewed adapter must define endpoint/protocol/auth and credential
  injection from approved secret storage. Do not commit a credential value.
- Prove timeouts, cancellation, finite retries/backoff, bounded async queues,
  overflow/drop counters, sampling/cardinality caps, rate windows and retention.
- Prove TLS/authentication and exact target/project scope. Evidence IDs are not
  permission to fetch arbitrary URLs or local paths.
- Prove redaction, replay/deduplication strategy, version negotiation and behavior
  when SENS is offline. Do not synchronously depend on SENS in application hot paths.
- Preserve approval/authority and mandatory evidence gates on failures; optional
  telemetry drop must not disable security or bypass the local ledger.
- Use an isolated target and actual integration receipts before enabling a live
  connection. Keep operator-controlled disable/rollback independent from SENS.

The current module implements only offline validation/context checks and a bounded
batch preview. It does not implement these network/worker requirements. SENS may
submit code and tests for review, but no self-activating hook exists in this repo.

## Safe proposal workflow

Copy the registration template into `registrations/<sens-id>.json` in a reviewed
branch. Fill only known metadata; add its relative path to `registry.json.entries`.
Run SAGE CI. The registry's `active_instances` remains empty and `auto_activate`
remains false. Review/approval of a later transport is a distinct change, not a
flag the SENS agent can switch in this interface. Do not move all SENS code into
SAGE merely to use this slot.
