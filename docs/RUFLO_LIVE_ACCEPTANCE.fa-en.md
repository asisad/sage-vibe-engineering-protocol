# گزارش پذیرش SAGE × Ruflo — 2026-10-24

**نتیجهٔ اجرایی:** دو گردش‌کار واقعیِ ساخت و اصلاح، با هماهنگی Ruflo و عامل‌های
Codex زیر اختیار SAGE، به `DONE` رسیدند. این افزونهٔ توسعهٔ `sage-runtime 0.2.0`
برای هستهٔ `0.8.4` است؛ نسخهٔ تاریخی هسته بازنویسی نشده است.

## چه چیزی واقعاً اجرا شد؟

| مورد | مشاهده و مدرک |
|---|---|
| ساخت کتابخانهٔ تبدیل متن به slug | متن فارسی و Unicode؛ ۴ آزمون پروژه + ۲ آزمون مستقل؛ بازبینی پذیرفته شد |
| اصلاح تقسیم اشتباه در پروژهٔ نمونه | خرابی اولیه ثابت شد؛ ۵ آزمون پروژه + ۲ آزمون مستقل؛ اصل پروژه بدون تغییر |
| توقف و ادامه | پس از PLAN در فرایندی تازه ادامه یافت؛ برنامه دوباره تولید نشد |
| هماهنگی واقعی Ruflo | شش Task واقعی؛ تأیید تخصیص پیش از مدل و بازخوانی نتیجه از MCP تازه و فایل مستقل |
| بازیابی metadata نیمه‌تمام | Task متعلق به همان Run در فرایندی تازه شناسایی و لغو شد؛ بدون فراخوانی مدل |
| محیط Ruflo | نسخهٔ ثابت `3.61.1` در Docker، بدون شبکه و root؛ فقط metadata همان Run قابل‌نوشتن |
| بودجه | ۶ Job واقعی از سقف تأییدشدهٔ ۱۲؛ هیچ رزروی حذف یا بازنشانی نشد |
| رگرسیون Runtime | ۱۷۹ مورد، صفر خطا و شکست؛ یک مورد symlink به‌علت مجوز حساب ویندوز اجرا نشد |
| مرز MCP قدیمی | ۲۲ آزمون موفق؛ شواهد آفلاین از اجرای زنده جدا هستند |
| بررسی اصلی هسته | هر ۱۹ اسکریپت CI در کپی تمیز محلی موفق؛ CI جدید در GitHub اجرا نشده است |
| کاتالوگ ECC | ۴۲۵ تعریف و ۱۳۷۵ فایل بررسی شدند؛ ۳۱ آزمون مرزی با یک skip و ۶ آزمون یکپارچگی موفق |
| بستهٔ نصب | Wheel و sdist ساخته شدند؛ بازسازی مستقل از sdist همان محتوای Wheel را تولید کرد |
| نصب مستقل | نصب کپی‌شده بیرون از مخزن؛ ۷۵۰ منبع و ۱۲ ماژول بررسی شدند؛ اتصال واقعی Ruflo و بازخوانی دو DONE موفق |

شناسه‌ها، هش خروجی، ایمیج و Lockfile در
[مدرک ماشین‌خوان](../extensions/ruflo/live-acceptance.json) ثبت شده‌اند.
راهنمای نصب، استفاده و نمودار مسیر در
[راهنمای دوزبانه](../extensions/ruflo/LIVE_BINDING.fa-en.md) قرار دارد.

بسته‌های باینری فعلاً محلی‌اند و در GitHub یا PyPI منتشر نشده‌اند:

| فایل | SHA256 |
|---|---|
| `sage_runtime-0.2.0-py3-none-any.whl` | `5a95426663d315c4779b36838e73d6ccb18a15a7db2719e450f81736ff6d385e` |
| `sage_runtime-0.2.0.tar.gz` | `ae3991077c855f56632c24195945c6494d110afda91242f6ff2d271e9434fd3f` |

برای ساخت آرشیو سورس در ویندوز باید از مسیر کوتاه استفاده شود؛ ساخت از مسیر
طولانی موقت به محدودیت مسیر برخورد کرد و از کپی تمیز با مسیر کوتاه موفق شد.
نصب Wheel به این کپیِ سورس وابسته نیست. هش خود فایل ZIP بازسازی‌شده ممکن است
به‌علت زمان‌های داخل آرشیو فرق کند؛ محتوای تک‌تک فایل‌های دو Wheel یکسان بود.

## مرز نتیجه

این مسیر **Worker خارجی SAGE/Codex** است. اجرای داخلی LLM در Ruflo، swarm
توزیع‌شده، Hookها، یادگیری حافظه و همهٔ ۸۶۳ تعریف کاتالوگ فعال نشده‌اند.
Ruflo فقط metadata و هش پاسخ معتبر مدل را دریافت می‌کند؛ کد، prompt و
اعتبارنامهٔ حساب وارد آن نمی‌شوند. `completed` صف، پذیرش محصول نیست؛ SAGE پس
از بررسی Scope، آزمون واقعی و بازبینی جداگانه تصمیم `DONE` می‌گیرد.

پذیرش زندهٔ این تحویل محدود به نمونه‌های Python است. تست‌های آفلاین برای
سایر بخش‌ها معادل اجرای زندهٔ همهٔ زبان‌ها و ابزارها نیستند. بازبینی در نشست
تازهٔ مدل انجام شده است؛ بازبینی انسانی یا Provider متفاوت محسوب نمی‌شود.
این کار گواهی امنیت یا production نیست؛ Push، Release جدید و اسکن Strix در
این دامنه انجام نشده‌اند.

## English record

Two real local Python workflows passed: a Unicode slug library build and repair
of an independently verified division defect in a new output copy. Each used
three actual Codex jobs coordinated by real pinned Ruflo MCP tasks. Every
successful response has a matching task result and independent persisted
readback; SAGE's separate source/test/review gates grant product acceptance.
Plan pause/resume and interrupted metadata reconciliation were verified. This
proves the controlled external-worker binding, not native Ruflo `agent_execute`,
every catalog capability, security certification or production readiness.
No GitHub publication was performed in this delivery.
