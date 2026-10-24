# SAGE bounded autonomous runtime / اجرای خودکارِ محدود SAGE

Version **0.2.0** is an additive development package, not a new release of the
SAGE **0.8.4** SDK. It turns an authorized small software idea into a plan,
architecture artifacts, generated source, observed checks and an independent
model review. It does not guarantee arbitrary software or security certification.

نسخهٔ **۰٫۲٫۰** یک بستهٔ توسعهٔ مستقل و افزوده است؛ نسخهٔ SDK و برچسب انتشار
`v0.8.4` را تغییر نمی‌دهد. این اجراگر یک درخواست مجاز و محدود را از برنامه‌ریزی
تا تولید کد، آزمون واقعی و بازبینی جداگانه پیش می‌برد. «خودکار» به معنای حذف
مجوز، تضمین صحت هر نرم‌افزار یا صدور گواهی امنیت نیست.

Local reference acceptance on **2026-10-24** verified a Python standard-library
build and a read-only-source repair using isolated Docker checks, independent
behavioral oracles and fresh-session review. **Node and static-web remain
declared profiles, not live end-to-end accepted on this host.** See the
[bounded acceptance receipt](../../extensions/autonomous-runtime/acceptance.json).
These results do not certify arbitrary applications or security.

در پذیرش محلی **۲۰۲۶/۱۰/۲۴**، ساخت و اصلاح نمونه‌های Python با آزمون ایزوله،
آزمون رفتاری مستقل و بازبینی نشست جدا تأیید شد. این اثبات به همان نمونه‌ها و
نمایه محدود است؛ Node و وب ایستا هنوز پذیرش سرتاسریِ زنده روی این دستگاه
ندارند. جزئیات و مرزهای اثبات در رسید بالا ثبت شده‌اند.

```text
Idea / ایده
  -> Intake / فهم نیاز
  -> SAGE + ECC discovery / انتخاب منابع تخصصی
  -> Plan + architecture / برنامه و معماری
  -> Exact plan approval / تأیید همان برنامه
  -> Generate source / تولید کد
  -> Sandboxed checks / آزمون در محیط ایزوله
  -> Independent review / بازبینی جداگانه
  -> Bounded repair loop / اصلاح محدود
  -> Delivery with evidence OR visible stop / تحویل مستند یا توقف روشن
```

## Installation / نصب

Optional real Ruflo task coordination is now available through an explicit
`--ruflo-config`; the model worker remains Codex and all final SAGE gates remain
mandatory. This is not native Ruflo LLM execution or automatic activation of its
catalog. See [the bilingual live-binding guide](../../extensions/ruflo/LIVE_BINDING.fa-en.md).

هماهنگی واقعی کار با Ruflo اختیاری است؛ عامل مدل همچنان Codex است و SAGE
اختیار و پذیرش نهایی را حفظ می‌کند. برای نصب جداگانه و فعال‌سازی صریح،
[راهنمای فارسی/انگلیسی](../../extensions/ruflo/LIVE_BINDING.fa-en.md) را بخوانید.

Python **3.11+**, an installed/authenticated Codex CLI, and a supported isolated
check runner are needed for live work. Node is additionally required for the
Node profile. Missing isolation/tools produce **BLOCKED**, never an unsandboxed
fallback. Docker fallback, where available, requires a suitable image already
present; the runtime never pulls an image or installs dependencies for you.
Docker checks currently cover **Python and static-web only**. Node checks need
an approved, working native sandbox plus Node; there is no Node Docker fallback.
On this delivery machine the native `mxc` sandbox is currently unavailable, so
that native route is **BLOCKED**; generic support does not imply local proof.

برای اجرای واقعی، Python نسخهٔ ۳٫۱۱ یا جدیدتر، Codex نصب‌شده با ورود به حساب و
امکان اجرای آزمون در محیط ایزوله لازم است. فقط نمایهٔ Node به Node هم نیاز
دارد. نبود ابزار یا محیط ایزوله باعث **توقف** می‌شود؛ اجرای بدون ایزوله، نصب
وابستگی و دریافت خودکار ایمیج جایگزین آن نمی‌شود.
در اجرای Docker فعلی فقط Python و وبِ ایستا پوشش دارند؛ نمایهٔ Node به محیط
ایزولهٔ بومیِ تأییدشده و Node نیاز دارد. محیط بومی `mxc` در دستگاه این تحویل
فعلاً در دسترس نیست؛ بنابراین آن مسیر محلی «متوقف» است، نه تأییدشده.

Use a virtual environment; no global installation is necessary:

