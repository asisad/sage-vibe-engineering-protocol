# معماری تیم مهندسی AI چندزبانه در SAGE — نسخه 0.2 (توسعه‌یافته از 0.1)

**تاریخ:** ۱۴ اکتبر ۲۰۲۶  
**وضعیت:** طرح و فایل‌های پیکربندی اولیه؛ فاقد Agent مستقر یا خودکار در محیط اجرایی. **مالک معماری: SAGE؛ SENS فقط زیرسیستم مشاهده و تحلیل.**

## تصمیم اصلی
ساختن یک Agent مستقل برای تک‌تک زبان‌های جهان مقرون‌به‌صرفه نیست. بهتر است یک «معمار/هماهنگ‌کننده»، چند «متخصص پرکاربرد»، «مهارت‌های قابل‌بارگذاری» و «بازبین مستقل» داشته باشیم. متخصصان کم‌مصرف و زبان‌های نو به‌صورت On-demand فعال شوند. راهبرد انتخاب فناوری Rust-first **برای زیرساخت‌های مناسب** است؛ نه Rust-everywhere.

## چهار معنای متفاوت از یادگیری
1. **آموزش مدل پایه:** وزن‌های شبکه عصبی از گفت‌وگو و مطالعه مستندات به‌صورت دلخواه یا دائمی تغییر نمی‌کنند.
2. **یادگیری در بستر همان کار:** Agent می‌تواند مستندات، کد، کتابخانه و خطاهای کامپایلر را در context بررسی کند.
3. **دانش قابل‌بازیابی:** File / Git / AGENTS.md / Skill / RAG می‌تواند راهکارها، تجربه‌ها و استانداردها را در دسترس اجرای بعدی بگذارد؛ به شرط اتصال و بازیابی صحیح.
4. **آموزش واقعی اختصاصی:** یک پروژه جداگانه با داده و فرایند ارزیابی/آموزش مدل است؛ پیش‌نیاز راه‌اندازی این تیم نیست.

## ساختار اجرایی پیشنهادی

```text
User / Engineering Request
           |
           v
Engineering Orchestrator (selection + cost + approval)
           |
           +-- Language Specialist (Rust/Python/TS/Go/C#/C++/SQL/Graphics)
           |       |
           |       +-- Skill + official/versioned docs + repository + sandbox
           |       |
           |       +-- Compiler, linter, unit/integration/performance tests
           |
           +-- Independent QA/Security reviewer
           |
           +-- Docs/Knowledge curator -> provenance-preserving Memory/RAG
           |
           v
Technical decision + tested artifact + source/evidence log
```

## نقش‌های کلیدی
- **Engineering Orchestrator:** انتخاب کمترین تعداد متخصص ضروری و هماهنگی تصمیم‌ها.
- **Rust Engineer:** داده‌های حجیم، صف‌های محدود، هم‌زمانی، سرویس‌های سبک، telemetry و بخش‌های MCP.
- **Python AI Engineer:** مدل، RAG، ML experiment، APIهای AI و Blender automation.
- **TypeScript/Web Engineer:** مرورگر، UI، داشبورد، Three.js/WebGL.
- **Go Engineer:** سرویس‌های شبکه‌ای کم‌پیچیدگی، CLI و tooling.
- **C# Engineer:** Unity و پروژه‌های .NET.
- **C++ Engineer:** Unreal و ابزارهای native وابسته به C++.
- **Data Engineer:** PostgreSQL/SQL، جداسازی داده خام از استنتاج، provenance و UEG.
- **Graphics Engineer:** موتور بازی، رندر و shader.
- **Language Researcher:** Zig، Mojo و فناوری‌های زودتغییر؛ ابتدا نمونه اجرا، نه انتخاب تولید.
- **QA/Security:** بازبینی مستقل و آزمون‌های واقعی.

## قانون انتخاب زبان
| مسئله | کاندید نخست | شرط تغییر انتخاب |
|---|---|---|
| SENS collection/normalization hot path | Rust | اگر overhead و هزینه توسعه با ابزار آماده کمتر شود، آماده را ترجیح بده |
| AI training/experimentation | Python | در kernel محاسباتی، benchmark Rust/C++/Mojo انجام بده |
| Agent orchestration | Python/TypeScript | اگر binary/tool runtime کوچک و مستقل لازم است Rust/Go بررسی شود |
| MCP gateways/tool policy enforcement | Rust یا TypeScript | امنیت، SDK و محیط استقرار تصمیم نهایی را تعیین می‌کنند |
| Dashboards and browser 3D | TypeScript | محیط desktop/native نیازمند انتخاب متفاوت است |
| Unity | C# | اجزای native فقط با سنجش عملکرد |
| Unreal | C++ | نیازمندی موتور و plugin ecosystem |
| UEG/CMDB persistence | PostgreSQL/SQL + ابزارهای آماده | محاسبات الگوریتمی ویژه ممکن است Rust بخواهد |
| GPU kernels | C++/CUDA و ابزار جاافتاده | Mojo فقط با اثبات ابزار و عملکرد در target |

