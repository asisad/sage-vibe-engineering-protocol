# SAGE × Ruflo — اتصال اجرایی MCP (FA / EN)

**تاریخ:** 2026-10-24 · **نسخه افزونه:** 0.1.0 · **Core سازگار:** SAGE 0.8.4

## نتیجه و حدود ادغام
این افزونه یک MCP Client واقعی برای Ruflo می‌افزاید؛ بر خلاف کاتالوگ ECC، امکان برقراری اتصال STDIO، مذاکره پروتکل، دریافت فهرست ابزارها و فراخوانی ابزار تحت مجوز محدود را دارد. ابزارها به‌صورت زنده از Ruflo شناسایی می‌شوند؛ شمار و کارکردشان از روی نام مخزن فرض نمی‌شود. SAGE مالک task، مجوز، scope، تأیید و شواهد می‌ماند.

**توجه:** ثبت کد در GitHub به معنی نصب روی ویندوز، وجود کلید مدل، تکمیل آزمون مستقل اجرای Agentها یا استقرار وب نیست. نصب npm، hooks، daemon، console و افزونه Claude Code به‌صورت خودکار انجام نمی‌شوند. اجرای واقعی نیازمند محیط میزبان آماده است.

## مرز معماری
SAGE intake/plan/approved TaskPacket → Ruflo MCP adapter → Ruflo tools → SAGE evidence + independent verify.

- ECC مهارت و منابع می‌دهد؛ Ruflo موتور اجرایی اختیاری است؛ SENS فقط مشاهده‌گر است.
- مالکیت approval با قرارداد SAGE است، نه annotations ابزار MCP یا دستورهای داخل فایل‌های upstream.
- پیش‌فرض صرفاً status آفلاین است؛ برای اتصال --live الزامی است. Discovery خودش مجوز tools/call نیست.
- فراخوانی ابزار نیازمند Approval منقضی‌نشده، شناسه یکسان، allowlist دقیق ابزار و workspace مشخص است.
- ابزارهای خارج از allowlist محلی READ_ONLY، mutating/unknown تلقی می‌شوند. برایشان --allow-mutation و --ack-host-access و run contract اصلیِ SAGE با gateهای PASS لازم است.
- **این آداپتور OS sandbox نیست.** حتی یک ابزار نام‌گذاری‌شده read-only ممکن است در سرور ثالث side effect داشته باشد. برای mutation فقط از محیط ایزوله و worktree قابل‌دورریختن و حساب با حداقل مجوز استفاده کن.
- دسترسی Ruflo از کاربری که آن را اجرا می‌کند گرفته می‌شود. ادغام SAGE مجوز شبکه/فایل را در سطح سیستم‌عامل محدود نمی‌کند.
- EXECUTED_UNVERIFIED یعنی فراخوانی MCP انجام شده، **نه** اینکه ویژگی نرم‌افزاری ساخته یا آزمون پذیرش مستقل پاس شده باشد. synthetic=true و isError=true به BLOCKED تبدیل می‌شوند.
- آرگومان‌های دارای رمز و کلیدها در receipt نوشته نمی‌شوند؛ هش پاسخ ثبت می‌شود.

## نسخه و نصب مستقل
منبع upstream: https://github.com/ruvnet/ruflo
Release: https://github.com/ruvnet/ruflo/releases/tag/v3.61.1
- Git tag commit: e6c3743ef1977b2cfa562210316ac8fd026139c4
- npm: ruflo@3.61.1؛ Node.js 20+ و Python 3.11+.
- شاخه main در هنگام بررسی جلوتر از release بود؛ اصلاحات آن را به بسته نصب‌شده نسبت ندهید.
- فرمان پیش‌فرض آداپتور: npx --no-install ruflo@3.61.1 mcp start؛ بنابراین بسته گمشده به‌طور خودکار دانلود نمی‌شود.

در یک **workspace آزمایشی جدا از مخزن اصلی** (نه پوشه سورس SAGE) که مجاز به تغییر آن هستی:
1. Node.js 20+ و Python 3.11+ را بررسی کن.
2. در همان workspace آزمایشی، npm install --save-dev --save-exact ruflo@3.61.1 را اجرا کن.
3. سپس از ریشه SAGE، مسیر واقعی workspace را بده.

فرمان‌های مستقیم:

    python extensions/ruflo/sage_ruflo.py status
    python extensions/ruflo/sage_ruflo.py probe --workspace /ABSOLUTE/SAFE/WORKTREE --live
    python extensions/ruflo/sage_ruflo.py list --workspace /ABSOLUTE/SAFE/WORKTREE --live

در Windows PowerShell 7 (از ریشه SAGE):

    .\sage.ps1 ruflo -RufloAction status
    .\sage.ps1 ruflo -RufloAction probe -RufloWorkspace 'C:\temp\safe-worktree' -RufloLive