```powershell
python -m venv C:\Temp\sage-runtime-env
C:\Temp\sage-runtime-env\Scripts\python.exe -m pip install .\runtime\autonomous
C:\Temp\sage-runtime-env\Scripts\sage.exe doctor
```

If using `uv pip install`, add `--link-mode copy`; source validation deliberately
rejects multi-link files. An installation shared through cache hardlinks is not
silently trusted. / در نصب با `uv` از `--link-mode copy` استفاده کنید؛ فایل‌های
چندپیوندی عمداً پذیرفته نمی‌شوند و این کنترل نباید دور زده شود.

Or install a locally built wheel. The wheel contains a curated, attributed
offline closure of the SAGE/ECC catalog, declared sources/resources, licenses,
notices and SAGE contract; it works outside the source repository. The bundled
upstream sources are **data**, not automatically installed Skills/hooks/plugins.
`BUNDLED_RESOURCES.json` records included paths, byte sizes and hashes. Hash
agreement proves local integrity against metadata, not upstream authenticity.
The bundled Skill registry's optional-extension manifests and their declared
catalog/policy/schema/guide metadata are retained. This is an offline source
snapshot, not activation of every listed extension or an entire SAGE repository.

فایل Wheel، منابع لازم برای کشف تخصص را همراه با منشأ، مجوز و هش حمل می‌کند؛
پس استفاده بیرون از مخزن هم ممکن است. کدها و دستورهای موجود در منابع ECC صرفاً
دادهٔ مرجع‌اند؛ با نصب بسته، هیچ اسکیل، هوک یا پلاگینی خودکار فعال نمی‌شود.

## Commands / فرمان‌ها

All command results are JSON; `--json` is also accepted explicitly. Help/version
are normal text. `--kit-root` and `--state-root` work before or after a subcommand.
Source use automatically finds this repository; installed use finds bundled kit
assets. `--kit-root` can select an explicitly trusted compatible source root.

خروجی فرمان‌ها JSON است. برای مشخص‌کردن پوشهٔ منابع و پوشهٔ خصوصی شواهد،
`--kit-root` و `--state-root` را می‌توان پیش یا پس از نام فرمان نوشت.
پوشهٔ شواهد باید بیرون از پروژهٔ تولیدی و منابع مدیریت‌شده باشد.

```powershell
# Readiness only: does NOT call a model / فقط بررسی آمادگی، بدون فراخوانی مدل
sage doctor

# Create a non-live checkpoint; no generated code execution / ایجاد رکورد بدون اجرای مدل
sage build "Create a Python standard-library calculator CLI with unittest tests" --output C:\Temp\sage-calculator --approval-id local-demo

# Or start live; output directory MUST be new and absolute / اجرای واقعی، پوشهٔ جدید
sage build "Create a Python standard-library calculator CLI with unittest tests" --output C:\Temp\sage-calculator-live --approval-id local-demo --live --profile python-stdlib --max-model-calls 6 --max-repairs 1 --max-seconds 600

# Replace RUN_ID and PLAN_SHA256 with the values in actual JSON output
# مقادیر را از خروجی واقعی همان اجرا بردارید
sage status RUN_ID
# Read the latest plan/diagram using the returned artifacts map (details below)
# برنامه و دیاگرام فعلی را از نگاشت artifacts بخوانید، سپس همان هش را تأیید کنید
sage approve RUN_ID --plan-hash PLAN_SHA256
sage resume RUN_ID --live

# Supply requested clarification, without changing authorization / پاسخ به ابهام
sage clarify RUN_ID --answer "Local terminal use only; no network, no third-party dependencies."
sage resume RUN_ID --live

# Pause on a durable boundary, then continue the same run / توقف و ادامهٔ همان اجرا
sage build "Create a small Python stdlib utility and unittest tests" --output C:\Temp\sage-paused --approval-id local-demo --live --pause-after PLAN
sage resume RUN_ID --live

# Cancel without deleting project/evidence / لغو بدون حذف کد یا شواهد
sage cancel RUN_ID
```

### Repair an existing project / اصلاح پروژهٔ موجود

`--source` explicitly selects a small existing local source snapshot to import
into a **new** isolated output. The original is never edited. Source files must
pass the same bounded path/content/credential/link preflight; a checksum-bound
private snapshot supplies planning context and the plan must preserve every
imported source path. Binary assets, secrets, unsupported dependencies or files
outside the bounded profile are not silently admitted. Review the selected
source before import; the model must not receive private data unnecessarily.

