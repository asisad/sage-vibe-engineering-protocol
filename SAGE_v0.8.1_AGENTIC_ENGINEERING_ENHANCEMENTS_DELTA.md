# SAGE v0.8.1 — Agentic Engineering Enhancements Delta

Status: Formalized Enhancement Baseline  
Base: SAGE v0.8.0 Formalized Baseline  
Version: 0.8.1  
Date: 2026-09-09

این Delta حاصل بازبینی مقایسه‌ای SAGE با Spec Kit، BMAD-METHOD، GitLab AI-Assisted Development، SWE-agent، NIST SSDF/SSDF-A و پژوهش‌های مرتبط با Agentic Software Engineering است. Baseline v0.8 تغییر نمی‌کند؛ این سند Baseline الحاقی رسمی v0.8.1 است.

## ۱. تصمیم‌های ادغام

### DEC-0.8.1-01 — Context/Memory Manifest

حافظهٔ پروژه یک Manifest ماشین‌خوان دارد. هر ورودی باید شناسه، منبع، نسخه، authority، freshness، حساسیت و محدودهٔ استفاده داشته باشد. Context Builder فقط حداقل Context لازم برای Task را می‌سازد و ورودی منقضی یا خارج از Scope را وارد نمی‌کند.

### DEC-0.8.1-02 — Spec Workflow Compatibility

SAGE یک Profile سازگار با جریان `Constitution → Specify → Plan → Tasks → Implement → Verify/Converge` ارائه می‌کند. این Profile جایگزین State Machine و Gateهای SAGE نیست؛ مراحل Spec Kit یا GitLab به‌عنوان Workflow Adapter route می‌شوند و Risk، Approval و Evidence SAGE روی آن‌ها اعمال می‌شود.

### DEC-0.8.1-03 — Harness/Sensor Contract

هر Sensor باید نوع، ورودی، خروجی، هزینه، determinism، privacy و failure semantics خود را اعلام کند. Sensorهای computational (test, lint, type-check, SAST) از Sensorهای inferential (AI review, semantic review) جدا ثبت می‌شوند. هیچ Sensor به‌تنهایی Authority یا Completion ایجاد نمی‌کند.

### DEC-0.8.1-04 — Agent Evaluation Gate

اجرای Agent باید trajectory حداقلی، tool calls، زمان، هزینه، نتیجهٔ تست، خطا، iteration count و disposition را ثبت کند. Regression Gate باید سناریوهای ثابت را دوباره اجرا کند؛ یک خروجی زبانی موفق بدون Evidence اجرایی معتبر نیست.

### DEC-0.8.1-05 — AI-SSDF Security Profile

برای سیستم‌های Agentic، کنترل‌های SSDF با موارد زیر تکمیل می‌شوند: prompt/tool injection، زنجیرهٔ تأمین Skill و Provider، integrity مدل و پیکربندی، محرمانگی Context، مدیریت دادهٔ حساس، human oversight و ثبت provenance. Strix می‌تواند یک Security Sensor/Adapter باشد، اما بخشی از Core نیست.

### DEC-0.8.1-06 — Dynamic Role Routing

نقش‌های BMAD الهام‌بخش‌اند، اما Agentهای ثابت برای همهٔ Taskها اجباری نیستند. Orchestrator بر اساس Risk، Capability، Cost و Gateهای لازم نقش‌های Architect، Implementer، QA یا Safety را انتخاب می‌کند.

## ۲. قراردادهای جدید

قراردادهای ماشین‌خوان در `schemas/v0.8.1/sage-enhancements.schema.json` و Policy اجرایی در `policies/v0.8.1/agentic-engineering-policy.json` قرار دارند. Fixtureهای مرجع در `fixtures/v0.8.1/` هستند. این مجموعه پس از اعتبارسنجی CI و تأیید صریح کاربر در 2026-09-09 رسمی شد.

## ۳. چیزهایی که عمداً ادغام نشدند

- شش Agent ثابت BMAD برای هر پروژه؛
- ادعای اینکه Star، Download یا تعداد Agent معیار کیفیت مهندسی است؛
- اجرای خودکار Sandbox یا Provider خارجی برای R0/R1؛
- جایگزینی مدل Approved با خروجی Reverse Discovery؛
- ثبت کامل Prompt، Secret، exploit payload یا دادهٔ شخصی در Telemetry؛
- تبدیل خروجی AI Review به مدرک قطعی بدون تست یا بررسی انسانی متناسب.

## ۴. مرز پیاده‌سازی

این Delta قرارداد و Reference Validation را اضافه می‌کند. اتصال واقعی به سرویس SENS، Rendererهای خارجی، Backend Registry، Benchmark توزیع‌شده و Live Providerها همچنان نیازمند Adapter مستقل، Scope و مجوز جداگانه است.