## اجرای یک ابزار با Approval
از قالب examples/approval.template.json استفاده کن.
- workspace_root مسیر مطلق واقعی workspace باشد، بدون symlink و بدون .. .
- authority.status=GRANTED فقط وقتی به‌وسیله مالک اختیار و کار مشخص تأیید شده باشد.
- approval_id، task_id، scope و allowlist باید با درخواست مورد نظر هماهنگ باشد.
- expires_at آینده و timezoneدار باشد؛ max_timeout_seconds بین ۱ تا ۳۰۰.
- برای mutation باید authority.scope با task_packet.authority.scope و allowed_paths در run-contract تطبیق داشته باشد؛ "." برای mutation در قرارداد اصلی مجاز نیست.

مثال READ_ONLY، فقط پس از کشف نام واقعی ابزار و ثبت approval:

    python extensions/ruflo/sage_ruflo.py invoke --workspace /ABSOLUTE/SAFE/WORKTREE --live --tool memory_search --args-json '{"query":"SAGE"}' --approval-file /ABSOLUTE/APPROVAL.json

مثال MUTATING در worktree قابل‌دورریختن و محیط جداشده:

    python extensions/ruflo/sage_ruflo.py invoke --workspace /ABSOLUTE/ISOLATED/WORKTREE --live --tool TOOL_FROM_DISCOVERY --args-json '{}' --approval-file /ABSOLUTE/APPROVAL.json --run-contract /ABSOLUTE/APPROVED_SAGE_RUN.json --allow-mutation --ack-host-access

این فرمان صرفاً روش فراخوانی مجاز است؛ نام فرضی TOOL_FROM_DISCOVERY و سند نمونه برای اجرای واقعی کافی نیستند. مدل، اعتبارنامه و ابزارها باید روی میزبان موجود باشند. ack-host-access اثبات sandbox نیست.

برای کلید مدل، آن را فقط در environment تنظیم کرده و نام متغیر را با --pass-env ANTHROPIC_API_KEY یا یکی از نام‌های مجاز صراحتاً انتخاب کن. مقدار کلید را در JSON، مخزن یا Approval ننویس.

## قرارداد اجرای واقعی و رسید
فراخوانی شامل JSON-RPC initialize → notifications/initialized → tools/list → tools/call با پیشنهاد نسخه 2025-11-25 و پذیرش نسخه‌های مشخص 2024-11-05 یا 2025-11-25 است. ناسازگاری نسخه، نبود ابزار، خطا، timeout و عدم مطابقت شناسه fail-closed می‌شود. هر اتصال/فراخوانی receipt دارای نسخه upstream، mode، شناسه تأیید، هش قرارداد SAGE، هش پاسخ، زمان و وضعیت verification می‌سازد:

    <workspace>/.sage/ruflo-receipts/ruflo.<uuid>.json

Receipt رکورد دارای هش است؛ به‌تنهایی امضای دیجیتال یا تضمین عدم تغییر در برابر فرد دارای دسترسی نوشتن نیست. برای حسابرسی قوی آن را با سیستم شواهد SAGE و ذخیره کنترل‌شده پیوند بده.

## آزمون و تأیید
- python tools/test_sage_ruflo.py : آزمون واقعی انتقال JSON-RPC در فرآیند مجزا با سرور ساختگی؛ handshake، انقضا، scope، allowlist، synthetic، خطا و timeout. این آزمون به upstream یا کلید مدل نیاز ندارد.
- sage.ps1 ruflo -RufloAction status : تأیید عدم فعال‌سازی پیش‌فرض.
- probe روی میزبان با Ruflo واقعی و receipt دارای نسخه و فهرست ابزارها: شرط اثبات اتصال واقعی.
- یک کار کدنویسی کوچک در محیط ایزوله، با شواهد diff + اجرای مستقل تست: شرط اثبات کارکرد Agent. agent_spawn یا پاسخ success به‌تنهایی کافی نیست.
- مقایسه موتور مستقیم، Ruflo و OpenHands SDK با سناریو و بودجه یکسان ضروری است؛ موتور پیش‌فرض تحمیل نمی‌شود.

## English operational summary
SAGE adds an optional, version-pinned, real MCP stdio client to Ruflo, with separate per-task authority, strict tool allowlists, timeouts, receipts, and a native SAGE run-contract gate for possible mutations. It does not install Ruflo in the host, initialize Claude Code hooks, start daemons, alter global configuration, or certify autonomous code-writing workflows. Upstream MCP tools can have broader OS permissions than this adapter can enforce: use external isolation and independent verification. The existing SAGE DRY_RUN production adapter is unchanged.


بسته npm Ruflo 3.61.1 در آزمون اولیه GitHub پروتکل 2024-11-05 را برگرداند؛ تفاوت نسخه‌های کد upstream و خروجی بسته باید در رسید مذاکره ثبت شود. پذیرش فقط همین نسخه‌های مشخص مجاز است.