با `--source`، یک نمونهٔ کوچک از کد موجود برای اصلاح انتخاب می‌شود؛ اصلاح فقط
در **پوشهٔ خروجی جدید** انجام می‌شود و اصل پروژه دست‌نخورده می‌ماند. مسیرها،
حجم، محتوای متنی، نبود رمز و پیوندها پیش از پذیرش کنترل می‌شوند. برنامه باید
تمام مسیرهای واردشده را حفظ کند؛ فایل خصوصی یا وابستگیِ پشتیبانی‌نشده نباید
بی‌صدا وارد اجرای مدل شود.

```powershell
sage build "Fix the subtraction bug in this stdlib calculator; preserve existing behavior and add a regression unittest" --source C:\Temp\calculator-bug --output C:\Temp\calculator-fixed --approval-id local-bugfix --live --profile python-stdlib --max-model-calls 6 --max-repairs 1
sage approve RUN_ID --plan-hash PLAN_SHA256
sage resume RUN_ID --live
```

`sage doctor` checks provider configuration/authentication and kit presence only.
Its JSON explicitly reports `sandbox_readiness=NOT_PROBED` and
`live_acceptance=NOT_RUN`; a **READY** doctor result does not prove that the actual
test sandbox or an end-to-end build works. The runner must establish supported
isolation during the real authorized verification step, or stop **BLOCKED**.

فرمان `doctor` فقط آمادگی اتصال مدل و وجود منابع کیت را بررسی می‌کند؛ خروجی
`READY` به معنی موفقیت آزمون واقعی یا آمادگی محیط ایزوله نیست. وضعیت این دو
مورد جداگانه «هنوز بررسی/اجرا نشده» اعلام می‌شود و در مرحلهٔ آزمون واقعی باید
تأیید شوند؛ در غیر این صورت کار متوقف می‌شود.

An approval ID is a caller's task-specific authorization reference, **not an
authentication credential** and not proof that the caller owns an external
target. `--live` must be explicit on each build/resume that may use a provider.
`sage approve` records the plan decision; it does not run the model itself.

شناسهٔ مجوز باید به تأیید واقعی همین کار اشاره کند؛ این شناسه رمز ورود یا
مجوز نامحدود نیست. برای فراخوانی مدل، `--live` لازم است. تأیید برنامه به‌تنهایی
اجرای مدل را آغاز نمی‌کند؛ پس از آن باید `resume --live` اجرا شود.

Evidence artifacts are immutable and versioned. After clarification/replanning,
an older root-level `plan.json` or `architecture.mmd` may still exist and must not
be assumed current. Read the latest `sage status RUN_ID` JSON: combine
`evidence_directory` with `artifacts["plan.json"]` or
`artifacts["architecture.mmd"]` to find the latest **committed** artifact. Review
that plan and approve only the same status response's current `plan_hash`.

شواهد نسخه‌دار و تغییرناپذیرند. پس از پاسخ به ابهام و برنامه‌ریزی مجدد، ممکن
است فایل قدیمی `plan.json` یا `architecture.mmd` همچنان وجود داشته باشد؛ آن
را برنامهٔ فعلی فرض نکنید. مسیر نسخهٔ معتبر را از نگاشت `artifacts` در آخرین
خروجی `status` بردارید و به `evidence_directory` اضافه کنید؛ سپس فقط
`plan_hash` همان وضعیت فعلی را تأیید کنید.

Only when the user already authorized **R1 low-risk local implementation**, add
`--auto-approve-plan` to a live build. The engine still validates the plan and its
scope; this flag never authorizes external actions, deployment, Git push, package
installation, scans or broader permissions.

فقط وقتی کاربر از قبل پیاده‌سازی محلی و کم‌خطر **R1** را تأیید کرده، می‌توان
`--auto-approve-plan` را به فرمان ساخت واقعی افزود. این گزینه مجوز انتشار،
نصب ابزار، Push، اسکن امنیتی یا دسترسی خارجی ایجاد نمی‌کند.

## Initial capability boundary / محدودهٔ اولیه

| Profile | Supported scope | Explicitly outside this scope |
| --- | --- | --- |
| `python-stdlib` | Local Python source and standard-library checks/tests | pip installs, frameworks, network services |
| `node-stdlib` | Local Node source and built-in checks/tests | npm installs, frameworks, network services |
| `static-web` | Static HTML/CSS/JavaScript and supported fixed checks | Browser/device/visual certification; automatic hosting |

Unsupported stacks stop with a capability gap. This runtime does not silently
replace your requested technology. A separate model session reviews generated
work, but a model's opinion cannot mark a test **PASS**. Fixed runtime-owned
checks produce observed receipts; **DONE** is only valid for the checked current
project hash. Selected ECC agents are source definitions, not hundreds of
independently provisioned workers.