## SENS — سیاست ثابت
- **Out-of-band + fail-open + non-invasive**؛ سیستم پایش نباید سرویس مورد مشاهده را کند یا ناپایدار کند.
- سقف CPU، حافظه، network، storage، queue، latency و cardinality تعریف شود.
- bounded queues، backpressure، sampling/adaptive sampling، batching، aggregation، compression و retention/tiering.
- کاهش کیفیت تدریجی telemetry در فشار بالا: full -> sampled -> metrics-only.
- meta-observability کم‌حجم همراه با recursion guard.
- پروژه فعلی را صرفاً برای «استفاده از Rust» بازنویسی نکنید. ابتدا benchmark و مقایسه با baseline.

## تفاوت فایل‌ها
- `AGENTS.md`: سیاست‌ها و قراردادهای کاری در scope مخزن.
- `skills/*/SKILL.md`: راهنمای رویه تخصصی قابل‌فعال‌سازی در محیط‌های سازگار.
- `agents/*.md`: **تعریف نقش** برای نگاشت به سیستم orchestrator؛ به‌خودی‌خود Agent مستقل نمی‌سازد.
- `knowledge/`: داده تجربی بازیابی‌پذیر و دارای provenance، نه تغییر وزن‌های مدل.
- `quality/`: حداقل شواهد لازم برای تأیید خروجی.

## گردش کار نمونه
1. مأموریت و acceptance criteria ثبت شود.
2. مخزن به شکل read-only بررسی و نسخه‌ها شناسایی شوند.
3. Orchestrator زبان و متخصص را انتخاب و بر مبنای ADR توجیه کند.
4. متخصص مستندات نسخه صحیح را بخواند؛ اجرای ممنوع یا خطرناک نیازمند تأیید انسانی باشد.
5. یک diff کوچک در شاخه/محیط امن پیاده شود.
6. Build، lint، test، scan و در صورت نیاز benchmark انجام شود.
7. بازبین مستقل مسائل امنیت، معماری و performance را کنترل کند.
8. با حفظ لینک منبع/نسخه/شواهد، تصمیم‌ها در Knowledge ثبت شوند.
9. اقدامات مخرب، انتشار، استقرار و دسترسی به اسرار بدون مجوز انجام نشوند.

## برنامه استقرار در سه فاز
**فاز A — بدون پیچیدگی اجرای چند Agent:** AGENTS.md + Skillهای Rust/Python/TypeScript + QA را روی یک مخزن تست به کار ببرید.  
**فاز B — Agentهای واقعی در یک harness:** Orchestrator و 3-5 متخصص + QA را به runtime دارای ابزار مخزن/کامپایل/تست وصل کنید؛ مجوزها و session state تعریف شود.  
**فاز C — دانش پایدار:** RAG مستندات versioned، trace، آزمون‌های تکراری و evaluation ایجاد کنید و نقش‌های Go/C#/C++/Graphics را طبق مصرف فعال کنید.

## ریسک‌ها
- زیادکردن بی‌مورد Agent باعث افزایش هزینه و پیچیدگی و حتی اختلاف دستورها می‌شود.
- Memory/RAG اگر بدون provenance و تاریخ انقضا باشد، کتابخانه‌های قدیمی را معتبر نشان می‌دهد.
- متخصص زبانی بدون build/test صرفاً یک persona است، نه شواهد تخصص.
- دسترسی گسترده Agentها به shell، مخزن، شبکه و اسرار خطرناک است. least privilege و sandbox اجباری.
- تخصص به معنی تضمین صحت یا حذف بازبینی انسانی در تغییرات حساس نیست.

## Definition of Done برای Pilot
یک مخزن نمونه، حداقل سه سناریوی واقعی، نسخه ابزار دقیق، خروجی compile/test مستند، یک بازبینی مستقل، اندازه‌گیری overhead در سناریوی SENS، و ثبت شکست‌ها/درس‌ها در Knowledge. نتیجه پیش از این مرحله «پیکربندی اولیه» است، نه یک تیم Agent آزمایش‌شده.

