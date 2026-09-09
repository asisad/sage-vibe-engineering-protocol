# SAGE v0.8 Validation Report

Status: PASS — Formalized Baseline  
Target version: 0.8.0  
Validation date: 2026-09-09  
Validator: tools/Test-SageContracts.ps1

## ۱. نتیجه

- Reference Schema: JSON Schema Draft 2020-12
- Fixtureهای معتبر: ۳
- Policyهای JSON معتبر: ۲
- بررسی‌های مثبت: ۱۴۲
- بررسی‌های ناموفق: ۰
- آزمون منفی: PASS؛ تغییر record_type به مقدار نامعتبر توسط Schema رد شد.

## ۲. Fixtureها

| Fixture | Risk | هدف | نتیجه |
|---|---|---|---|
| fixtures/v0.8/r0-documentation-typo.json | R0 | Scope محدود و جلوگیری از overengineering | PASS |
| fixtures/v0.8/r2-feature-data-path.json | R2 | Goal، Scope، Gate، build و write/read proof | PASS |
| fixtures/v0.8/r4-authorized-security-validation.json | R4 | Authority، Human Approval و Security Scope | PASS |

PASS در Fixture R4 به معنی اجرای pentest نیست؛ فقط سازگاری قرارداد و controls را ثابت می‌کند. Gateهای اجرایی آن عمداً PENDING هستند و Target از دامنهٔ غیرقابل‌مسیریابی example.invalid استفاده می‌کند.

## ۳. بررسی‌های معنایی Validator

- تطابق task_id بین Task، Risk، Gate Plan و Brief
- نبود overlap مستقیم میان allowed و forbidden paths
- وجود Evidence requirement برای Gateهای Active و Blocking
- محدودماندن R0 به یک attempt و نبود independent review بی‌دلیل
- وجود Authority و Human Approval gate در R4
- وجود allowlist، prohibited techniques و granted authorization برای Security Scope
- جدا ماندن Security adapter از SAGE core
- تفسیر exit code 2 ابزار Strix به vulnerabilities_found، نه fatal error
- تطبیق Gate Plan هر Fixture با required_gates متناظر در core policy
- اعتبارسنجی مستقل Policyها با sage-policies.schema.json
- اعتبارسنجی کامل descriptorهای Agent، Tool و Provider Adapter
- تطبیق Hash تمام ۳۲ ورودی ثبت‌شده در SOURCE_MANIFEST.json
- حفظ کامل Goal Contract در Runtime Engineering Brief
- آزمون منفی expiry، ترتیب زمانی، مجوز Denied، هم‌پوشانی allow/deny و حذف Gate اجباری
- Hash منابع اصلی، Deltaها و نسخهٔ تاریخی draft.2
- Architecture Model fixture، Architecture Policy و Architecture Schema
- یکتایی Stable ID و resolve شدن endpointهای Relationship
- Reference Runtime semantic loader و Planned↔Observed drift test
- Reference Orchestrator با تصمیم‌های DONE/BLOCKED/ESCALATE
- Workflow State Machine، Evidence Ledger و آزمون transition غیرمجاز
- Ledger پایدار با chain head هش‌شده و CI یکپارچهٔ سه‌گانه
- Production Boundary و Provider/Tool Adapterهای DRY_RUN با CI پنج‌گانه

## ۴. یکپارچگی Source

- ۳۰ فایل در sources/ آرشیو شده‌اند و SOURCE_MANIFEST.json هش ۳۷ منبع/اسنپ‌شات و artifact را ثبت می‌کند.
- نسخهٔ draft.2 پیش از تغییر با Hash اصلی در history/ حفظ شده است.
- Spec Kit به commit 4a7341a93d944d6efe153b71da4a1adb9c2b578c قفل شده است.
- Strix به tag v1.6.2 و commit ff5c8cc8e46d8e60c2bc2439f7bcb07c05ca3db2 قفل شده است.
- PDF اصلی در ۳۳ صفحه Render و بصری بررسی شد؛ نقص خوانایی مشاهده نشد.

## ۵. Hash خروجی‌های اصلی

| Artifact | SHA-256 |
|---|---|
| SAGE_v0.8_EXECUTION_PROTOCOL_AND_SKILL_CONTRACT.md | deeaebf46c344a05ae09198d985ad6678f1351234842539c6fafe5783b2d4c2c |
| SOURCE_REGISTRY.md | 39e5c62e683c7cbf12ce92d26552f03d982b6424ad02d20c78b111e79f40f91f |
| SOURCE_MANIFEST.json | ba5f0179d83a13dd908f856706aeb424182d1ea9a77febc722c8ed4a7a2edf39 |
| schemas/v0.8/sage-contracts.schema.json | ab6dbe7c8be784a954b707d9264b378a932e0b2a34e73f68edcf5bd97b5b9a82 |
| schemas/v0.8/sage-policies.schema.json | ab38029ab3022605731b7f0b9511fc2a0939231aaf4a5f61d6f6f0e47e9bf5b0 |
| policies/v0.8/core-policy.json | dcf2c963facab84fb32f1016deaba18dcd9c6b2d45482ccc2ae6cf947640aa50 |
| policies/v0.8/security-adapter-policy.json | adb04098e794ba239388454b63a5c7063282daa0a56f751ad4a918fd6cc4cae8 |
| schemas/v0.8/sage-architecture.schema.json | 929860da8e19f53c19f45cea5761351904363b6bd0950b6d96e106404a4b8620 |
| policies/v0.8/architecture-policy.json | 354e0c6435510cd4ff65c0c3400f561950101580b6f717d7f7444d238bc6f3d9 |

## ۶. محدودیت‌ها

- Runtime نهایی Orchestrator ساخته نشده است؛ این‌ها reference contracts هستند.
- Reference Runtime حداقلی برای semantic model checks و drift comparison ساخته و آزموده شده است؛ Orchestrator production هنوز خارج از دامنه است.
- کتابخانهٔ Python jsonschema در Runtime بسته‌بندی‌شده موجود نبود و نصب نشد. اعتبارسنجی با Test-Json در PowerShell 7 انجام شد.
- validator فعلی wildcard path containment، canonicalization پیچیدهٔ Target و cryptographic trust را پوشش نمی‌دهد.
- هیچ Skill یا CLI متعلق به Strix توسط این مرحله نصب، تغییر یا اجرا نشده است.
- هیچ scan امنیتی و هیچ اتصال به Target واقعی انجام نشده است.
- وضعیت سند پس از تکمیل independent review و تأیید صریح کاربر به `Formalized Baseline` ارتقا یافت؛ محدودیت‌های Runtime production همچنان برقرار است.
- بازبینی مستقل اولیه انجام شد؛ یافته‌های BLOCKING/HIGH رفع و با اعتبارسنجی مجدد پوشش داده شدند. یک Runtime production هنوز ساخته نشده است.
