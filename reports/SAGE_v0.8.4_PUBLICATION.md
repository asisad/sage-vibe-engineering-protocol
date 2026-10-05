# SAGE v0.8.4 — GitHub Pre-release Workflow

Date: 2026-10-06 (Asia/Tehran).
User decision: publish a Review Candidate with the full Strix scan deferred.
Channel: GitHub pre-release, tag `v0.8.4`; not a stable/security-certified release.

## Approved scope / محدودهٔ تأییدشده

۱) آزمون نهایی بسته و بررسی فایل‌های قابل‌انتشار.
۲) ثبت تغییرات، Push و بررسی نتیجهٔ CI در GitHub.
۳) ایجاد Tag و پیش‌انتشار `v0.8.4` با اعلام صریح وضعیت Strix.

No live provider/tool activation, paid model calls, target pentest or Strix
scan is part of this publication workflow. The default live-adapter boundary
remains disabled. The manifest retains `security_certified=false` and
`security_scan.status=PENDING`.

## Acceptance gates

- Unified CI: all 17 checks must pass locally and on GitHub.
- Exact-byte source hashes and archived originals must pass in a clean
  independent checkout; `.gitattributes` disables newline conversion.
- Review publishable files for credential patterns; exclude `tmp/` and
  `strix_runs/`. A pattern check is not a complete security scan.
- Preserve historical tags/manifests; no force-push or existing-tag replacement.
- Create the GitHub release as `prerelease=true` and `make-latest=false`.

Local generated receipts are retained under `tmp/`; remote Actions results
and the release record are the independently observable publication evidence.

## Runner compatibility repair

The first publication CI run (`37380950520`) reached the release check but
failed because inline comma-separated path expressions were received as
literal arguments by the runner's Python command. `Test-SageRelease.ps1`
now resolves the three SDK paths before the native call and splats the
argument array. Release acceptance requires a successful rerun, not that
failed run or local-only evidence.

## Publication receipts

- Repository: https://github.com/asisad/sage-vibe-engineering-protocol
- Release: https://github.com/asisad/sage-vibe-engineering-protocol/releases/tag/v0.8.4
- CI: https://github.com/asisad/sage-vibe-engineering-protocol/actions

These are receipt locations, not a claim that the workflow has succeeded
before the remote records exist. Verify the tag commit, `prerelease` flag
and the matching Actions conclusion when accepting this release.

## Strix disposition / وضعیت Strix

Strix is installed locally, but the two historical scans were interrupted.
One encountered Windows sandbox target-path visibility; the repository scan
exhausted free-model quota. Neither establishes complete coverage of 0.8.4.
Model/quota availability must be checked again when a future scan is authorized.

اسکن کامل Strix انجام نشده است. این پیش‌انتشار، ادعای نبود آسیب‌پذیری یا
تأیید امنیت ندارد. معیار پذیرش اسکن در `SAGE_STRIX_SCAN_RETRY_PLAN.md` ثبت شده است.
