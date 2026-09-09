# SAGE v0.8.2 — Production Delivery & Operations Delta

Status: Approved Integration Delta  
Base: SAGE v0.8.1 Formalized Enhancement Baseline  
Version: 0.8.2-draft.1  
Date: 2026-09-09

این Delta لایهٔ رساندن خروجی مهندسی به محیط اجرا را اضافه می‌کند. SAGE ابزار خاصی را Core نمی‌کند؛ Docker/Compose، Coolify، Dokploy، Incus، Supabase و Redis به‌صورت Provider/Adapter با Contract یکسان route می‌شوند.

## ۱. قراردادها

- `Deployment Contract`: Artifact، image digest، environment، trigger، health، migration، rollback و evidence.
- `Environment Profile`: مرزهای dev/test/staging/production، secrets، network و approval.
- `Service Dependency`: سرویس‌هایی مانند Supabase و Redis با version، persistence، backup و health semantics.
- `Operations Gate`: health check، migration safety، backup freshness، observability، rollback rehearsal و human approval.

## ۲. Provider Mapping

- Docker/Compose: اجرای قابل‌تکرار سرویس‌ها در local، CI، staging و single-host production.
- Coolify/Dokploy: PaaS control-plane Adapter برای Git/Compose deployment، domain، logs و release history؛ ادعاهای rollback/rolling update باید از Provider evidence شوند.
- Incus/LXC: زیرساخت VM و system-container؛ جایگزین application-container Docker نیست.
- Supabase: Backend provider برای Postgres/Auth/Storage/Migrations؛ local stack و hosted project دو Target جدا هستند.
- Redis: cache/queue/session dependency؛ persistence و recovery باید صریح باشد.

## ۳. قواعد ایمنی

- build موفق، به‌تنهایی deploy موفق محسوب نمی‌شود.
- هر Promotion باید immutable artifact یا image digest، health evidence و rollback reference داشته باشد.
- Secret در Compose، Log، Evidence یا SENS ثبت نمی‌شود.
- Production و hosted provider بدون Target، Scope و Approval معتبر قابل invocation نیستند.
- Provider failure باید به `BLOCKED` یا `ROLLBACK_REQUIRED` منجر شود، نه fallback خاموش.

قرارداد ماشین‌خوان در `schemas/v0.8.2/sage-operations.schema.json`، Policy در `policies/v0.8.2/production-operations-policy.json` و Fixtureهای مرجع در `fixtures/v0.8.2/` قرار دارند.
