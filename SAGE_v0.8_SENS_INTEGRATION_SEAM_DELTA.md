# SAGE — SENS Integration Seam 0.1

Date: 2026-10-14 (Asia/Tehran).
Status: approved source-branch addition; no new core release or SENS deployment.
Replaces: nothing. SENS implementation remains an independent project.

## ۱) محل و مسئولیت

`integrations/sens/` جایگاه رسمی معرفی و اتصال بعدی SENS در مخزن SAGE است.
قرارداد، Schema، تنظیمات نمونه، محل ثبت معرفی، رویداد/یافتهٔ نمونه و راهنمای
پیوستن در همان‌جا قرار دارند. کد پروژهٔ SENS به این مخزن منتقل نمی‌شود.
مخزن یا endpoint واقعی SENS هنوز ارائه نشده؛ مقدار null عمداً حفظ شده است.

## ۲) قراردادهای هنجاری

۱. معرفی SENS فقط `PROPOSED` و `OBSERVATION_ONLY` است؛ ثبت فایل، Commit یا
وجود capability، مجوز نصب، فعال‌سازی، اجرای دستور یا تصویب تغییر ایجاد نمی‌کند.
Registry در این نسخه صرفاً محل Proposal است و active instance ندارد.

۲. حالت پیش‌فرض `DISABLED` است. `PREVIEW_ONLY` صرفاً metadata را در حافظه
بررسی می‌کند. این افزوده HTTP sender/receiver، daemon، صف پایدار، سرویس SENS،
credential resolution یا استقرار ندارد. GitHub محل نگهداری این سورس است،
نه مدرک اجرای سرویس SENS.

۳. خروجی SAGE -> SENS فقط فیلدهای metadata در Schema، Project مجاز، شناسه‌های
ارتباط، Revision، وضعیت و ارجاع شواهد است. raw payload، کد، Prompt، credential
و exploit payload در این کانال عمومی مجاز نیست. بررسی الگوهای شناخته‌شدهٔ
کلید، جایگزین حفاظت کامل داده یا DLP در emitter/receiver واقعی نیست.

۴. Preview محدودیت بایت UTF-8، Project allowlist، تکرار شناسه و ظرفیت batch/
queue را بررسی می‌کند و حداکثر ۲۵۶ ورودی را با جزئیات پردازش می‌کند. rate
window و retention زمانی فقط الزام آداپتور آینده‌اند، نه رفتار پیاده‌شده.

۵. یافتهٔ SENS فقط `OBSERVED` و دارای provenance/uncertainty است. Project،
Task، Revision و SENS ID باید در Context مستقل SAGE تطبیق داده شوند؛ حتی
پس از آن، یافته صرفاً پیشنهاد بازبینی است و صحت Evidence یا تصویب را ثابت
نمی‌کند. هیچ دستور یا اصلاحی از payload اجرا نمی‌شود.

۶. خرابی یا اشباع پایش اختیاری می‌تواند به drop منجر شود. Scope، Approval،
Security، Evidence اجباری و Ledger محلی هرگز با قطع SENS bypass نمی‌شوند.
اختیار معماری و تغییرات در SAGE باقی می‌ماند.

۷. اتصال واقعی نیازمند تغییر مستقلِ بازبینی‌شده با endpoint/auth، Scope،
بودجه، timeout/retry/cancellation، redaction، تست مستقل و disable/rollback است.
SENS می‌تواند معرفی و کد سازگار پیشنهاد دهد، اما hook خودفعال‌ساز ندارد.

## ۳) پیاده‌سازی و معیار پذیرش

- `integrations/sens/schemas/sage-sens.schema.json`: registration, registry,
  config, event and finding records.
- `integrations/sens/SageSens.psm1`: offline validation/context checks and preview.
- `sage.ps1 sens`: slot status; optional record validation/local preview.
- `tools/Test-SageSensIntegration.ps1`: positive and adverse offline cases.
- `integrations/sens/docs/CONNECTING_SENS.fa-en.md`: handoff to the independent
  SENS repository, including what is intentionally not implemented.

The existing SAGE -> SENS conceptual event contract is preserved and narrowed
to this versioned metadata seam. This is not a replacement SENS architecture,
an enabled transport, a cryptographic trust protocol or a safety certification.
Source Push includes the separately approved technology-engineering extension;
published v0.8.4 manifests/tags and the pending Strix status are preserved.