اگر فناوری در محدوده نباشد، اجراگر باید کمبود قابلیت را روشن اعلام کند؛ حق
ندارد بی‌صدا زبان دلخواه خود را جایگزین کند. بازبینی مدل از جلسهٔ تولید جداست،
ولی نظر مدل جای نتیجهٔ آزمون را نمی‌گیرد. صرف وجود تعریف نقش در ECC به معنی
راه‌اندازی صدها ایجنت واقعی نیست.

## Durable budgets and stops / سقف‌ها و توقف‌ها

Defaults: **12 model invocations**, **2 repairs**, **900 elapsed seconds** per
run. There are also bounded file/context/total-project byte and file-count
limits. Calls are reserved **before** launch: failed or interrupted calls still
count. Resume reuses the same budget and integrity-bound evidence ledger; it
cannot reset limits. Review/repair sessions count as calls. There is no automatic
model/provider fallback or controller-level hidden retry. The Codex CLI's own
internal HTTP/SSE retry policy is not attested or overridden here; disabling its
unbounded-retry feature does **not** prove zero underlying HTTP retries. The cap
counts controller-launched CLI invocations, including failed bootstrap attempts,
not individual upstream requests. These are local controls, **not a
guaranteed monetary spending cap** for account-authenticated providers.

پیش‌فرض هر اجرا: **۱۲ فراخوانی مدل، ۲ نوبت اصلاح و ۹۰۰ ثانیه**. فراخوانی ناموفق
یا قطع‌شده هم مصرف‌شده محسوب می‌شود. ادامهٔ اجرا سقف را صفر نمی‌کند. این
سقف‌های فنی، تضمین سقف مبلغ صورتحساب نیستند. در آزمون پذیرش این تغییر، سقف
تجمیعی جداگانهٔ ۱۲ فراخوانی برای کل تحویل برقرار است؛ نه ۱۲ فراخوانی برای هر
آزمون.
سقف، تعداد اجرای CLI به‌دست کنترل‌کننده را می‌شمارد؛ تلاش ناموفق آغاز اتصال
هم محاسبه می‌شود. سیاست تکرار درخواست‌های HTTP/SSE داخل Codex در اینجا
تأیید یا بازنویسی نشده است؛ خاموش‌بودن تکرار نامحدود به معنی صفر درخواست
تکراری در لایهٔ داخلی نیست.

Examples of visible non-completion: missing authorization, clarification needed,
plan approval pending, unsupported stack, provider unavailable, sandbox blocked,
budget exhausted, failed checks, failed review or altered evidence/project files.
Exit **0** indicates a successful command (which can still be non-live); **2**
indicates a visible blocked/action-needed run, and **1** a structured input or
runtime error. Always inspect the JSON status and evidence, not just exit code.

## Safety and evidence / ایمنی و شواهد

- Generated paths/content are validated as a complete bounded set before writes.
  Links, credentials, traversal and protected paths are rejected; existing user
  projects are not used as unrestricted workspaces.
- Model sessions are read-only and use structured payloads. Source packets cannot
  supply shell commands, model names, credentials or permission grants.
- Runtime-controlled profiles execute only inside supported isolation; model
  credentials are not forwarded to generated checks.
- State/receipts/hash-chained events live outside generated projects. This is
  local tamper evidence, not remote attestation or proof against an administrator
  who controls every local file.
- No automatic deployment, publication, Git push, Strix scan, cloud provisioning,
  arbitrary tool execution or dependency installation.

سِیج صاحب محدوده، مجوز و شواهد می‌ماند. منابع ECC مشاورند. هیچ مرز امنیتی با
متن تولیدی مدل یا دستور تعبیه‌شده در اسکیل کنار گذاشته نمی‌شود. آزمون محلی یا
موفقیت CI، به‌تنهایی اثبات کارکرد بصری، مرورگر واقعی، امنیت کامل یا آمادگی هر
محصول برای Production نیست.

## Local verification / بررسی محلی

```powershell
$env:PYTHONPATH = (Resolve-Path .\runtime\autonomous\src).Path
python -m unittest discover -s runtime/autonomous/tests -v
python -m sage_runtime --version
python -m sage_runtime doctor
```

Unit tests use fake provider/runner objects and never call a real model. A live
acceptance run is separately authorized and must retain actual provider/check
receipts. Read [`DESIGN.md`](DESIGN.md) for the implementation contract. Original
runtime code is MIT; bundled third-party sources retain source-local licenses
and the complete notices inside `_kit/extensions/ecc/THIRD_PARTY_NOTICES.md`.
