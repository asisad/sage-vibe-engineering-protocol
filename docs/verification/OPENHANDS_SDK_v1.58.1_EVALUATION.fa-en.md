# SAGE — ارزیابی OpenHands SDK 1.58.1

Status: `IN_PROGRESS`, approved 2026-10-24 in the existing SAGE task. Tracking:
https://github.com/asisad/sage-vibe-engineering-protocol/issues/4

## تصمیم ثابت

SAGE مالک انحصاری Runtime، Approval، Scope، Budget، State، Evidence و VERIFY
می‌ماند. موتور پیش‌فرض تغییر نمی‌کند. هیچ برنامه‌ریز، حافظه، کاتالوگ Skill یا
Ledger موازی ساخته نمی‌شود. OpenHands فقط نامزد یک Worker اختیاری است.

## مبنا و ترتیب

- Local verified baseline: `c017f8108a57d711a646c181a5f9ff3e5fdb660a`.
- Remote baseline before synchronization: `73696bb319637ea5ca32a4d65d8f8015e5cbbb56`.
- Sync PR: https://github.com/asisad/sage-vibe-engineering-protocol/pull/5
- Merged baseline: `3c65765ef9c76115cd17d449d7e469739adf336a`.
- Windows/Linux CI passed after canonical-path fixture correction, without changing runtime policy:
  https://github.com/asisad/sage-vibe-engineering-protocol/actions/runs/40119435275
- Real upstream Ruflo smoke passed:
  https://github.com/asisad/sage-vibe-engineering-protocol/actions/runs/40119435165

هش ۱۶۷۴ فایل مبنا، ۷۵۰ منبع Wheel، سه فایل بسته و Ledger/Artifact هر دو Run
قبلی در این بررسی خواندنی تطبیق داده شدند. دو Run موفق بازاجرا نشدند. چهار
فایل پذیرش تازهٔ GitHub نیز در Merge حفظ شدند. فایل‌های پذیرش تاریخی بازنویسی
نمی‌شوند؛ گزارش قدیمی فقط نتیجهٔ همان تحویل را توصیف می‌کند.

## طرح آزمایش تأییدشده

سه مسیر: Direct Codex، SAGE + Ruflo + Codex، SAGE + OpenHands. دو نمونهٔ
قبلی Unicode slug و اصلاح division دوباره برای مسیرهای فاقد شاهد استفاده
می‌شوند؛ نتایج قبلی Ruflo یک مبنای **تاریخی** هستند، نه مقایسهٔ هم‌زمانِ کاملاً
کنترل‌شده. یک تغییر کوچک در ابزار تأیید همین مخزن، روی کپی‌های جدا، برای مقایسهٔ
جدید استفاده خواهد شد. Prompt مشترک، مدل درخواستی، نسخه، منابع، سقف زمان،
اختلاف system prompt و ابزارها در Receipt ثبت می‌شوند.

سقف جدید: ۳۰ Job مدل برای **کل ارزیابی** و ۹۰۰ ثانیه برای هر Run؛ تلاش ناموفق
هم رزرو می‌شود. بودجهٔ قبلی ۶/۱۲ دست‌نخورده می‌ماند. همان DeliveryBudget موجود
برای ارزیابی استفاده می‌شود؛ سقف پیش‌فرض قدیمی همچنان ۱۲ است. هزینهٔ API پولی
مجاز نیست؛ ورود جداگانهٔ اشتراک OpenHands ممکن است لازم باشد.

کد آزمودنی فقط در فضای disposable و بدون شبکه/اعتبارنامه اجرا می‌شود. SDK
آزمایشی وابستگی اجباری SAGE نیست. مدل حق خواندن Home، تنظیمات میزبان، socket
داکر یا فایل‌های SAGE را ندارد. پاسخ موفق موتور، نتیجهٔ تست، یا `finished`
به‌تنهایی DONE نیست؛ پذیرش نهایی با گیت مستقل SAGE و هش سورس انجام می‌شود.

## معیار تصمیم

صحت و آزمون مستقل، زمان، مصرف گزارش‌شده، RAM/CPU، توقف/ادامه، بازیابی خطا،
Scope و Workspace بررسی می‌شوند. معیارها باید پیش از انتخاب موتور خوانده
شوند؛ سرعتِ بیشتر با مدل یا Prompt متفاوت برتری موتور تلقی نمی‌شود. دادهٔ
ناموجود `NOT_VERIFIED` می‌ماند. ایمنیِ پایه شرط لازم است و با سرعت معاوضه نمی‌شود.

پذیرش دائمی فقط با فایدهٔ کاربردیِ اندازه‌گیری‌شده و Adapter کوچکِ سازگار مجاز
است؛ آن هم با Feature Flag پیش‌فرض خاموش و استفاده از گیت‌های موجود. اگر فایده
اثبات نشود، فقط نتیجهٔ بررسی ثبت می‌شود و وابستگی یا موتور دائمی اضافه نمی‌شود.

## منابع اولیه

- https://github.com/OpenHands/software-agent-sdk/tree/v1.58.1
- https://github.com/OpenHands/software-agent-sdk/releases/tag/v1.58.1
- https://pypi.org/project/openhands-sdk/1.58.1/
- https://docs.openhands.dev/sdk
- https://docs.openhands.dev/sdk/guides/llm-subscriptions
- https://docs.openhands.dev/sdk/guides/agent-server/docker-sandbox
- https://docs.openhands.dev/sdk/guides/convo-persistence
- https://docs.openhands.dev/sdk/guides/metrics

Latest web documentation may drift from the pinned release. Installed source
and version-specific tests are the implementation reference. Documentation
claims are not scored as observed SAGE runtime evidence.
