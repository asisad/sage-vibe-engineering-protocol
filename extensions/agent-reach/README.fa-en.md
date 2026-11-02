# Agent Reach Research Adapter — افزونهٔ مشترک SAGE / Deep Research

نسخهٔ توسعه: `sage-agent-reach/0.1`. این افزونه مستقل از هستهٔ SAGE است و فایل‌های Agent Reach را تغییر نمی‌دهد. برای استفاده روی Windows، Python 3.11+ و `agent-reach 1.6.0` نصب‌شده روی PATH لازم است. وابستگی Python دیگری ندارد.

## نتیجه و محدودیت اثبات

- مسیر مشترک: `SAGE یا Deep Research → sage_agent_reach.py → Agent Reach CLI → JSON → Private task journal → Obsidian note (when connected)`.
- فقط عملیات read/search تعریف‌شده در ۱۴ کانال نسخهٔ ۱.۶؛ بدون login/logout، post، message، تنظیم حساب یا دورزدن محدودیت پلتفرم.
- اجرای واقعی **پیش‌فرض خاموش** است؛ `invoke` به `--live` و شناسهٔ task/agent/authority reference نیاز دارد. `authority-ref` فقط شناسنامهٔ تصمیم **بالادستی** است و خود آن مجوز نمی‌دهد. اعتبارسنجی Approval و scope همچنان مسئولیت SAGE یا Deep Research است.
- برای هر جفت `(agent_id,task_id)` یک فایل journal خصوصی و یک یادداشت Obsidian ایجاد می‌شود؛ جست‌وجوهای همان task جمع می‌شوند و شناسهٔ `event-id` برای حذف تکرار استفاده می‌شود.
- بدون `configure-vault`، شواهد محلی در `~/.sage/agent-reach/tasks/` صف می‌مانند؛ **در Obsidian نوشته نمی‌شوند**. هر اجرای بعدی `invoke` یا `finalize` تا ۱۰ task را همگام می‌کند؛ دستور `sync` برای صف قدیمی است. هیچ daemon/background delivery وجود ندارد.
- `finalize` متن پاسخ نهایی ایجنت را به همان یادداشت اضافه می‌کند. اجرای خام و مستقیم `agent-reach ...` خارج از Adapter گزارش نمی‌شود؛ برای پوشش کامل باید تمام فراخوانی‌های پژوهشی از این Adapter عبور کنند.
- گزارش فقط منبع، زمان، backend، پرس‌وجو، عنوان و excerpt کوتاه را دارد. `raw`، نشست‌ها و کلیدها ذخیره نمی‌شوند. فیلتر محرمانگی best-effort است؛ ورودی محرمانه نباید وارد query یا پاسخ نهایی عمومی شود.
- هنگام قطع Obsidian، اجرای پژوهش متوقف نمی‌شود؛ نداشتن مسیر Vault معتبر فقط باعث `PENDING` می‌شود. تمام مسیرهای خارج از Vault و symlink/reparse point رد می‌شوند. تغییر دستی داخل بخش managed یادداشت، موجب توقف همگام‌سازی همان note می‌شود؛ متن بیرون آن حفظ می‌شود.

## راه‌اندازی روی سیستم کاربر

در PowerShell از ریشهٔ مخزن SAGE:

```powershell
$adapter = ".\extensions\agent-reach\sage_agent_reach.py"
python $adapter status

# مسیر واقعی Vault را از Obsidian پیدا کن؛ مقدار زیر فقط مثال است.
python $adapter configure-vault --vault "C:\ABSOLUTE\PATH\Alireza-Brain" --folder "11-AI/Research/Agent-Reach"

# فراخوانی خواندنی با شناسنامهٔ مجوز واقعیِ task بالادستی
python $adapter invoke --task-id research-001 --agent sage --authority-ref approved-read-001 `
  --channel github --action search --params-json '["agent-reach"]' --live

# جمع‌آوری نهایی؛ فایل پاسخ باید متن نهایی تولیدشده توسط ایجنت باشد
python $adapter finalize --task-id research-001 --agent sage `
  --answer-file "C:\Temp\Research\research-001-answer.md" --confidence medium

python $adapter sync --limit 100
```

برای Deep Research، همان دستورات را با `--agent deep-research` و شناسهٔ task خود Deep Research صدا بزن. بستهٔ source را یک بار در مسیر مشترک نصب/در دسترس قرار بده، نه اینکه دو کپی ناسازگار ایجاد کنی. اگر اجرا روی host جداگانه است، مسیر CLI محلی به صورت خودکار قابل‌دسترس نیست؛ باید transport مجاز و ایمن با احراز هویت جداگانه برقرار باشد.

## Error policy

`PLATFORM_BLOCKED`، `RATE_LIMITED`، `NEED_LOGIN`، `BUSY` → وضعیت `BLOCKED`، بدون retry، تعویض backend یا ورود خودکار. Timeout و سایر خطاها با `UPSTREAM_ERROR` ثبت می‌شوند. CLI فقط یک فراخوانی به ابزار اصلی انجام می‌دهد. وضعیت `SUCCESS` به معنی دریافت پاسخ است و نه تأیید حقیقت آن.

## Observability / Evidence

پاسخ JSON شامل `schema_version`, `request_id`, `status`, `result`, `report`, `error` است. `report.status=SYNCED` فقط برای batch اجراشده معتبر است. فایل‌های private با atomic write و lock زمان‌دار نگهداری می‌شوند؛ اطلاعات داخل Vault از طریق file-sync مستقیم و محلی نوشته می‌شود. نویسندهٔ task باید قبل از اعلام تکمیل، receipt نهایی را بررسی کند.

## آزمون و بازگشت

```powershell
python -m unittest discover -s tools -p test_sage_agent_reach.py -v
```

آزمون‌ها فقط fake CLI و Vault موقت را به‌کار می‌برند؛ تست محلی Windows/Obsidian واقعی **هنوز انجام نشده**. برای غیرفعال‌کردن کافی است فراخوانی Adapter را از Task Router برداری. فایل‌های outbox و گزارش‌های Vault را صرفاً بعد از بررسی و تأیید مالک حذف کن؛ حذف افزونه نباید داده‌ها یا تنظیمات حساب را پاک کند. هستهٔ `SageAdapters.psm1` همچنان DRY_RUN است.

## یادداشت اتصال DeerFlow / Deep Research

این افزونه خودِ DeerFlow 2.0 را تغییر نمی‌دهد. برای task اجرایی موجود، Source Selector باید `agent-reach` را به‌عنوان ابزار read-only مکمل انتخاب و CLI مشترک را invoke کند. پس از جمع‌بندی Evidence Fusion، با `finalize` پاسخ نهایی را به همان `task_id` ارسال کند. اگر پروژهٔ محلی یا دسترسی اجرای DeerFlow شناسایی نشده، اتصال واقعی آن `PENDING` است؛ وجود مخزن عمومی `bytedance/deer-flow` به معنی نصب/فعال‌بودن ایجنت کاربر نیست.

## English contract

This is an opt-in, read-only CLI companion adapter, **not** a model orchestrator, sandbox, MCP server, or authority grant. No production SAGE settings, browser sessions, or upstream Agent Reach sources are modified. Local offline contract tests are not host smoke tests. The vault path must be explicitly configured and verified before any write to Obsidian can be claimed.