---

# افزودهٔ معماری v0.2 — دامنه توسعه مهندسی و تفکیک SAGE / SENS

## ۱. اصلاح مرز معماری (تصمیم الزام‌آور)

SAGE = **SiSsad Agentic General Engineering**، معماری مادر برای وایب‌کدینگ مهندسی‌شده، SDAE/Spec-Driven Agentic Engineering، Constitution، معماری و تأیید تصمیم‌ها، Engineering Orchestrator، Agent/Model Fabric، Skill Router و MCP/CLI/Tool Execution. **تمام Agentهای متخصص برنامه‌نویسی و سخت‌افزار متعلق به SAGE هستند.**

SENS = **SiSsad Engineering Nervous System**، زیرسامانه مشاهده و تحلیل است که شواهد اجرای Agentها و برنامه‌ها را جمع‌آوری می‌کند: UEG، CMDB، گراف کد/دانش/تصمیم، ثبت لاگ و تله‌متری، تشخیص drift، تحلیل اثر تغییر، replay و نمایش SEOv. SENS به اجرای کد یا کنترل موتور فرمان نمی‌دهد؛ از وضعیت SAGE و پروژه‌ها شواهد دریافت می‌کند و پیشنهاد/گزارش به SAGE برمی‌گرداند.

```text
SAGE (parent)
 ├── Constitution / SDAE / Architecture Authority / ADR
 ├── Engineering Orchestrator + Agent/Model Fabric
 │    ├── Language specialists: Rust, Python, TS, Go, C#, C++, SQL...
 │    ├── Domain specialists: Docker, Embedded, Robotics, CNC, IaC, HDL...
 │    ├── Skill Router + SKILL.md
 │    ├── MCP/CLI/Tool execution boundary (approval-gated)
 │    └── QA / Security / Verification
 ├── Repository Knowledge + Artifact/Evidence References
 └── SENS Integration Bridge (nonblocking, privacy- and budget-aware)
         |
         v
      SENS (SAGE subcomponent; passive observer)
      UEG + CMDB + Telemetry + Drift + Code/Knowledge Graph + SEOv
         |
         +----> Evidence / Analysis / Suggestions ----> SAGE
```

**قانون مرزی:** SAGE منبع مصوب تصمیم‌های معماری و تغییرات است؛ SENS منبع شواهد مشاهداتی و روابط تحلیل‌شده است. SENS هرگز جای Orchestrator یا Skill Router را نمی‌گیرد. اتصال باید out-of-band، fail-open و با budget/queue/sampling محدود باشد. برای قرارداد جزئی: `docs/SAGE_SENS_INTEGRATION.md`.

## ۲. چهار گروه فناوری متفاوت

۱. **زبان برنامه‌نویسی:** Rust، Python، TypeScript، Go، C/C++، C#، SQL و زبان‌های تعبیه‌شده.  
۲. **سکو و چارچوب:** Docker، Docker Compose، Kubernetes، Arduino ecosystem، ESP32 hardware، ESP-IDF، Zephyr، ROS2.  
۳. **زبان دامنه‌محور یا پیکربندی:** G-code، Dockerfile، Terraform/HCL، YAML، Kubernetes manifests، Shader DSL، PLC Structured Text.  
۴. **تجهیزات/رابط‌های فیزیکی:** سروو و استپر موتور، GPIO، PWM، I²C، SPI، UART، CNC، FPGA.

از این رو ایجاد ده‌ها «Agent زبان» دائمی غلط است. یک متخصص دامنه می‌تواند چند زبان و پروتکل مرتبط را پوشش دهد. مثلاً متخصص Embedded براساس مدل دقیق ESP32 بین ESP-IDF (C/C++)، Arduino (C++)، MicroPython و Rust (`esp-hal`) انتخاب می‌کند؛ متخصص CNC نوع کنترلر و dialect را می‌سنجد؛ متخصص DevOps با Dockerfile و Compose و Kubernetes سروکار دارد.

## ۳. شش نقش و شش Skill جدید

