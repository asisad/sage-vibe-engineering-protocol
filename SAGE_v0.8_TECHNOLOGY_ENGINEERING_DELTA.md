# SAGE — Technology Engineering Extension 0.1

Date: 2026-10-14 (Asia/Tehran).
Status: user-approved source-branch extension; not a new published core release.
Base: preserved SAGE v0.8 baseline and v0.8.4 Agent-Native package.
Replaces: nothing. Architecture and approval authority remain in SAGE.

## ۱) هدف و مرز

SAGE باید پیش از تصمیم مهم پیاده‌سازی، زبان، Runtime، Framework و ساختار
مناسب را با توجه به نیاز پروژه انتخاب و دلیل آن را ثبت کند. معیار، تسلط
ادعایی مدل یا محبوبیت فناوری نیست؛ نیاز، محدودیت، هزینهٔ نگهداری و شواهد است.
این افزوده، Council شرطی نسخهٔ ۷ و Dynamic Role Routing نسخهٔ ۰٫۸٫۱ را
عملی‌تر می‌کند؛ نقش جدیدی بر قانون اساسی حاکم نمی‌شود.

این نسخه قرارداد، پروفایل و رفتار مرجع قابل‌آزمون را فراهم می‌کند؛ نه تیم
خودکار مستقر، همهٔ کامپایلرها، اتصال واقعی SENS یا تضمین ساخت هر نرم‌افزار.
نسخه و Tag منتشرشدهٔ v0.8.4، SDK و هشت Skill هسته تغییر نسخه نمی‌دهند.
این افزوده برای شاخهٔ اصلی آماده شده و در Tag منتشرشدهٔ v0.8.4 نیست؛
Push سورس با انتشار نسخهٔ جدید یا راه‌اندازی تیم اجرایی تفاوت دارد.

## ۲) قواعد هنجاری

۱. در پروژهٔ جدید، تغییر مهم فناوری یا افزودن زبان، یک تصمیم فناوری به
مراحل DISCOVER/PLAN پیوند می‌خورد؛ اصلاح جزئی در پشتهٔ مصوب چنین باری ندارد.

۲. پشتهٔ مناسب فعلی یکی از گزینه‌هاست. Rust-first، تیم ثابت P0، چندزبانه‌سازی
و Microservice پیش‌فرض نیستند. تک‌گزینه بودن به دلیل الزام محیط مجاز است،
به شرط ثبت علت؛ گزینهٔ ساختگی برای پرکردن جدول تولید نمی‌شود.

۳. محدودیت‌های قطعی قبل از ترجیح‌ها بررسی می‌شوند. نتیجهٔ UNKNOWN یا
UNSATISFIED در محدودیت اجباریِ گزینهٔ منتخب، بررسی برنامه را متوقف می‌کند.
برای گزینه‌ها tradeoff و منابع نسخه‌دار ثبت می‌شود، نه امتیاز علمیِ ساختگی.

۴. زبان اضافه به هزینهٔ نگهداری، استقرار و ارتباط بین‌زبانی دلیل روشن و
برنامهٔ آزمون سازگاری نیاز دارد. ادعای عملکرد اندازه‌گیری‌شده به receipt
Benchmark و artifact با هش معتبر برای همان Candidate/Revision نیاز دارد.

۵. Task ID، Component ID، نسخهٔ مدل معماری، Revision، شواهد، گزینه‌ها و
برنامهٔ اعتبارسنجی به هم متصل‌اند. View دیاگرام از همین تصمیم تولید می‌شود؛
تصویر یا خروجی AI مرجع تأیید نیست. پیوند مدل فقط در صورت ارائهٔ مدل بررسی
می‌شود؛ NOT_CHECKED به معنی تأیید مدل نیست.

۶. ۱۷ پروفایل و ۱۸ Skill افزونه برحسب نیاز route می‌شوند؛ شمار نقش‌ها معیار
کیفیت نیست. پروفایل، Agent اجراشده یا مدرک تخصص نیست. زبان گزینهٔ منتخب باید
با پروفایل‌های routeشده پوشش داده شود؛ قابلیت ناشناخته جایگزین حدسی نمی‌شود.

۷. PLAN می‌تواند پیشنهاد ساختارمند با تست‌های NOT RUN داشته باشد. VERIFY
تست اجباری اجرا‌نشده/ناموفق، receipt غایب یا تغییرکرده، Revision نامرتبط و
Fixture مصنوعی را به‌عنوان مدرک پروژه رد می‌کند. تطابق هش، صحت ادعای اجرای
کامپایلر را اثبات نمی‌کند؛ review مستقل و receipt اجرایی معتبر همچنان لازم است.

۸. `READY_FOR_REVIEW` مجوز اجرا یا تصویب تصمیم نیست. اجرای واقعی، نصب ابزار،
Flash، حرکت دستگاه، IaC apply، استقرار و انتشار همچنان مجوز مختص خود می‌خواهند.

۹. SENS فقط مشاهده و پیشنهاد می‌دهد. قطع Telemetry اختیاری می‌تواند fail-open
باشد؛ مجوز، Scope، Safety و شواهد اجباری fail-closed می‌مانند. این افزوده
مالکیت UEG/CMDB یا مرز مخازن دیگر را جابه‌جا نمی‌کند.

## ۳) قرارداد و رفتار مرجع

- Schema: `schemas/extensions/sage-technology-engineering.schema.json`
- Optional package: `extensions/technology-engineering/manifest.json`
- Specialist catalog and policy: `specialists.json` / `policy.json` in that package.
- Runtime: `runtime/reference/SageTechnologyEngineering.psm1`
- DISCOVER: `Find-SageEngineeringCapabilities` returns declared on-demand profiles.
- PLAN: optional `TechnologyDecision` / `RequireTechnologyDecision` on the
  lifecycle performs advisory review, task/language routing checks and records
  the serialized decision hash in the Evidence Ledger. Five lifecycle stages
  are preserved. No tool, specialist process or external service is started.
- Validation: `tools/Test-SageTechnologyEngineering.ps1`; three synthetic
  scenarios cover stack preservation, a browser integration and a constrained
  engine interface. These are reference tests, not three shipped applications.

## ۴) Workflow / جریان

```text
Intent -> Intake/constraints -> Discover feasible options + specialist profiles
       -> Technology decision + architecture/flow view -> Review/approval
       -> Scoped implementation -> Build/test/compatibility/benchmark as needed
       -> Independent verification + evidence -> Done / Blocked / Escalated
```

The language/domain Skill Pack is adapted from the supplied v0.2 templates,
not installed into a host. Its AGENTS.md is preserved only inside the source
ZIP and has not replaced repository/user instructions. Sources and original
hashes are recorded in SOURCE_REGISTRY and SOURCE_MANIFEST. Method references
are listed in the extension's specialist contract; this is an adaptation of
tradeoff/ADR principles, not a full ATAM evaluation or external certification.
