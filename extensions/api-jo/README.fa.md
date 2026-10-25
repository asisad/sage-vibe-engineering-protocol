# APIجو v0.1 — API Discovery Agent & Credential Broker

**وضعیت تحویل:** کد اجرایی و تست‌های محلی + پنل کاتالوگ؛ یکپارچه‌سازی واقعی کلیدها از طریق سرویس آمادهٔ [Agent Vault](https://github.com/Infisical/agent-vault). نصب خودکار روی رایانهٔ کاربر یا فعال‌سازی مستقل عامل در SAGE با ساخت ZIP اثبات نمی‌شود.

## قابلیت‌ها

- جست‌وجوی منابع: [public-apis](https://github.com/public-apis/public-apis) (MIT)، [publicapis.dev](https://github.com/marcelscruz/public-apis) (MIT)، [APIs.guru](https://github.com/APIs-guru/openapi-directory) (CC0)، با حفظ لینک منبع و تاریخ sync.
- آغاز آفلاین با ۲۸ نامزد نمونه؛ بارگذاری کامل منابع **پس از اجرای sync در محیط متصل به اینترنت** انجام می‌شود؛ تعداد APIهای آنلاین در زمان تدوین این بسته ادعا نشده است.
- SQLite FTS5 با متن، دسته‌بندی، URL، امتیاز BM25 و خروجی Context قابل استناد برای RAG.
- پنل فارسی واکنش‌گرا برای جست‌وجو، گرفتن Context و وضعیت منابع؛ کلیدهای محرمانه در پنل **جداگانهٔ امن Agent Vault** ثبت و نگهداری می‌شوند.
- Agent Vault مدیریت مالک/اعتبارنامه/سرویس/Agent Token/پروپوزال تأیید و HTTP proxy را برعهده دارد؛ APIجو اصلاً کلید را دریافت نمی‌کند.
- خروجی Markdown قابل انتقال به Obsidian بدون ذخیرهٔ Secrets.

## نصب در Windows PowerShell

از این پوشه در رایانهٔ خودت، Python 3.11+ و برای بخش کلیدها Docker Desktop لازم است:

```powershell
cd C:\path\to\APIJo_v0.1
python api_jo.py seed
python api_jo.py sync --source all
.\start-windows.ps1
```

سپس پنل کاتالوگ را باز کن: `http://127.0.0.1:8765`.

برای روشن‌کردن **Agent Vault** با Docker Desktop و ورود رمز اصلی به‌صورت تعاملی:

```powershell
.\start-windows.ps1 -StartVault
```

در مرورگر: `http://127.0.0.1:14321`. در پنل اصلی Agent Vault، owner را بساز، vault جداگانه بساز، کلیدها را از همان پنل اضافه کن، host هر سرویس را به‌دقت تعیین کن، و Agent Token با دامنهٔ حداقلی صادر کن. برای استفادهٔ CLI از token، متغیرهای `AGENT_VAULT_TOKEN`, `AGENT_VAULT_ADDR`, `AGENT_VAULT_VAULT` باید به‌صورت امن در محیط اجرای Agent تزریق شوند؛ **هرگز مقدار کلید یا token را در این چت، GitHub، Obsidian یا پرامپت قرار نده.**

**توجه:** اگر Docker/Agent Vault نصب یا روشن نشده باشد، بخش «کلیدها» تنها راهنمایی و لینک پنل خواهد بود؛ تحویل این بسته به معنی ایجاد Vault واقعی یا ورود کلیدهای قبلی نیست. به‌دلیل نبود دسترسی زنده به Windows PC، آزمون host-level لازم است.

## دستورهای کاربردی

```powershell
python api_jo.py search "weather"
python api_jo.py rag "flight"
python api_jo.py stats
python api_jo.py archive
python api_jo.py discover
python api_jo.py propose --service flight-provider --host api.actual-provider.com --credential-key FLIGHT_API_KEY --reason "Flight status for approved application"
python api_jo.py proposal-status 1
```

**جریان تأیید:** درخواست Agent → proposal در Agent Vault → لینک تأیید مالک → تأیید/رد و واردکردن کلید مفقود در پنل مالک → Agent با credential placeholder و Proxy (بدون دسترسی به مقدار واقعی) کار می‌کند. اگر کلید از قبل موجود باشد از `--existing-key` استفاده می‌شود. تأیید دسترسی سرویس با اجازهٔ تغییر نرم‌افزار در SAGE یکسان نیست.

## مرزهای امنیتی

1. `SQLite` فقط نام‌ها/لینک‌ها/توضیح و متن کاتالوگ را ثبت می‌کند؛ رمزی در آن نیست.
2. افزودن یا تحویل کلید از APIجو امکان ندارد. صفحهٔ کلیدها به ابزار ایزولهٔ Agent Vault می‌رود.
3. در Agent Vault سیاست `unmatched_host_policy=deny`، تفکیک Vaultهای پروژه‌ها، host/path allowlist، least privilege، rotation و expiration را تنظیم کن. **وضعیت اولیهٔ passthrough نباید به‌عنوان enforcement در نظر گرفته شود.**
4. اتصال Agent Vault پروتکل HTTPS MITM دارد. نصب CA آن و اجرای Docker باید با مستندات رسمی و در شبکهٔ قابل اعتماد انجام شود. نصب خودکار یا تغییر تنظیمات شبکه توسط APIجو انجام نمی‌شود.
5. در نسخهٔ اول، برای هر *grant جدید* تأیید خواسته می‌شود؛ برای **هر تماس API** تأیید انسانی تضمین نشده است. در صورت الزام، gateway جدا با lease کوتاه‌عمر لازم است.
6. اگر کلیدها به‌صورت `oauth` یا `query parameter` موردنیاز باشند، `propose` نمونه صرفاً bearer است؛ الگوی auth و محدودیت هر provider باید با سرویس واقعی تنظیم شود.
7. APIجو RAG واژه‌ای دارد (FTS5 + متن قابل تزریق به LLM)، نه بردار/embedding و نه AI مولد مستقل. برای جست‌وجوی معنایی در آینده می‌توان embedding backend اضافه کرد.

## ارتباط با SAGE و Obsidian

ساختار پیشنهادی در SAGE: `extensions/api-jo/` مستقل و اختیاری. طبق قرارداد Agent-Native، discovery مجوز نمی‌دهد و عملیات بیرونی نیازمند approval اصلی SAGE است. ابتدا با تست‌های host واقعی و consent اسکوپ‌دار، adapter را فعال کن. `AGENT.md` قرارداد رفتار ایجنت را توضیح می‌دهد.

خروجی `python api_jo.py archive` را می‌توان در Vault Obsidian بارگذاری کرد. نسخهٔ دارای کلید به Obsidian منتقل نمی‌شود.

## آزمون

```powershell
python -m unittest discover -s tests -v
```

آزمون‌های بدون شبکه parser، FTS، RAG، حذف stale rows، کنترل‌ host/credential input و endpointهای پنل را می‌سنجند. این تست‌ها اثبات نصب روی PC یا کارکرد Agent Vault live نیستند.

## حقوق منابع

مخزن‌های بالا فهرست‌های مستقل‌اند، نه APIهای تضمین‌شده. برای استناد و بازنشر دادهٔ هر منبع، شرایط و license مربوط به همان منبع و API‌دهنده رعایت شود. APIجو فقط metadata را ingest می‌کند و از اجرای اسکریپت منابع ناشناس خودداری می‌کند.