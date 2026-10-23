# SAGE — گزارش پذیرش اجراگر خودکار / Runtime acceptance

تاریخ محلی: **۲۰۲۶/۱۰/۲۴**. بستهٔ افزوده: `sage-runtime 0.1.0`؛ هستهٔ
`SAGE 0.8.4` و برچسب‌های تاریخی تغییر نکردند. این گزارش پذیرش محلی است، نه
انتشار عمومی، تضمین ساخت هر نرم‌افزار یا گواهی امنیت.

## نتیجه / Outcome

چرخهٔ واقعی «ایده ← فهم نیاز ← انتخاب منابع SAGE/ECC ← طرح و دیاگرام ←
تولید فایل مجاز ← آزمون ایزوله ← بازبینی مستقل ← تحویل مستند» روی دو نمونهٔ
کوچک Python تأیید شد. اصلاح محدود، پاسخ به ابهام، لغو، کنترل مسیر و بازیابی
پس از قطع نیز آزمون‌های تزریق خطای مستقل دارند.

| بررسی | نتیجهٔ مشاهده‌شده |
| --- | --- |
| ساخت کتابخانهٔ Unicode/Persian slug | `DONE`؛ ۳ آزمون پروژه + ۲ آزمون مستقل؛ بازبینی پذیرفته شد |
| توقف و ادامه | توقف پس از طرح و ادامه در فرایند تازه؛ فقط یک فراخوانی Planner در اجرای موفق |
| اصلاح خطای تقسیم در کپی تازه | شکست واقعی آزمونِ اصل؛ سپس `DONE` با ۵ آزمون پروژه + ۲ آزمون مستقل |
| حفظ اصل پروژه | هش فایل‌های اصل، قبل و بعد یکسان |
| آزمون‌های اجراگر | ۱۶۲ مورد، بدون خطا؛ ۱ مورد به‌علت مجوز ساخت Symlink ویندوز اجرا نشد |
| کنترل‌های قدیمی SAGE | هر ۱۹ کنترل محلی موفق |
| منابع ECC | ۴۲۵ تعریف و ۱۳۷۵ فایل معتبر؛ ۳۱ آزمون مرزی با ۱ Skip و ۶ آزمون یکپارچگی موفق |
| محیط واقعی Docker | ۶ سناریو؛ موفقیت، شکست واقعی، جعل نتیجه، مرز دسترسی، Timeout و لغو |

هر مرحلهٔ مدل در نشست تازهٔ Codex CLI نسخهٔ `0.163.0` اجرا شد؛ مدل ابزاری
اجرا نکرد. فقط کنترل‌کننده فایل می‌نویسد و آزمون‌ها در Docker بدون شبکه،
دسترسی نوشتن به منبع، حساب مدل یا دسترسی ریشه اجرا شدند. بازبینی جداگانه به
معنای مدل یا انسان متفاوت نیست. آزمون مستقل به همان هش منبع متصل است؛ صرف
وجود `DONE` یا نظر مدل کافی نیست.

در تحویل، **۱۲ رزرو از سقف ۱۲ نوبت** مصرف شد: ۶ تلاشِ متوقف‌شده هنگام
آماده‌سازی/تشخیص پیام آغازین و ۶ فراخوانی در دو اجرای موفق. تلاش ناموفق بازپرداخت
نشد و مجوزی برای فراخوانی اضافه ایجاد نشد. سقف، تعداد اجرای کنترل‌کننده است؛
تعداد درخواست‌های HTTP داخلی یا سقف مبلغ حساب را تضمین نمی‌کند.

حلقهٔ اصلاحِ پس از پیاده‌سازی در دو نمونهٔ موفق لازم نشد؛ مسیر آن با آزمون‌های
آفلاینِ دارای شکست عمدی تأیید شده است. این دو نوع مدرک عمداً یکی نامیده نمی‌شوند.

## استفاده و مرزها / Usage and limits

راهنمای نصب و فرمان‌ها: [فارسی/انگلیسی](../runtime/autonomous/README.fa-en.md).
معماری: [افزودهٔ اجراگر](../SAGE_AUTONOMOUS_RUNTIME_DELTA.md).
رسید عمومیِ بدون محتوای خصوصی: [acceptance.json](../extensions/autonomous-runtime/acceptance.json).

نمایهٔ **Python استاندارد** روی این میزبان، پذیرش زندهٔ کامل دارد. نمایه‌های
Node و وب ایستا تعریف شده‌اند، اما پذیرش زندهٔ سرتاسری آن‌ها در این تحویل ادعا
نمی‌شود. Docker فعلی فقط Python و وب ایستا را بررسی می‌کند؛ Node به محیط بومی
تأییدشده نیاز دارد. محیط بومی `mxc` این دستگاه مسدود است و جایگزینِ بدون ایزوله ندارد.

خروجی بسته‌بندی و هش‌ها در `tmp/autonomy-final-20261024/packaging-acceptance.json`
ثبت شده است؛ ساخت Wheel و Sdist، بازسازی مستقل از Sdist، نصب بیرون مخزن و
خواندن همان دو اجرای موفق با CLI نصب‌شده تأیید شدند. این مسیر محلی و Git-ignored است.
منابع همراه بسته، تعریف و راهنمای
تخصص‌اند؛ نصب بسته، صدها عامل یا Hook خارجی را فعال نمی‌کند.

این کار فقط روی شاخهٔ توسعهٔ محلی انجام شد؛ GitHub Push، Tag/Release تازه،
نصب وابستگی پروژه‌های تولیدی، استقرار و اسکن Strix انجام نشدند.

کنترل نسخهٔ تمیز، تفاوت پایان‌خط ۹ فایل قدیمی Strix را مشخص کرد؛ فقط پایان‌خط
با بایت‌های ثبت‌شدهٔ گیت یکسان شد و متن/رفتار تغییر نکرد. نسخهٔ محلی قبلی در
`tmp/autonomy-original-strix-eol/` حفظ شد. همچنین آزمون قفل فرایند ویندوز اصلاح
شد تا به‌جای واسط محیط مجازی، مالک واقعی قفل را متوقف و PID آن را بررسی کند؛
رفتار قفلِ اجراگر تغییر نکرد. این مورد در دو محیط، هرکدام ۲۰ بار موفق آزموده شد.

## English summary

Two actual authorized Python workflows reached `DONE`: a generated Unicode slug
library and a repaired copy of a defective division project. Fixed project tests
and controller-authored external oracles ran inside hardened local Docker;
fresh-session reviews accepted the current source hashes. A plan checkpoint was
resumed in a new process without replanning. Original repair inputs were unchanged.

Offline runtime regression: **162 tests, zero failures/errors, one Windows
symlink-permission skip**. All 19 existing local SAGE CI checks passed. Real Docker
transport cases and offline injected-failure regressions are separate from the
two live model workflows. The 12-slot delivery budget includes all six earlier
stopped bootstrap/notice-validation attempts; no hidden refund or extra call.

This is bounded local reference acceptance, not universal correctness, a hosted
production deployment, an independently different reviewer model, a complete
live Strix assessment, or evidence that GitHub CI ran. Historical SDK/tags remain
unchanged. See the machine-readable receipt for run IDs and delivery/oracle hashes.