| نقش جدید SAGE | Skill | کارکرد اصلی | الزام |
|---|---|---|---|
| `devops-containers-engineer` | `devops-containers` | Docker/Compose، کانتینر، Kubernetes، امنیت و بسته‌بندی | قبل از اجرای سرویس یا deploy مجوز |
| `embedded-iot-engineer` | `embedded-iot` | Arduino، ESP32، STM32، C/C++، MicroPython، Rust Embedded | مشخصات واقعی برد + compile قبل از flash |
| `robotics-control-engineer` | `robotics-motion` | Servo/Stepper، PWM، درایور، سنسور، ROS2 | حدود حرکتی، توقف اضطراری، simulation |
| `cnc-gcode-engineer` | `cnc-gcode` | G-code، GRBL، LinuxCNC، Marlin/Klipper | کنترلر/dialect، واحد و dry run |
| `automation-iac-engineer` | `automation-iac` | Bash/PowerShell، YAML، Terraform، Ansible، CI | plan و validation، بدون apply خودسرانه |
| `hdl-fpga-engineer` | `hdl-fpga` | Verilog/SystemVerilog/VHDL و آزمون FPGA | simulator/testbench و timing، جدا از پروگرام سخت‌افزار |

تمام نقش‌ها زیرمجموعه `agents/ROUTER.md` در SAGE قرار می‌گیرند. تخصص‌های نادر مثل PLC یا Mojo از `language-researcher` و Skill/ابزار مناسب استفاده می‌کنند تا زمان نیاز به نقش پایدار اثبات شود.

## ۴. نمونه مسیر کار — ESP32 و سروو موتور

```text
درخواست: ESP32 موتور سروو را با داده سنسور کنترل کند
SAGE Orchestrator
  -> Embedded + Robotics Specialist
     -> Board/SoC/pinout/driver/voltage/limits
     -> Language choice (ESP-IDF C/C++ / Arduino C++ / MicroPython / Rust)
     -> Firmware code + deterministic unit tests
     -> Offline compile + trajectory simulation
     -> Independent QA/Safety review
     -> **Explicit authorization required for board flashing or motor actuation**
SAGE evidence emitter -> SENS async bounded event ingest
SENS -> UEG link (task -> agent -> code -> tool -> build result), anomalies & report
SAGE Architect -> approve/reject next action
```

مثال Docker نیز همین‌طور است: `Dockerfile` و `compose.yaml` تحت مسئولیت DevOps در SAGE تولید و اعتبارسنجی می‌شوند؛ SENS فقط رخدادهای build/deploy مجاز و رفتار container را پایش می‌کند. `docker compose up/down` یا تغییر production بدون اجازه اجرا نمی‌شود.

## ۵. اولویت اجرا در نسخهٔ بعدی

- **P0:** Orchestrator + Rust/Python/TypeScript + QA و قابلیت DevOps/Containers برای محیط‌های تست و CI. Data/SQL نیز برای SENS/UEG نزدیک هسته می‌ماند.
- **P1 (On-demand):** Embedded + Robotics + CNC برای کارهای سخت‌افزاری، Go/C#/C++ و Graphics برای پروژه‌های مربوط.
- **P2 (On-demand):** HDL/FPGA، PLC و زبان‌های کم‌مصرف/جدید؛ فقط پس از پژوهش، ابزار مناسب و اثبات با نمونه واقعی.

**این سند برنامهٔ معماری و بستهٔ نقش/مهارت است؛ Agent اجرایی مستقلی را نصب نمی‌کند.** اتصال به SAGE و SENS واقعی باید بر مبنای مخازن اصلی، سیاست‌ها، قراردادهای داده و ساختار جاری آن‌ها انجام شود و بدون دسترسی به مخزن نباید ادعای ادغام مستقیم مطرح شود.

## ۶. آزمون‌پذیری و دروازه ایمنی

| سطح ادعای موفقیت | شرط |
|---|---|
| Syntax validated | parser/formatter/linter با خروجی واقعی |
| Build successful | کامپایل روی toolchain و target مشخص |
| Simulated successfully | simulation با فرض‌ها و پارامترهای مستند |
| Hardware tested | دستگاه واقعی، مجوز و لاگ تأییدشده |
| Production deployed | مجوز جدا و شواهد واقعی deployment |

فایل‌های `quality/QUALITY_GATES.md` و `quality/AGENT_EVALUATION.md` معیارها را بسط داده‌اند؛ **NOT RUN** هرگز معادل PASS نیست.

## ۷. تفکیک منابع و محدودیت‌ها

این افزوده از مستندات رسمی Docker، Arduino، Espressif ESP-IDF، esp-rs، MicroPython، LinuxCNC، Terraform و Zephyr استفاده کرده است. URLها در `docs/SOURCES.md` و `docs/CAPABILITY_CATALOG_FA.md` آمده‌اند. پشتیبانی تراشه، فرمان CNC و رفتار tooling به نسخه و دستگاه وابسته‌اند؛ هر مأموریت باید جداگانه اعتبارسنجی شود.
