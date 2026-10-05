# SAGE v0.8.4 — Agent-Native Interface Formalization

Status: REVIEW_CANDIDATE
Date: 2026-10-06
Approval basis: explicit approval of Agent-Native integration in this task.
Extends: preserved Formalized Baseline v0.8.0 and package v0.8.3.

## ۱. هدف و مرز معماری

این افزوده، مسئولیت API بومی نرم‌افزار، Bridge، CLI، MCP و Skill را رسمی
می‌کند. مسیر ترجیحی دسترسی Agent، استفاده از قابلیت تایپ‌شدهٔ نرم‌افزار است.
Bridge فقط در صورت نیاز به انتقال، thread یا lifecycle جدا اضافه می‌شود؛
CLI و MCP دو سطح مکمل‌اند و وجود هر دو در تمام Taskها اجباری نیست.

Skill روش استفاده را توضیح می‌دهد؛ ابزار قابلیت فراخوانی را عرضه می‌کند.
Discovery فقط پیشنهاد می‌دهد و MUST NOT اختیار، Scope یا Permission تازه بسازد.
اجرای کد دلخواه فقط با Gate صریح و متناسب با Risk مجاز است.

## ۲. قرارداد قابل‌نسخه‌بندی

هر integration MUST منبع قابلیت، نسخهٔ interface، لایه‌ها و محدودیت‌ها،
capabilityها، کلاس اثر جانبی، سیاست امنیت، سازگاری و شواهد آزمون را ثبت کند.
خروجی، خطا و timeout/cancellation MUST semantics قابل‌بررسی داشته باشند.
مرجع ماشین‌خوان: `schemas/v0.8/sage-agent-interface.schema.json`.

استانداردهای حاکم در `docs/architecture/`:

- `agent-native-interfaces.md`: انتخاب interface و مالکیت لایه‌ها؛
- `api-adapter-standard.md`: mapping تایپ‌شده و حفظ Scope/Authority/Evidence؛
- `cli-standard.md`: JSON، help، version، exit code، dry-run و timeout؛
- `mcp-standard.md`: schema تایپ‌شده، initialize، نسخه و قابلیت‌ها؛
- `bridge-standard.md`: transport، lifecycle، thread، reconnect و containment.

## ۳. تصمیم استفادهٔ مجدد

ADOPT: کد موجود با معماری، مجوز، نگهداری، تست و امنیت مناسب استفاده شود.
ADAPT: قابلیت پایه مناسب است و wrapper یا تغییر محدود ارزش استفادهٔ مجدد را حفظ می‌کند.
BUILD: معماری/مجوز/امنیت نامناسب است یا هزینهٔ اصلاح از جایگزینی بیشتر است.
هر تصمیم MUST دلیل و provenance داشته باشد. CLI-Anything منبع روش‌شناختی
با disposition `ADAPT` است؛ وابستگی اجرایی تازه از آن وارد SAGE نمی‌شود.

## ۴. فرمال‌سازی و شرط پایان

ورودی: نیاز Task، descriptor، API/host versions و authority موجود.
خروجی Discovery: candidates معتبر، علت رد موارد نامعتبر، انتخاب پیشنهادی و
`authority_granted=false`. ثبت descriptor تأیید صحت ادعاهای اجرای واقعی نیست.

Integration فقط وقتی DONE است که Source، version و مسئولیت لایه‌ها مشخص،
قرارداد تایپ‌شده و مرز امنیت معتبر، decision ثبت‌شده، راهنمای Skill موجود
و آزمون‌های applicable با receipt قابل‌ردیابی اثبات شده باشند.
برای GUI نرم‌افزار، Headless Contract CI و Host-Application Smoke CI هر دو لازم‌اند.
PASS تست reference یا mock MUST NOT به‌عنوان PASS transport/host واقعی گزارش شود.

## ۵. پیاده‌سازی و پوشش تحویل

Reference module و Discovery، اعتبارسنجی و انتخاب advisory descriptor را اجرا
می‌کنند. production registry، descriptor معتبر را به‌صورت OFFLINE ثبت می‌کند.
سه Skill تخصصی کنار پنج Skill چرخه در Bundle و Registry قرار دارند.
CI این مسیر را با fixtureهای مثبت/منفی و آزمون ثبت/Discovery بررسی می‌کند.

این نسخه server کامل MCP، bridge نرم‌افزار خاص یا distributed agent runtime
عرضه نمی‌کند. اتصال live هر Provider، با آزمون compatibility/transport مستقل
در scope همان integration تکمیل می‌شود. امنیت Strix همچنان Pending است.

## ۶. حفظ تاریخ و مرجع حاکم

نسخه‌های 0.8.0 تا 0.8.3 و Manifest قدیمی محفوظ‌اند. این افزوده و
`RELEASE_MANIFEST_v0.8.4.json` ترکیب فعال را مشخص می‌کنند؛ افزوده دامنهٔ
permission یا approval نسخهٔ پایه را گسترش نمی‌دهد.
