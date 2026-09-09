# SAGE Release Readiness — فارسی / English

این سند وضعیت آماده‌بودن SAGE برای بازبینی، ارائه و انتشار را مشخص می‌کند. این سند «ادعای امنیتی» یا مجوز اجرای Target واقعی نیست؛ هر اجرای بیرونی همچنان به Scope و Approval مستقل نیاز دارد.

## فارسی

### SAGE چیست؟

SAGE یک **Vibe Engineering Protocol & Runtime Kit** است: چارچوبی عمومی برای تبدیل یک درخواست مبهم یا Vibe Coding به کار مهندسیِ قابل‌فهم، قابل‌تست و قابل‌ردیابی. SAGE خودش محصول دامنه‌ای، کدنویس خودکار یا جایگزین تصمیم انسانی نیست.

### مسیر اصلی

```text
Intent → Intake → Discover → Plan → Implement → Verify → DONE / BLOCKED / ESCALATED
```

- `Intake`: هدف، محدودیت‌ها، ابهام‌ها و سطح ریسک را ثبت می‌کند.
- `Discover`: Skill، Tool و Provider مناسب را پیدا و پیشنهاد می‌کند؛ مجوز اجرا نمی‌دهد.
- `Plan`: معماری، Scope، Gateها، معیار پذیرش و روش Rollback را مشخص می‌کند.
- `Implement`: فقط تغییراتِ مجاز در Plan تأییدشده را اجرا می‌کند.
- `Verify`: تست، مشاهده و شواهد مستقل را بررسی می‌کند و یکی از سه نتیجه را می‌دهد.

### اجزای تحویلی

۱) **Protocol و Contract** — قواعد، نقش‌ها، Authority، Scope و Approval در `SAGE_v0.8_EXECUTION_PROTOCOL_AND_SKILL_CONTRACT.md`

۲) **Runtime** — اجرای مرجع و مرز کنترل‌شدهٔ Production در `runtime/`

۳) **Skill Pack** — پنج مرحلهٔ استاندارد در `skills/` و ترتیب رسمی در `skills/registry.json`

۴) **Registry و Discovery** — توصیف و Route کردن `Agent / Tool / Provider / Skill`

۵) **Evidence Ledger** — ثبت append-only شواهد، نتایج تست و تصمیم‌ها

۶) **Diagram-as-Code** — مدل قابل‌ویرایش معماری در `docs/diagrams/sage-architecture.mmd`

۷) **SDK و CLI** — بستهٔ بدون وابستگی در `sdk/python/` و فرمان‌های `sage.ps1`

۸) **Security Adapter** — قرارداد اختیاری Strix در `config/` و `schemas/`؛ Strix بخشی از هسته و اعطاکنندهٔ Authority نیست.

### وضعیت فعلی

| حوزه | وضعیت | تفسیر |
|---|---|---|
| هستهٔ پروتکل و State Machine | آمادهٔ بازبینی | قرارداد و مسیر چرخه مشخص است |
| Skill/Tool/Provider Registry | آمادهٔ بازبینی | Discovery پیشنهاددهنده و محدود به Scope است |
| SDK و CLI | آمادهٔ بازبینی | نصب و اجرای محلی باید با CI همین نسخه بررسی شود |
| Diagram-as-Code | آمادهٔ استفاده | منبع ویرایش‌پذیر برای دیاگرام است |
| Strix Adapter | قراردادی / Dry-Run | Scan Live کامل، نتیجهٔ انتشار محسوب نمی‌شود |
| Providerهای بیرونی | Opt-in | اتصال واقعی نیازمند Target و Approval مستقل است |
| GitHub Release | فقط پس از تأیید نهایی | Commit، Tag و Push نباید از این سند استنباط شود |

### معیار پذیرش انتشار

- همهٔ قراردادها و Fixtureها اعتبارسنجی شوند.
- Lifecycle بدون پرش مرحله‌ای، با نتیجهٔ قابل‌ردیابی اجرا شود.
- SDK و CLI روی محیط هدف نصب و اجرا شوند.
- Diagram با معماری واقعی همخوان باشد.
- Source Manifest و provenance برای فایل‌های تحویلی به‌روز باشند.
- هیچ Secret، Target خصوصی یا خروجی خام Strix وارد مخزن نشود.
- هر Live Adapter دارای Scope، Approval، Review، بودجه، زمان و شواهد مستقل باشد.

تا زمانی که این موارد بررسی و تأیید نشده‌اند، برچسب درست نسخه `Review Candidate` است؛ عبارت «امن و بدون آسیب‌پذیری» مجاز نیست.

## English

### What SAGE is

SAGE is a **Vibe Engineering Protocol & Runtime Kit**. It turns an ambiguous request or vibe-coding prompt into work that is scoped, reviewable, testable and evidence-backed. SAGE is not a domain application, an autonomous code generator, or a replacement for human decisions.

### Core flow

```text
Intent → Intake → Discover → Plan → Implement → Verify → DONE / BLOCKED / ESCALATED
```

Discover is advisory and never grants authority. Implement is gated by an approved plan. Verify bases the outcome on observations and evidence.

### Delivery map

- Protocol and contracts: `SAGE_v0.8_EXECUTION_PROTOCOL_AND_SKILL_CONTRACT.md`
- Runtime: `runtime/`
- Ordered Skill Pack: `skills/` and `skills/registry.json`
- Registry and discovery: Agent/Tool/Provider/Skill descriptors
- Evidence Ledger: append-only evidence and decisions
- Diagram-as-Code: `docs/diagrams/sage-architecture.mmd`
- SDK and CLI: `sdk/python/` and `sage.ps1`
- Optional Strix security adapter: `config/` and `schemas/`

### Release gates

Run the repository's release checks in PowerShell 7 and preserve the output as evidence. Confirm contract validation, lifecycle behavior, SDK/CLI smoke checks, diagram consistency, provenance and secret hygiene. Live adapters remain opt-in and require a separately approved target, scope, time window, budget, review and independent evidence.

The correct pre-release label is `Review Candidate` until the gates are verified. Do not claim that a scan proves the absence of vulnerabilities.

