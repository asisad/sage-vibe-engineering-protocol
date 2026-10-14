# SAGE / SENS — Source Integration and Push Workflow

Date: 2026-10-14 (Asia/Tehran).
User-approved scope: create the SENS integration slot, test it and Push it
together with technology-engineering 0.1 to the existing SAGE repository.
Delivery channel: source branch `master`, not a new release or version tag.

## نتیجهٔ فارسی

جایگاه اتصال پروژهٔ مستقل SENS در `integrations/sens/` ساخته شد. قرارداد،
تنظیمات غیرفعال، معرفی پیشنهادی، نمونهٔ رویداد/یافته و راهنمای پیوستن موجود
است. پروژهٔ SENS مستقر یا متصل نشده و هیچ اختیار اجرایی دریافت نمی‌کند.
افزونهٔ انتخاب فناوری نیز در همین تحویل سورس قرار می‌گیرد.

## Components and boundaries

- Five strict record contracts: proposal registration, proposal registry,
  disabled/preview config, metadata-only event, and advisory finding.
- Offline reference helpers: schema/semantic checks, exact finding context
  matching and bounded preview. No network transport, listener or worker.
- Empty registry: no invented SENS repository, live instance or self-activation.
- Future implementation handoff: protocol/version, source and capability
  declaration, review, isolated transport receipts and separate activation.
- Core/SDK version and historical v0.8.4 release artifacts remain preserved;
  a source-branch Push does not imply inclusion in that older tag.

## Verification evidence

- SENS focused tests: 56 checks passed before the final unified run.
- Technology engineering: its 130-assertion regression joins the same unified CI.
- Unified suite: 19 scripts, including all prior core/SDK/reference checks.
- Raw local receipt location: `tmp/sage-sens-source-2026-10-14-ci.json`.
- GitHub Actions matching the source commit is required before reporting
  successful remote verification; local evidence alone is not remote CI.

Tests exercise malformed/null records, self-activation/authority escalation,
protocol mismatch, credential-shaped IDs and unsafe source references, raw
payload rejection, project scope, exact finding context, byte/batch/queue limits,
duplicate IDs, bounded inspection and NOT RUN preservation. They are reference
tests, not actual SENS service tests or a full security scan.

## Publication acceptance

Inspect staged paths and source hashes; exclude generated `tmp/`, `strix_runs/`
and credentials. Commit/Push only these approved source additions. Do not force
Push, replace a tag, create a new Release, deploy SENS or activate Strix.
Check the remote commit and matching Actions result after Push.

Authoritative remote evidence locations:

- https://github.com/asisad/sage-vibe-engineering-protocol/commits/master/
- https://github.com/asisad/sage-vibe-engineering-protocol/actions
- https://github.com/asisad/sage-vibe-engineering-protocol/tree/master/integrations/sens

These locations are not a premature success claim. The delivered source commit
and final Actions conclusion are reported after they actually exist.
