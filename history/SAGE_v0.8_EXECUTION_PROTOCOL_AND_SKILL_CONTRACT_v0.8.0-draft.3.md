# SAGE — SiSsad Agentic General Engineering
## Execution Protocol & Skill Contract v0.8

Status: Draft for Review  
Version: 0.8.0-draft.3  
Date: 2026-09-09  
Language: Persian explanatory text; English machine contracts  
Extends: SAGE Master Baseline v0.7  
Replaces: Nothing

Source Baseline: SAGE_v0.7_MASTER_BASELINE.md  
Baseline SHA-256: DC0C6BAF80465E1F2CF63A2ACA96F3578153A898D55752DEB9A936E506FD6C0D  
Handoff Source: SAGE_HANDOFF_v0.7_to_v0.8.md  
Handoff SHA-256: 867ADAB8787B00AA25024DC293C850A5D58E4B1132AA7A2F06762D179679CD5E  
Revision: Source integration and independent-review remediation pass for specification workflows, engineering briefs, convergence, composable workflow packages, and authorized security validation

این سند، قانون اساسی SAGE v0.7 را تغییر نمی‌دهد. وظیفهٔ آن تبدیل قواعد v0.7 به یک پروتکل اجرایی، قابل‌ردیابی و قابل‌پیاده‌سازی برای Orchestrator، Agent، Skill و Tool است.

تا زمانی که این سند صریحاً تصویب نشود، وضعیت آن Draft است و نباید به‌عنوان Baseline رسمی v0.8 معرفی شود.

---

# ۱. هدف

SAGE v0.8 باید بتواند برای یک درخواست مهندسی مشخص کند:

۱) Intent و Scope چیست؛  
۲) Task در کدام سطح Risk از R0 تا R4 قرار می‌گیرد؛  
۳) کدام Domainها تحت‌تأثیرند؛  
۴) کدام Quality Gateها واقعاً لازم‌اند؛  
۵) چه Approvalهایی باید پیش از Action دریافت شوند؛  
۶) کدام Agent، Skill و Tool واجد شرایط‌اند؛  
۷) حداقل Context کافی چیست؛  
۸) چه Evidenceای Completion را ثابت می‌کند؛  
۹) Failure چگونه Diagnose و Repair می‌شود؛  
۱۰) چه زمانی Loop باید متوقف و Escalate شود.

اصل اجرایی:

> The control plane must be deterministic enough to audit; the execution plane must remain adaptive enough to solve the task.

---

# ۲. دامنه

## ۲.۱. در دامنهٔ v0.8

- Execution State Machine
- Task Envelope و Task Packet
- Risk Classification Protocol
- Affected-Domain Detection
- Quality Gate Resolution
- Dynamic Definition of Done
- Skill Contract
- Skill Discovery و Routing
- Agent / Model / Tool Eligibility
- Context Packaging
- Approval و Policy Enforcement
- Verify–Diagnose–Repair Loop
- Circuit Breaker و Escalation
- Evidence Contract
- Run Ledger و Handoff
- نمونهٔ قراردادهای YAML
- سناریوهای پذیرش R0 تا R4
- Runtime Engineering Brief و Goal/Change Scope contracts
- Clarification، cross-artifact consistency و convergence gates
- Workflow Package، Instruction Projection و source provenance
- Authorized Security Validation adapter contract
- JSON Schema 2020-12، policy examples، fixtures و validator reference

## ۲.۲. خارج از دامنهٔ v0.8

- پیاده‌سازی Runtime نهایی Orchestrator
- ساخت Dashboard برای SENS
- انتخاب Provider نهایی
- ساخت Model Benchmark Registry واقعی
- تعریف Agent Reputation Score عملیاتی
- پیاده‌سازی Distributed Swarm
- ساخت همهٔ Skillهای مهندسی
- نصب یا اجرای ابزار امنیتی خاص از جمله Strix
- انجام penetration test یا scan علیه هر Target واقعی
- جایگزینی CI/CD یا Repository policy موجود
- تعریف استاندارد کامل Telemetry برای SENS

این موارد می‌توانند در نسخه‌های بعدی بر پایهٔ قراردادهای همین سند ساخته شوند.

---

# ۳. زبان الزامات

چهار واژهٔ اصلی v0.7 حفظ می‌شوند:

| واژه | معنا |
|---|---|
| MUST | الزام غیرقابل‌حذف مگر توسط Rule بالادست |
| MUST NOT | ممنوعیت |
| SHOULD | پیش‌فرض قوی؛ انحراف نیازمند Rationale است |
| MAY | اختیاری و وابسته به Context |

واژه‌های اجرایی جدید:

| واژه | معنا |
|---|---|
| BLOCKING | تا رفع آن، Run حق رسیدن به DONE ندارد |
| CONDITIONAL | فقط با Trigger صریح فعال می‌شود |
| EVIDENCE | شاهد قابل‌انتساب به یک Claim یا Gate |
| AUTHORITY | حق معتبر برای انجام یک Action مشخص |
| POLICY | قانون قابل‌اعمال بر Run، Project یا Environment |

---

# ۴. اصول طراحی v0.8

## ۴.۱. Proportional Engineering

کم‌هزینه‌ترین فرایندی که Evidence کافی و ایمن تولید می‌کند ترجیح دارد.

## ۴.۲. Deterministic Control, Adaptive Execution

Classification، Gate Resolution، Permission Check و Completion Evaluation باید قابل‌توضیح و قابل‌بازتولید باشند. روش حل مسئله می‌تواند با توجه به Agent، Skill و Evidence تطبیق پیدا کند.

## ۴.۳. Evidence over Declaration

اعلام Agent مبنی بر «تمام شد» Evidence محسوب نمی‌شود.

## ۴.۴. Authority Cannot Be Inherited from Capability

توانایی Tool یا Skill برای انجام یک Action، مجوز انجام آن Action نیست.

## ۴.۵. Minimum Sufficient Context

Agent فقط Context لازم برای Task را دریافت می‌کند، نه کل Repository یا کل Chat history.

## ۴.۶. No Silent Scope Expansion

تغییر در Scope، Side Effect، Dependency، Public Contract یا Data Boundary باید آشکار و در صورت لزوم دوباره تأیید شود.

## ۴.۷. Native Compatibility

SAGE نباید فایل‌های بومی Provider را با Metadata اختصاصی و ناسازگار پر کند. اطلاعات قابل‌حمل SAGE در Sidecar یا Registry نگهداری می‌شود.

## ۴.۸. Idempotent Control Operations

تا حد امکان، تکرار یک فرمان کنترلی با Idempotency Key یکسان نباید Side Effect جدید ایجاد کند.

## ۴.۹. Repository as Source of Truth

تصمیم، Spec، Evidence و وضعیت پایدار نباید فقط در حافظهٔ Agent یا متن گفتگو باقی بمانند.

## ۴.۱۰. Fail Closed on Authority

اگر مجوز مبهم، منقضی یا خارج از Scope باشد، Action متوقف می‌شود. ابهام در Permission نباید به اجرای خوش‌بینانه تبدیل شود.

## ۴.۱۱. Source Before Synthesis

Artifact مشتق‌شده باید Source، نسخه یا Hash و نوع Authority آن را نگه دارد. متن Reference یا Prompt به‌خودی‌خود Rule حاکم نیست؛ ابتدا باید تحلیل، تعمیم و disposition شود.

## ۴.۱۲. Specification and Reality Must Converge

Spec، Plan، Task، Implementation و Evidence نباید بی‌صدا از هم جدا شوند. اختلاف باید یا اصلاح شود، یا به‌عنوان deviation مجاز و دارای Rationale ثبت گردد.

## ۴.۱۳. Security Testing Requires Explicit Authorization

Capability امنیتی، اجازهٔ آزمون امنیتی ایجاد نمی‌کند. هر اقدام تهاجمی یا شبه‌تهاجمی MUST دارای مالک یا مجوز کتبی، Target دقیق، محدودیت روش، زمان، بودجه و Stop condition باشد.

---

# ۵. سلسله‌مراتب Ruleها

ترتیب پایه از بالاترین Authority:

۱) قانون، Safety constraint و Platform/System policy غیرقابل‌تخطی  
۲) Intent، Constraint و Authorization صریح کاربر برای Task جاری  
۳) Policyهای معتبر Organization، Workspace، Repository و Path  
۴) SAGE Master Constitution v0.7  
۵) SAGE Execution Protocol v0.8  
۶) Project Workflow و Task Plan  
۷) Skill instructions  
۸) Agent heuristics

قواعد:

- Rule پایین‌تر MUST NOT Rule بالاتر را گسترش، تضعیف یا دور بزند.
- Skill MUST NOT Authority جدید ایجاد کند.
- در تعارض Permission، تفسیر محدودتر اجرا می‌شود تا تعارض حل شود.
- Rule انتخاب‌شده باید Source، Scope و دلیل اعمال‌شدن داشته باشد.
- Project policy می‌تواند SAGE default را سخت‌گیرانه‌تر کند.
- انحراف از SHOULD باید Rationale ثبت کند؛ انحراف از MUST فقط با Rule بالادست ممکن است.
- در میان projectionها و بسته‌های Workflow هم‌سطح، اولویت صریح Project override سپس selected profile/package سپس default برقرار است؛ ambiguity در تعارض هم‌سطح باید BLOCKING شود.
- فایل‌هایی مانند `AGENTS.md`، `CLAUDE.md` یا تنظیمات Provider projection هستند و MUST NOT منبع حاکم را بی‌ردپا جایگزین کنند.

---

# ۶. معماری اجرایی

~~~text
USER INTENT
    ↓
INTAKE + AUTHORITY
    ↓
TASK ENVELOPE
    ↓
PRELIMINARY CLASSIFICATION
    ↓
BOUNDED DISCOVERY / CLARIFICATION GATE
    ↓
FINAL CLASSIFICATION + AFFECTED DOMAINS
    ↓
RUNTIME ENGINEERING BRIEF + GATE COMPILER
    ↓
EXECUTION PLAN
    ↓
POLICY / APPROVAL CHECK
    ↓
CONTEXT PACKAGER
    ↓
AGENT + SKILL + TOOL ROUTER
    ↓
EXECUTION
    ↓
VERIFY → ANALYZE CONSISTENCY → DIAGNOSE → REPAIR
    ↓
REVIEW / APPROVAL / CONVERGENCE
    ↓
DYNAMIC DoD
    ↓
DONE / BLOCKED / ESCALATED / FAILED
~~~

## ۶.۱. Control Plane

Control Plane شامل این اجزاست:

- Intake Controller
- Clarification Gate
- Two-pass Risk Classifier
- Domain Detector
- Gate Compiler
- Cross-Artifact Consistency Analyzer
- Convergence Engine
- Anti-Overengineering Evaluator
- Policy Engine
- Approval Manager
- Context Packager
- Router
- Run State Machine
- Evidence Evaluator
- Circuit Breaker
- Ledger Writer

## ۶.۲. Execution Plane

Execution Plane شامل:

- Agents
- Models
- Skills
- Tools
- Scripts
- Provider adapters
- Local runtimes
- CI/CD runners
- Optional authorized security adapters

## ۶.۳. Evidence Plane

Evidence Plane شامل:

- Test results
- Build outputs
- Static-analysis results
- Diffs و hashes
- Review findings
- Approval records
- Runtime observations
- Rollback / recovery evidence
- Coverage disclosure و failure artifacts
- Security findings، SARIF و scan-run receipts در صورت فعال‌بودن Gate
- SENS-compatible events

Control Plane تصمیم می‌گیرد چه چیزی لازم است؛ Execution Plane کار را انجام می‌دهد؛ Evidence Plane ثابت می‌کند چه اتفاقی افتاده است.

---

# ۷. شناسه‌ها و Versioning

هر Object اجرایی MUST شناسهٔ پایدار داشته باشد.

| Object | الگوی پیشنهادی |
|---|---|
| Task | TASK-YYYYMMDD-NNN |
| Run | RUN-UUID |
| Step | STEP-NNN |
| Evidence | EVD-UUID |
| Approval | APR-UUID |
| Decision | DEC-UUID |
| Artifact | ART-UUID |
| Skill | namespace/name@semver |

قواعد:

- Task می‌تواند چند Run داشته باشد.
- Retry کنترل‌شده یک Run جدید یا Attempt جدید با Parent reference می‌سازد.
- Artifact overwrite بی‌ردیابی SHOULD NOT رخ دهد.
- Schemaها MUST دارای schema_version باشند.
- Skill contract از Semantic Versioning استفاده می‌کند.
- تغییر breaking در Input، Output، Permission یا Evidence contract نیازمند Major version است.

---

# ۸. Core Execution Objects

## ۸.۱. Task Envelope

Task Envelope کوچک‌ترین نمایش استاندارد درخواست است:

- task_id
- objective
- request_type
- requested_outcome
- source
- authority
- constraints
- initial_scope
- external_side_effects
- ambiguity
- created_at

Request Type یکی از این موارد است:

| Type | معنا |
|---|---|
| ASK | پاسخ یا توضیح بدون Mutation |
| INSPECT | بررسی Read-only |
| DIAGNOSE | یافتن علت بدون Fix مگر صریحاً درخواست شود |
| DESIGN | طراحی Artifact یا Architecture |
| CHANGE | ایجاد یا تغییر Local artifact/code |
| RUN | اجرای Tool، Script، Build یا Test |
| EXTERNAL_MUTATION | ارسال، انتشار یا تغییر سیستم بیرونی |
| DESTRUCTIVE | حذف، overwrite یا تغییر دشوار برای بازگشت |
| MONITOR | انتظار یا پایش وضعیت |

## ۸.۲. Task Packet

Task Packet نسخهٔ غنی‌شدهٔ Envelope برای Execution است:

- Objective و expected outcome
- Background لازم
- Acceptance criteria
- Relevant architecture
- Relevant files و versions
- Allowed changes
- Forbidden changes
- Constraints
- Affected domains
- Risk assessment
- Gate plan
- Required approvals
- Expected deliverables
- Expected evidence
- Budget
- Stop conditions
- Context provenance
- current-state summary و target-state delta
- goal contract
- change-scope contract
- selected workflow package/profile
- approved deviations

Fieldهای غیرمرتبط حذف می‌شوند؛ خالی‌کردن Fieldهای مهم برای کوچک‌کردن Context مجاز نیست.

### Runtime Engineering Brief

برای Taskهای DESIGN، CHANGE و RUN که بیش از یک Step معنادار دارند، Orchestrator SHOULD یک Brief حداقلی Compile کند:

- role/capability لازم، بدون persona نمایشی و مطلق؛
- minimum context و provenance؛
- Goal Contract شامل outcome، acceptance و non-goals؛
- Change Scope Contract شامل allowed، restricted و forbidden paths/change-types؛
- active policy، Risk، Authority و approval boundary؛
- expected evidence، budget و stop conditions.

Brief جای Task Packet نیست؛ projection اجرایی کوچک آن برای یک Agent/Run است.

### Goal Contract

Goal Contract باید problem statement، intended users در صورت ارتباط، observable success، acceptance criteria، failure states، unknownها و پرسش‌های باز را از هم جدا کند. «ساختن Feature» بدون outcome قابل‌بررسی Goal کامل نیست.

### Change Scope Contract

Change Scope Contract حداقل این Fieldها را دارد:

- allowed_paths و allowed_change_types؛
- restricted_paths همراه شرط و approval؛
- forbidden_paths و forbidden_side_effects؛
- generated_artifact policy؛
- dependency و migration boundary؛
- deviation protocol.

## ۸.۳. Risk Assessment

شامل:

- risk_level
- confidence
- dimensions
- mandatory_floors
- escalation_reasons
- assumptions
- evidence
- classifier_version

## ۸.۴. Gate Plan

برای هر Gate:

- gate_id
- state
- activation_reason
- blocking
- executor
- reviewer
- evidence_required
- acceptance_rule
- status

## ۸.۵. Execution Plan

شامل:

- ordered_steps
- dependencies
- mutation_boundaries
- approval_checkpoints
- verification_steps
- rollback_or_rollforward
- selected capabilities
- budget
- completion_rule

## ۸.۶. Skill Invocation

شامل:

- skill_id و version
- selected_mode
- input binding
- allowed tools
- granted permissions
- context references
- expected output
- evidence obligations
- attempt budget

## ۸.۷. Evidence Record

شامل:

- evidence_id
- claim_id یا gate_id
- kind
- producer
- command_or_method
- scope
- result
- artifact references
- hash در صورت کاربرد
- timestamp
- environment
- reproducibility
- limitations

## ۸.۸. Approval Record

شامل:

- approval_id
- approver
- authorized_action
- exact_scope
- target
- constraints
- valid_from
- expires_at یا completion boundary
- status
- revocation

## ۸.۹. Run Ledger

Ledger باید حداقل این Eventها را ثبت کند:

- state transition
- classification decision
- gate activation
- approval request و result
- routing decision
- tool invocation receipt
- artifact mutation
- verification result
- repair attempt
- circuit-breaker event
- review disposition
- completion decision

Ledger SHOULD append-only باشد و MUST NOT secrets را بی‌دلیل ذخیره کند.

## ۸.۱۰. Workflow Package

Workflow Package یک ترکیب نسخه‌دار از profile، gates، templates، Skill references و projection rules است. Package:

- MUST شناسه، نسخه، compatibility range و source pin داشته باشد؛
- MUST عملیات install/update/remove را به owning package محدود کند؛
- MUST پیش از mutation، plan یا dry-run قابل‌مشاهده ارائه کند؛
- MUST نصب تکراری را idempotent کند؛
- MUST تعارض و precedence را آشکار کند؛
- MUST NOT Authority یا Approval جدید اعطا کند.

## ۸.۱۱. Security Scope

Security Scope برای هر آزمون امنیتی فعال شامل owner/authorization، target allowlist، target denylist، allowed techniques، prohibited techniques، time window، rate/concurrency budget، data handling، credential handling، stop conditions و reporting destination است.

---

# ۹. Execution State Machine

## ۹.۱. Stateها

| State | معنا |
|---|---|
| RECEIVED | درخواست دریافت شده |
| PRECLASSIFIED | Risk floor اولیه و مرز Discovery تعیین شده |
| DISCOVERING | بررسی Read-only برای فهم Scope |
| NEEDS_CLARIFICATION | Intent یا Scope برای ادامه کافی نیست |
| CLASSIFIED | Risk و Domainها تعیین شده‌اند |
| PLANNED | Gate Plan و Execution Plan آماده‌اند |
| WAITING_APPROVAL | Approval لازم هنوز معتبر نیست |
| READY | Preconditions کامل است |
| EXECUTING | Action در حال انجام است |
| VERIFYING | Evidence در حال تولید یا ارزیابی است |
| REPAIRING | Failure کنترل‌شده در حال اصلاح است |
| CONVERGING | Spec، Plan، Implementation و Evidence در حال هم‌ترازشدن‌اند |
| REVIEWING | Review لازم در حال انجام است |
| BLOCKED | مانع خارجی یا ورودی ضروری وجود دارد |
| ESCALATED | Task به Authority یا Capability بالاتر ارجاع شده |
| DONE | Dynamic DoD برقرار است |
| FAILED | Stop condition نهایی فعال شده |
| CANCELLED | Authority معتبر Task را متوقف کرده |

## ۹.۲. Transitionهای مجاز

~~~text
RECEIVED
  → NEEDS_CLARIFICATION
  → PRECLASSIFIED

PRECLASSIFIED
  → DISCOVERING
  → NEEDS_CLARIFICATION
  → CLASSIFIED

NEEDS_CLARIFICATION
  → PRECLASSIFIED (after a material answer; classification is recomputed)

BLOCKED
  → PRECLASSIFIED (after the blocking condition changes)

ESCALATED
  → PRECLASSIFIED (after an authorized resolution or handoff)

DISCOVERING
  → NEEDS_CLARIFICATION
  → CLASSIFIED
  → BLOCKED

CLASSIFIED
  → PLANNED
  → NEEDS_CLARIFICATION

PLANNED
  → WAITING_APPROVAL
  → READY

WAITING_APPROVAL
  → READY
  → CANCELLED
  → BLOCKED

READY
  → EXECUTING

EXECUTING
  → VERIFYING
  → BLOCKED
  → ESCALATED
  → FAILED

VERIFYING
  → REVIEWING
  → REPAIRING
  → CONVERGING
  → DONE
  → ESCALATED

REPAIRING
  → VERIFYING
  → ESCALATED
  → FAILED

CONVERGING
  → VERIFYING
  → REVIEWING
  → NEEDS_CLARIFICATION
  → ESCALATED

REVIEWING
  → DONE
  → REPAIRING
  → WAITING_APPROVAL
  → ESCALATED

هر State غیرنهایی
  → CANCELLED
  → WAITING_APPROVAL (if authority expires or scope changes; stop side effects first)

WAITING_APPROVAL
  → PRECLASSIFIED (if approval changes scope; never reuse stale classification)
~~~

## ۹.۳. Invariantها

- DONE فقط از طریق Completion Evaluator قابل ثبت است.
- PRECLASSIFIED فقط Risk floor و Discovery boundary می‌سازد و مجوز Execution نیست.
- CLASSIFIED نتیجهٔ نهایی مبتنی بر Discovery است؛ مگر اینکه مستند شود Discovery دیگری لازم نبوده است.
- Action دارای Side Effect پیش از READY ممنوع است.
- READY فقط با Authority و Preconditions معتبر ایجاد می‌شود.
- تغییر Scope پس از Approval می‌تواند Run را دوباره به WAITING_APPROVAL برگرداند.
- FAILED با BLOCKED یکسان نیست؛ BLOCKED ممکن است پس از تغییر External State ادامه یابد.
- ESCALATED به معنی Failure نیست؛ یعنی Orchestrator فعلی Authority یا Capability کافی ندارد.
- CONVERGING فقط اختلاف‌ها را در Scope مصوب حل می‌کند و حق گسترش Scope یا بازنویسی Intent را ندارد.

---

# ۱۰. Intake و Scope Protocol

Orchestrator در Intake باید:

۱) Objective را به Outcome قابل‌بررسی تبدیل کند؛  
۲) Request Type را تعیین کند؛  
۳) Mutation و External Side Effect را آشکار کند؛  
۴) Targetها را دقیق کند؛  
۵) Constraint و Non-goal را ثبت کند؛  
۶) Authority موجود را از Authority موردنیاز جدا کند؛  
۷) Ambiguity مؤثر بر نتیجه را تشخیص دهد؛  
۸) با اطلاعات موجود Preliminary Classification و Mandatory Floor اولیه را تعیین کند؛  
۹) Discovery خواندنی را در مرز Risk و Authority اولیه انجام دهد؛  
۱۰) Final Classification و Affected Domainها را با Evidence جدید تعیین کند؛  
۱۱) Goal Contract و Change Scope Contract متناسب را Compile کند؛  
۱۲) Scope proposal را برای Actionهای نیازمند Approval آماده کند.

Clarification فقط وقتی Blocking است که پاسخ آن نتیجه، Scope، Risk یا Authority را به‌طور معنادار تغییر دهد.

## ۱۰.۱. Clarification Gate

Clarification Gate خروجی یکی از این حالت‌ها را دارد:

- `CLEAR`: ambiguity باقیمانده اجرای معتبر را تغییر نمی‌دهد؛
- `ASSUMPTION_BOUNDED`: فرض محدود، آشکار و قابل‌برگشت ثبت شده است؛
- `QUESTION_REQUIRED`: پاسخ کاربر/مالک برای outcome، scope، risk یا authority ضروری است؛
- `BLOCKED`: پاسخ یا Source لازم در دسترس نیست.

Gate MUST سؤال‌هایی را که صرفاً ترجیح جزئی یا ceremony ایجاد می‌کنند Blocking نکند. پرسش‌های مؤثر باید یک‌جا و پیش از Mutation مطرح شوند؛ کشف ambiguity جدید پس از Mutation می‌تواند reapproval را فعال کند.

Orchestrator MUST NOT:

- درخواست Diagnose را خودکار به Fix تبدیل کند؛
- Approval برای بررسی را Approval برای Mutation تلقی کند؛
- اجازهٔ تغییر یک فایل را به کل Repository تعمیم دهد؛
- Permission ابزار را به Permission کاربر تبدیل کند؛
- عملیات بیرونی را با عنوان «مرحلهٔ طبیعی کار» پنهان کند.

---

# ۱۱. Risk Classifier v0.8

## ۱۱.۱. Two-Pass Classification

Classification در دو Pass انجام می‌شود:

### Pass A — Preliminary Classification

قبل از Discovery، Classifier با Objective، Request Type، Targetهای اعلام‌شده، Side Effectهای قابل‌مشاهده و Mandatory Floorهای شناخته‌شده یک سطح اولیه تولید می‌کند.

خروجی Pass A:

- provisional_level
- known_mandatory_floors
- uncertainty
- allowed_discovery
- forbidden_discovery
- approval_needed_for_discovery

Preliminary Classification:

- MUST پیش از Discovery دارای Side Effect انجام شود؛
- MUST NOT مجوز Execution تلقی شود؛
- SHOULD برای Discovery کاملاً Read-only سبک باشد؛
- اگر Target یا Authority مبهم است، Discovery را محدود یا Task را به NEEDS_CLARIFICATION منتقل می‌کند.

### Pass B — Final Classification

پس از Discovery، Classifier با Evidence جدید، Affected Domainها، Architecture impact، Reversibility و Uncertainty سطح نهایی را تعیین می‌کند.

Final Classification:

- MUST تمام Mandatory Floorهای اثبات‌شده را حفظ کند؛
- MAY با Evidence جدید سطح اولیه را افزایش دهد؛
- MAY سطح اولیه را فقط وقتی کاهش دهد که Floor اولیه با Evidence رد شده و Rationale ثبت شود؛
- MUST ورودی Gate Compiler باشد.

این طراحی ترتیب رسمی را چنین تثبیت می‌کند:

~~~text
INTAKE
→ PRELIMINARY CLASSIFICATION
→ BOUNDED DISCOVERY
→ FINAL CLASSIFICATION
→ AFFECTED DOMAINS
→ GATE COMPILATION
~~~

## ۱۱.۲. ابعاد Risk

هر Dimension از 0 تا 4 ارزیابی می‌شود:

| Dimension | پرسش |
|---|---|
| Reversibility | بازگشت چقدر دشوار است؟ |
| Blast Radius | چند کاربر، سرویس یا Artifact تحت‌تأثیر است؟ |
| Data | آیا دادهٔ پایدار، Migration یا Integrity درگیر است؟ |
| Security | آیا Trust boundary، Auth، Secret یا Privilege درگیر است؟ |
| Privacy / Safety | آیا دادهٔ حساس یا پیامد انسانی جدی وجود دارد؟ |
| Availability | آیا Production یا سرویس حیاتی ممکن است مختل شود؟ |
| Public Contract | آیا API، Schema، Plugin contract یا compatibility تغییر می‌کند؟ |
| Architecture | آیا Boundary یا تصمیم سخت برای بازگشت تغییر می‌کند؟ |
| External Effect | آیا پیام، انتشار، خرید یا Mutation بیرونی رخ می‌دهد؟ |
| Operational Complexity | آیا Deployment، concurrency یا distributed state درگیر است؟ |
| Uncertainty | آیا اطلاعات، تست یا شناخت سیستم ناکافی است؟ |

Risk نهایی میانگین سادهٔ Dimensionها نیست. Mandatory Floorها بر Average مقدم‌اند.

## ۱۱.۳. Mandatory Floorها

### Floor R4

حداقل R4 وقتی یکی از موارد زیر وجود دارد:

- عملیات destructive یا irreversible روی Production یا دادهٔ مهم
- تغییر safety-critical یا privacy-critical
- تغییر کنترل دسترسی، credential، cryptographic boundary یا secret handling با Blast Radius بالا
- Migration پرخطر بدون Rollback/Roll-forward اثبات‌شده
- انتشار عمومی یا External Mutation با پیامد حقوقی/مالی جدی
- Recovery اضطراری روی سیستم حیاتی

### Floor R3

حداقل R3 برای:

- Architecture boundary مهم
- Public API یا Plugin contract
- Schema migration قابل‌توجه
- Security boundary با دامنهٔ محدودتر
- Major dependency یا platform change
- Production configuration با اثر واقعی
- Cross-service integration
- Performance requirement بحرانی

### Floor R2

حداقل R2 برای:

- Feature یا Bugfix کاربرمحور با رفتار واقعی
- تغییر persistence محدود
- dependency update غیرساده
- refactor چندماژولی قابل‌بازگشت
- UI flow مهم

### R0 و R1

R0 فقط وقتی مجاز است که تغییر تقریباً بدون اثر رفتاری، کوچک، محلی و به‌سادگی قابل‌برگشت باشد.

R1 برای تغییر محدود، قابل‌برگشت و بدون Mandatory Floor بالاتر است.

## ۱۱.۴. Confidence

| Confidence | رفتار |
|---|---|
| 0.80–1.00 | Classification قابل‌استفاده |
| 0.50–0.79 | Discovery یا Assumption صریح لازم |
| کمتر از 0.50 | اجرای Mutation متوقف؛ Clarify یا Escalate |

اگر Uncertainty به‌طور منطقی بتواند Risk را یک سطح بالا ببرد، سطح بالاتر تا زمان رفع ابهام اعمال می‌شود.

## ۱۱.۵. Downgrade

- Mandatory Floor بدون Evidence جدید قابل Downgrade نیست.
- Downgrade باید reason، evidence و decider داشته باشد.
- R4 به R3 SHOULD نیازمند Human Review باشد.
- کم‌بودن LOC دلیل Downgrade نیست.
- بزرگ‌بودن Diff به‌تنهایی دلیل R3 یا R4 نیست.

## ۱۱.۶. خروجی قابل‌توضیح

Classifier باید علاوه بر Level، دلیل کوتاه تولید کند:

~~~text
Risk: R3
Because:
- public API contract changes
- migration is required
- rollback is available
Not R4 because:
- no destructive production operation
- no sensitive-data boundary change
Confidence: 0.88
~~~

---

# ۱۲. Affected-Domain Detection

Domainهای استاندارد:

- architecture
- application_logic
- frontend
- ux_accessibility
- api_contract
- data_migration
- security
- privacy_safety
- performance_scale
- observability_sens
- dependency_license
- ci_cd
- documentation
- operations_recovery
- external_integration
- agentic_tool_security

هر Domain شامل:

- affected: true/false/unknown
- reason
- impact_level
- required_context
- candidate_gates

Unknown MUST NOT به‌صورت خودکار False تفسیر شود.

---

# ۱۳. Quality Gate Compiler v0.8

## ۱۳.۱. وضعیت Gate

به‌جای یک علامت منفرد، Gate این Dimensionها را دارد:

- required: true/false
- automated: true/false
- independent_review: true/false
- human_approval: true/false
- blocking: true/false
- condition

این مدل حالت‌های R+IR و R+HA را بدون ابهام نمایش می‌دهد.

## ۱۳.۲. الگوریتم Compile

~~~text
INPUT:
  risk assessment
  affected domains
  acceptance criteria
  project policies
  environment
  requested side effects

START with v0.7 base matrix
APPLY mandatory risk gates
EVALUATE every conditional star
APPLY domain-specific gates
APPLY policy additions
APPLY approval rules
REMOVE only gates proven not applicable
DEFINE required evidence for each active gate
ORDER gates by dependency and mutation boundary
OUTPUT explainable Gate Plan
~~~

## ۱۳.۳. قانون ستاره

هر Gate دارای ستاره در v0.7 MUST یکی از این خروجی‌ها را داشته باشد:

- ACTIVE همراه Trigger
- NOT_APPLICABLE همراه Rationale
- UNRESOLVED و در نتیجه Blocking

Gate ستاره‌دار حق ندارد بی‌صدا حذف شود.

## ۱۳.۴. Triggerهای نمونه

| Domain / Change | Gateهای فعال |
|---|---|
| auth یا permission | Security، targeted tests، regression، independent review برحسب Risk |
| schema change | Migration، compatibility، integrity، recovery |
| public API | Contract، regression، docs، versioning |
| new dependency | Dependency، security، license، compatibility |
| user flow | UX، accessibility، UI regression |
| latency target | Performance و workload verification |
| production operation | Recovery، observability، approval |
| agent tool execution | Agentic security، permission، tool receipt |
| spec/plan/task change | Cross-artifact consistency، deviation check، convergence |
| repository bootstrap | current-state inventory، native-file preservation، build-stays-green |
| data integration | schema، migration، write/read proof، access-control check |
| security validation | authorization، security scope، finding normalization، scan evidence |

## ۱۳.۵. Gate Result

Gate status:

- PENDING
- PASS
- FAIL
- WAIVED
- NOT_APPLICABLE

WAIVED فقط با:

- Authority معتبر
- Rationale
- Scope
- Risk acknowledgement
- Expiration یا Task boundary

ممکن است. Gate قانونی یا Safety-critical قابل Waive نیست مگر Rule بالادست اجازه دهد.

## ۱۳.۶. Anti-Overengineering Gate

پیش از فعال‌کردن Artifact، Layer، Dependency، Agent یا Review اضافی، Compiler باید بپرسد:

۱) کدام Risk، Acceptance یا Failure mode آن را لازم کرده است؟  
۲) آیا راه کوچک‌تر Evidence کافی تولید می‌کند؟  
۳) هزینهٔ نگهداری و context آن چیست؟  
۴) آیا حذف آن Completion را واقعاً غیرقابل‌اثبات می‌کند؟

خروجی `NECESSARY`، `OPTIONAL_WITH_RATIONALE` یا `REMOVE` است. این Gate اجازهٔ حذف controls اجباری R3/R4، قانون یا Safety constraint را ندارد.

---

# ۱۴. Adaptive Workflow Profiles

| Risk | Profile | حداقل فرایند |
|---|---|---|
| R0 | MICRO | Scope کوتاه، Action محدود، targeted verification |
| R1 | QUICK | Plan سبک، relevant checks، rollback ساده |
| R2 | STANDARD | Acceptance، implementation، tests، relevant gates، review |
| R3 | CONTROLLED | Spec، architecture impact، rollback، independent review، CI |
| R4 | CRITICAL | formal approval، independent verification، recovery evidence، controlled execution |

Profile یک Template است، نه جایگزین Gate Compiler.

## ۱۴.۱. Workflow Profileهای موضوعی

Risk Profile می‌تواند با یک profile موضوعی ترکیب شود، مشروط به اینکه Risk floor حفظ شود:

- `FEATURE`: specify → clarify → plan → tasks → implement → analyze → converge؛
- `BUG`: assess → reproduce → fix → targeted test → regression → converge؛
- `IDEA_ASSESSMENT`: intake → research → define → shape → decide؛
- `REPOSITORY_BOOTSTRAP`: inventory → current-state → target-state delta → projection → verify؛
- `DATA_INTEGRATION`: contract → migration/recovery → write proof → read proof → access check؛
- `SECURITY_VALIDATION`: authorize → scope → execute adapter → normalize findings → verify coverage → disposition.

`FEATURE` مراحل را برحسب Risk و اندازهٔ کار slice می‌کند. `IDEA_ASSESSMENT` ممکن است با `GO`، `CLARIFY` یا `KILL` پایان یابد و الزاماً به Implementation منتهی نمی‌شود.

## ۱۴.۲. Workflow Package Resolution

ترتیب Resolution:

۱) project override معتبر؛  
۲) package/profile صریح Task؛  
۳) extensionهای سازگار؛  
۴) SAGE core default.

هر Merge باید origin هر Rule و conflict disposition را حفظ کند. Package نصب‌شده باید version-pinned، قابل dry-run، idempotent و removal آن ownership-aware باشد.

## ۱۴.۳. R0 نباید متورم شود

R0 به‌طور پیش‌فرض نیاز ندارد:

- ADR
- Council
- Full repository analysis
- Full regression
- Handoff مستقل
- Documentation گسترده

## ۱۴.۴. R4 نباید با Confidence مدل ساده شود

Confidence بالای Agent، Approval یا Independent Review لازم را حذف نمی‌کند.

---

# ۱۵. Dynamic Definition of Done Compiler

برای هر Run، DoD از Gate Plan Compile می‌شود:

~~~text
DONE =
  all required acceptance criteria satisfied
  AND all blocking gates are PASS or validly WAIVED
  AND required evidence exists and is in scope
  AND required reviews are resolved
  AND required approvals are valid
  AND no blocking failure remains
  AND cross-artifact inconsistencies are resolved or explicitly accepted
  AND implementation matches the approved spec or an approved deviation
  AND required state/documentation is updated
  AND completion scope equals approved scope
~~~

Completion Evaluator MUST:

- Evidence را به Claim مربوط وصل کند؛
- stale یا out-of-scope Evidence را رد کند؛
- PASS خوداظهاری را کافی نداند؛
- Gateهای NOT_APPLICABLE را با Rationale بررسی کند؛
- Approval منقضی یا محدودتر از Scope را رد کند؛
- Result را با دلیل ثبت کند.
- coverage انجام‌شده و انجام‌نشده را ثبت کند؛
- failure-only artifact را به‌عنوان جایگزین نتیجهٔ موفق نپذیرد، اما آن را برای diagnosis حفظ کند؛
- requirement checklist را مانند assertionهای قابل‌ردیابی به Evidence متصل کند.

---

# ۱۶. Context Packaging Protocol

## ۱۶.۱. Context Layers

### Layer 0 — Authority and Safety

- active authority، approval boundary و forbidden actions
- platform/system constraints
- sensitive-data handling

### Layer 1 — Routing Context

- objective
- short description
- risk
- affected domains
- candidate capabilities

### Layer 2 — Execution Context

- acceptance criteria
- relevant architecture
- allowed/forbidden changes
- relevant files
- active policies
- gate obligations

### Layer 3 — Current-State and Target-State Delta

- current behavior و verified repository state
- intended target state
- exact delta، non-goals و approved deviations

### Layer 4 — Conditional References

- detailed schema
- provider documentation
- migration procedure
- security policy
- design system
- domain-specific references

### Layer 5 — Evidence and Continuation

- prior relevant evidence و limitations
- current run state، remaining budget و stop conditions
- handoff فقط در صورت نیاز واقعی به ادامه‌دهنده

Agent فقط Layerهای لازم را دریافت می‌کند.

## ۱۶.۲. Instruction Projection

Authoritative rules می‌توانند به فایل‌های بومی Provider مانند `AGENTS.md`، `CLAUDE.md`، Cursor rules یا Copilot instructions projection شوند. Projection:

- MUST source IDs و version/hash مرجع را ثبت کند؛
- MUST معنی Rule را حفظ و conflict را آشکار کند؛
- MUST فقط syntax و granularity موردنیاز Provider را تغییر دهد؛
- MUST NOT Rule حاکم یا Authority تازه بسازد؛
- SHOULD با regeneration قابل‌بازتولید باشد؛
- MUST تفاوت دستی بعدی را به‌عنوان drift گزارش کند، نه اینکه بی‌صدا overwrite کند.

## ۱۶.۳. Context Item Contract

هر Context item SHOULD شامل:

- source
- version یا hash
- relevance
- freshness
- sensitivity
- authority
- load_condition

## ۱۶.۴. ممنوعیت‌ها

- کل Repository بدون دلیل به Agent داده نشود.
- Secret وارد Context نشود مگر ضرورت و Authority روشن وجود داشته باشد.
- Summary جای Source حیاتی را بدون Reference نگیرد.
- Chat history تنها Source of Truth نباشد.
- Skill همهٔ referenceها را به‌طور پیش‌فرض Load نکند.

---

# ۱۷. Skill Contract v0.8

## ۱۷.۱. تعریف

Skill مجموعه‌ای از Guidance و Resourceهای قابل‌بازاستفاده است که تصمیم یا اجرای Agent را برای یک نوع Task بهبود می‌دهد.

Skill:

- Agent نیست؛
- Model نیست؛
- Tool نیست؛
- Permission نیست؛
- Workflow کامل سازمان نیست، مگر صریحاً Orchestrator Skill باشد.

## ۱۷.۲. سه سطح Progressive Disclosure

۱) Discovery Metadata: نام و Description برای Routing  
۲) Entrypoint: Constraintها، Workflow و Routing لازم  
۳) Conditional Resources: reference، script و asset فقط هنگام نیاز

Skill بزرگ MUST NOT همهٔ منابع خود را همیشه وارد Context کند.

## ۱۷.۳. Portable Descriptor

SAGE اطلاعات قابل‌حمل را در **sage.skill.yaml** یا Skill Registry نگهداری می‌کند. فایل بومی Provider دست‌نخورده می‌ماند.

Fieldهای اصلی:

- schema_version
- id
- version
- title
- description
- intents
- domains
- risk_range
- invocation_policy
- inputs
- outputs
- preconditions
- side_effects
- permissions
- required_capabilities
- optional_capabilities
- tools
- context_requirements
- procedure_ref
- evidence_contract
- failure_modes
- retry_policy
- stop_conditions
- compatibility
- native_bindings

## ۱۷.۴. Invocation Policy

| Policy | معنا |
|---|---|
| implicit | Router در صورت Match می‌تواند Skill را انتخاب کند |
| explicit | فقط با درخواست صریح فعال می‌شود |
| orchestrator_only | فقط Control Plane می‌تواند فعال کند |
| forbidden_in_environment | در Environment مشخص قابل‌استفاده نیست |

Implicit invocation مجوز Mutation ایجاد نمی‌کند.

## ۱۷.۵. Input Contract

Input باید:

- required و optional fieldها را مشخص کند؛
- type و validation داشته باشد؛
- حساسیت داده را اعلام کند؛
- از Context نامرتبط جلوگیری کند؛
- missing critical input را به Clarification یا Block تبدیل کند.

## ۱۷.۶. Output Contract

Output باید:

- deliverable type
- artifact references
- structured result
- limitations
- unresolved items
- evidence references

را مشخص کند.

## ۱۷.۷. Permission Contract

Skill فقط Permission موردنیاز را اعلام می‌کند:

~~~text
read:
  - repository
write:
  - scoped_workspace_files
execute:
  - tests
network:
  - none
external_mutation:
  - none
~~~

Policy Engine تصمیم می‌گیرد Permission واقعاً Grant می‌شود یا نه.

Skill MUST NOT:

- Scope کاربر را گسترش دهد؛
- Approval را فرض کند؛
- Tool available را Tool authorized بداند؛
- fallback پرخطر را پنهانی اجرا کند.

## ۱۷.۸. Evidence Contract

Skill باید مشخص کند:

- چه Claimهایی تولید می‌کند؛
- هر Claim به چه Evidenceای نیاز دارد؛
- چه چیزی PASS و FAIL است؛
- چه Limitationهایی باقی می‌ماند.

## ۱۷.۹. Failure Contract

Failure Modeهای Skill باید قابل‌طبقه‌بندی باشند:

- INVALID_INPUT
- PRECONDITION_FAILED
- PERMISSION_DENIED
- TOOL_UNAVAILABLE
- EXECUTION_FAILED
- VERIFICATION_FAILED
- UNSUPPORTED_CASE
- BUDGET_EXHAUSTED
- EXTERNAL_STATE_CHANGED

Skill نباید Failure را به Success ظاهری تبدیل کند.

## ۱۷.۱۰. Skill Composition

- هر Skill باید Input و Output قابل‌اتصال داشته باشد.
- Skill downstream فقط Output معتبر upstream را مصرف کند.
- Permissionها جمع ساده نمی‌شوند؛ هر مرحله جداگانه بررسی می‌شود.
- Circular dependency بین Skillها ممنوع است.
- Composition باید Stop condition داشته باشد.

## ۱۷.۱۱. Native Binding

نمونهٔ Mapping برای Codex:

| SAGE concept | Codex-native location |
|---|---|
| discovery name/description | YAML frontmatter در SKILL.md |
| entrypoint | body فایل SKILL.md |
| conditional guidance | references/ |
| deterministic helper | scripts/ |
| output resources | assets/ |
| UI metadata | agents/openai.yaml |
| portable SAGE policy | sage.skill.yaml یا central registry |

SAGE MUST NOT Fieldهای اختصاصی خود را به frontmatter بومی تحمیل کند اگر Provider آن‌ها را پشتیبانی نمی‌کند.

## ۱۷.۱۲. Skill Conformance و Dry Run

Skill جدید یا تغییر معنادار Skill باید علاوه بر syntax validation، با یک درخواست واقع‌گرایانه بررسی شود. Conformance باید نشان دهد:

- routing description بیش‌ازحد گسترده نیست؛
- Skill intent و Scope کاربر را حفظ می‌کند؛
- permission را از capability جدا می‌کند؛
- referenceهای شرطی فقط هنگام نیاز Load می‌شوند؛
- script جدید روی ورودی واقعی یا fixture معتبر اجرا شده است؛
- dry run یا plan mode هیچ Mutation اعلام‌نشده ایجاد نمی‌کند؛
- stop condition و failure result قابل‌مشاهده‌اند.

Self-review مفید است اما در Skill پرریسک جای independent forward-test را نمی‌گیرد.

---

# ۱۸. Skill Discovery و Routing

## ۱۸.۱. Hard Filters

Skill قبل از Score باید این فیلترها را پاس کند:

- intent match
- domain match
- supported risk range
- compatible environment
- available required capabilities
- policy eligibility
- permission eligibility
- input satisfiable
- version compatibility

ردشدن هر Hard Filter یعنی Skill Candidate نیست.

## ۱۸.۲. Scoring

پس از Hard Filter، Router MAY براساس این عوامل Score دهد:

- task fit
- evidence quality history
- context cost
- latency
- monetary cost
- local/privacy preference
- tool availability
- prior success on similar tasks

وزن‌ها Project Policy هستند، نه قانون جهانی.

## ۱۸.۳. Routing Receipt

Router باید ثبت کند:

- candidates considered
- candidates rejected و reason
- selected skill/agent/tool
- required permissions
- expected evidence
- fallback

## ۱۸.۴. نبود Candidate

اگر Candidate واجد شرایط وجود ندارد:

- Orchestrator نباید Skill نزدیک اما ناسازگار را تحمیل کند؛
- MAY بدون Skill و با Agent عمومی ادامه دهد، اگر Policy و Risk اجازه دهد؛
- در غیر این صورت BLOCK یا ESCALATE می‌کند.

---

# ۱۹. Agent، Model و Tool Routing

تعریف:

~~~text
Agent =
  Model
  + Role
  + Skills
  + Tools
  + Context
  + Policies

Runtime Agent Session =
  Agent
  + Task Assignment
  + Granted Authority
  + Run Budget
~~~

تعریف Agent همان تعریف Frozen در v0.7 باقی می‌ماند. Authority ویژگی دائمی Agent یا Capability آن نیست؛ یک Grant محدود، قابل‌لغو و وابسته به Task/Run است.

Routing باید Capability-Based باشد.

## ۱۹.۱. Hard Requirements

- context capacity
- required modality
- repository access
- tool access
- privacy constraint
- local/cloud policy
- required independence
- supported output contract

## ۱۹.۲. Independence

برای R3 و R4، Independent Review باید حداقل در یکی از این ابعاد استقلال واقعی داشته باشد:

- Agent instance
- context packaging
- role/instructions
- model family
- evidence source
- implementation involvement

اجرای دوبارهٔ همان Prompt با همان Context، استقلال قوی محسوب نمی‌شود.

Reviewer بهتر است ابتدا Evidence خام، Acceptance و Diff را ببیند؛ Conclusion پیاده‌ساز فقط وقتی لازم است داده شود تا Anchoring کاهش یابد.

## ۱۹.۳. Tool Rule

هر Tool invocation باید:

- purpose
- exact target
- permission basis
- expected side effect
- timeout/budget
- receipt

داشته باشد.

## ۱۹.۴. Agent Capability Contract

Agent Registry باید برای هر Agent حداقل این اطلاعات را نگهداری کند:

- schema_version
- agent_id و version
- role profiles
- model binding
- declared capabilities
- capability evidence
- supported modalities
- context limits
- available tool classes
- supported environments
- privacy/locality modes
- maximum eligible risk
- review independence attributes
- health status
- compatibility

Capability declaration به‌تنهایی قابل‌اعتماد نیست. Capability مهم SHOULD با benchmark، verified run یا Evidence معتبر پشتیبانی شود.

Agent descriptor MUST NOT Authority دائمی ذخیره کند. Authority فقط هنگام ساخت Runtime Agent Session از Approval و Policy مشتق می‌شود.

## ۱۹.۵. Tool Registry Contract

Tool Registry برای هر Tool حداقل شامل:

- schema_version
- tool_id و version
- capabilities
- side_effect_class
- input/output schema references
- permission requirements
- supported environments
- network behavior
- idempotency support
- timeout defaults
- evidence outputs
- rollback/recovery support
- native binding

Side Effect Class:

| Class | معنا |
|---|---|
| READ_ONLY | بدون Mutation موردانتظار |
| LOCAL_REVERSIBLE | تغییر محلی قابل‌بازگشت در Scope مشخص |
| EXTERNAL_MUTATION | تغییر سیستم، داده یا مخاطب بیرونی |
| LOCAL_DESTRUCTIVE | حذف یا تغییر محلی دشوار برای بازگشت |
| SECURITY_ACTIVE | اقدام امنیتی فعال با Security Scope و Authorization |

Tool بدون Side Effect Class معتبر MUST NOT به‌طور خودکار Route شود.

## ۱۹.۶. Provider Adapter Interface

Provider Adapter باید یک Interface عمومی و Provider-neutral ارائه کند:

- describe_capabilities
- validate_configuration
- prepare_request
- execute
- stream_events
- cancel
- normalize_result
- health_check

Adapter:

- MUST semantics مربوط به Task، Scope، Authority و Evidence را حفظ کند؛
- MUST NOT Permission را هنگام Mapping گسترش دهد؛
- MUST native errorها را به Error Taxonomy نگاشت کند؛
- SHOULD idempotency و cancellation را در صورت پشتیبانی Provider عبور دهد؛
- MUST Provider-specific metadata را از Portable Contract جدا نگه دارد.

---

# ۲۰. Execution Step Contract

هر Step:

- step_id
- objective
- type
- inputs
- expected outputs
- allowed mutations
- forbidden mutations
- preconditions
- selected agent/skill/tool
- verification
- rollback
- timeout
- status

## ۲۰.۱. Spec Deviation Protocol

اگر واقعیت Repository یا اجرای معتبر، Implementation دقیق Spec را ناممکن یا نادرست کند:

۱) deviation پیش از گسترش Mutation ثبت می‌شود؛  
۲) affected acceptance، risk، API/data/UI contract و migration مشخص می‌شود؛  
۳) گزینهٔ کوچک‌تر یا rollback بررسی می‌شود؛  
۴) Spec یا Approval در صورت تغییر outcome/scope به‌روزرسانی می‌شود؛  
۵) deviation به Evidence و final report متصل می‌شود.

Agent MUST NOT برای حفظ ظاهر انطباق، Spec یا کد را بی‌صدا تحریف کند.

## ۲۰.۲. Build-Stays-Green

Execution Plan SHOULD به sliceهای کوچکی شکسته شود که پس از هر slice، entrypoint مناسب build/test/lint قابل اجرا بماند. اگر یک migration ناگزیر به حالت گذرا نیاز دارد، مدت، containment و recovery آن باید صریح باشد.

## ۲۰.۳. Tool/MCP Integration Gate

پیش از افزودن Tool یا MCP Server:

- منبع رسمی/نگهداری‌شده و نسخه pin شود؛
- command/config دقیق و scope پروژه مشخص شود؛
- secrets فقط از secret mechanism مجاز دریافت شوند؛
- allowed tools و denied tools تعیین شوند؛
- connection، typed response، error handling و timeout آزموده شوند؛
- Tool receipt و limitation ثبت شود؛
- removal/rollback مسیر مشخص داشته باشد.

## ۲۰.۴. Data Path Proof

برای integration داده‌ای، schema/config success کافی نیست. Evidence حداقل باید یک write کنترل‌شده، read-back، expected value comparison و در صورت ارتباط access-control/tenant boundary را اثبات کند. دادهٔ fixture باید غیرحساس و rollbackپذیر باشد.

## ۲۰.۵. Conditional Engineering Methods

این روش‌ها فقط با Trigger مربوط فعال می‌شوند و برای هر Task اجباری نیستند:

| Method | Trigger | Contract / Evidence |
|---|---|---|
| Product Brief / PRD | محصول یا Feature با کاربران و outcome چندگانه | problem، users، success metrics، scope، non-goals، acceptance و unknowns |
| UI/UX Design Contract | تغییر تجربه یا رابط کاربر | flow، hierarchy، responsive states، loading/empty/error/success، accessibility، tokens و visual verification |
| Risk-First Unknown Resolution | unknown پرریسک در Plan | آزمون کوچک پیش از وابسته‌کردن مراحل بعدی؛ نتیجه و تصمیم ثبت شود |
| Plan Sanity Check | Plan چندمرحله‌ای | dependency order، feasibility، verification، rollback و کافی‌بودن budget بررسی شود |
| Safe Code Cleanup | حذف کد یا dependency | caller/import/dynamic-reference inspection، حذف محدود و آزمون مرتبط؛ نبود reference متنی به‌تنهایی اثبات dead code نیست |
| Commit Planning | کاربر Commit خواسته باشد | تقسیم منطقی diff، بررسی staged files و secrets، پیام متناسب؛ برنامه مجوز commit/push نیست |
| Executable Guardrail Adapter | Provider hook یا policy runner لازم باشد | trigger، scope، command، timeout، failure semantic و dry-run مشخص؛ hook نباید اختیار تازه ایجاد کند |

Build-Stays-Green فقط entrypointهای مرتبط را اجرا می‌کند. Failure-only screenshots/traces می‌توانند حجم artifact را کم کنند، اما نتیجهٔ آزمون‌های موفق و Coverage Disclosure باید همچنان ثبت شوند.

## ۲۰.۶. Mutation Boundary

پیش از اولین Mutation:

۱) Scope resolved باشد؛  
۲) Risk و Gate Plan آماده باشد؛  
۳) Approval لازم معتبر باشد؛  
۴) exact target بررسی شده باشد؛  
۵) rollback یا recovery متناسب تعریف شده باشد؛  
۶) Evidence plan مشخص باشد.

## ۲۰.۷. Idempotency

External Mutation و عملیات retryپذیر SHOULD دارای Idempotency Key باشند. اگر مقصد از Idempotency پشتیبانی نمی‌کند، Ledger باید امکان تشخیص اجرای قبلی را فراهم کند.

## ۲۰.۸. Scope Drift

اگر Execution نیازمند تغییر خارج از Plan شد:

- Step متوقف می‌شود؛
- impact دوباره طبقه‌بندی می‌شود؛
- Gate Plan به‌روزرسانی می‌شود؛
- Approval جدید در صورت نیاز اخذ می‌شود.

---

# ۲۱. Verify–Diagnose–Repair Protocol

## ۲۱.۱. Loop

~~~text
EXECUTE
  ↓
VERIFY
  ↓ FAIL
CAPTURE FAILURE SIGNATURE
  ↓
FORM HYPOTHESIS
  ↓
REPAIR WITHIN SCOPE
  ↓
RE-VERIFY
  ↓
PASS / CONTINUE / CIRCUIT BREAK
~~~

## ۲۱.۲. Repair Attempt

Attempt معتبر باید:

- فرضیهٔ مشخص داشته باشد؛
- Change قابل‌ردیابی ایجاد کند؛
- Evidence جدید تولید کند؛
- Scope را حفظ کند؛
- نتیجه را با Failure signature قبلی مقایسه کند.
- expected behavior را از actual behavior جدا ثبت کند؛
- hypothesisها را برحسب احتمال و هزینهٔ آزمون اولویت دهد؛
- regression testی ایجاد کند که بدون Fix شکست بخورد، هرگاه از نظر Risk و هزینه متناسب باشد.

تکرار همان Fix بدون Evidence جدید Attempt مفید محسوب نمی‌شود.

## ۲۱.۳. Budget

Budget می‌تواند شامل:

- max_primary_attempts
- max_independent_attempts
- max_elapsed_time
- max_cost
- max_tokens
- max_tool_failures

باشد.

Baseline پیشنهادی و قابل Override:

| Risk | Primary repair | Independent diagnosis |
|---|---:|---|
| R0 | 1 | معمولاً لازم نیست |
| R1 | 2 | Conditional |
| R2 | 3 | پس از Stall یا uncertainty بالا |
| R3 | 2 | هنگام Stall لازم |
| R4 | 1 | پیش از Repair اضافی لازم؛ Reapproval ممکن است |

این اعداد Policy default هستند و نباید جای Stop condition واقعی را بگیرند.

## ۲۱.۴. No-Progress Detection

No Progress وقتی یکی از موارد زیر رخ دهد:

- failure signature بدون تغییر معنادار تکرار شود؛
- patch hash یا solution strategy تکرار شود؛
- Evidence جدید تولید نشود؛
- فرضیهٔ تازه‌ای وجود نداشته باشد؛
- Tool failure مشابه از threshold عبور کند؛
- remaining budget برای Verification معتبر کافی نباشد.

## ۲۱.۵. Circuit Breaker

در Circuit Break:

۱) Mutation بیشتر متوقف می‌شود؛  
۲) state و evidence snapshot ثبت می‌شود؛  
۳) rollback ایمن در صورت لزوم انجام می‌شود؛  
۴) independent diagnosis یا specialist انتخاب می‌شود؛  
۵) در R4 ممکن است Approval جدید لازم شود؛  
۶) در نبود مسیر معتبر، ESCALATE یا FAILED ثبت می‌شود.

Independent diagnosis بهتر است ابتدا raw evidence را دریافت کند، نه نتیجه‌گیری Agent قبلی.

## ۲۱.۶. Cross-Artifact Consistency و Convergence

Analyzer رابطهٔ Requirement → Spec → Plan → Task → Change → Evidence را بررسی می‌کند و findingهای `MISSING`، `CONFLICT`، `STALE`، `UNPROVEN` یا `OUT_OF_SCOPE` می‌سازد.

Convergence Engine فقط در budget و Scope معتبر:

۱) finding را به Source و affected artifact متصل می‌کند؛  
۲) کوچک‌ترین اصلاح معتبر را پیشنهاد یا اجرا می‌کند؛  
۳) Spec Deviation Protocol را در صورت تغییر intent/outcome فعال می‌کند؛  
۴) consistency و gates مرتبط را دوباره بررسی می‌کند؛  
۵) در no-progress، authority conflict یا budget exhaustion متوقف می‌شود.

Convergence به معنی بازنویسی بی‌پایان برای رسیدن به ظاهر هماهنگ نیست؛ اختلاف واقعی می‌تواند به `BLOCKED` یا `REJECTED_WITH_RATIONALE` منتهی شود.

---

# ۲۲. Review Protocol

Review فقط «نگاه دوباره» نیست. خروجی آن باید Finding قابل‌اقدام باشد:

- finding_id
- severity
- affected claim/file/artifact
- evidence
- risk
- required disposition
- status

Disposition:

- ACCEPTED
- FIXED
- REJECTED_WITH_RATIONALE
- DEFERRED_WITH_OWNER
- BLOCKING

قواعد:

- R3 و R4 نباید فقط توسط Implementer نهایی شوند.
- Review باید Acceptance، Risk و Gate Plan را ببیند.
- Reviewer نباید Scope تازه‌ای بدون دلیل به Task تحمیل کند.
- Finding سلیقه‌ای از Failure واقعی جدا شود.
- Council فقط برای conflict، uncertainty یا decision مهم فعال شود.
- Consensus جای Evidence را نمی‌گیرد.
- Self-review توسط همان Implementer، مستقل محسوب نمی‌شود.
- Tool-generated evidence مستقل از self-review است، اما استقلال Tool به‌تنهایی استقلال judgment انسانی/Agent را ثابت نمی‌کند.
- Critical-flow E2E باید دقیقاً flow پوشش‌داده‌شده، محیط، failure artifact و بخش‌های پوشش‌داده‌نشده را گزارش کند.

---

# ۲۳. Policy و Approval Protocol

## ۲۳.۱. Action Levels

| Level | رفتار |
|---|---|
| AUTO | در Scope و Policy مشخص، بدون توقف انسانی |
| REVIEW | اجرا می‌شود ولی قبل از Completion بررسی لازم است |
| APPROVAL | پیش از Action تأیید لازم است |
| FORBIDDEN | Action مجاز نیست |

## ۲۳.۲. Approval Scope

Approval باید دقیقاً مشخص کند:

- چه Actionای
- روی چه Targetی
- در کدام Environment
- با چه Constraintی
- تا چه زمانی یا چه Runی

Approval برای Plan، Approval برای Execution نیست مگر صریحاً هر دو را پوشش دهد.

## ۲۳.۳. Reapproval Trigger

- Scope expansion
- Risk escalation
- destructive fallback
- target change
- environment change
- external mutation جدید
- rollback غیرمنتظره
- budget expansion مهم

## ۲۳.۴. Forbidden Rule

FORBIDDEN با Confidence یا Council قابل دورزدن نیست. فقط Authority بالادست می‌تواند Policy را تغییر دهد.

---

# ۲۴. Evidence Contract

## ۲۴.۱. Evidence Kindها

- SOURCE_INSPECTION
- BUILD_RESULT
- TEST_RESULT
- STATIC_ANALYSIS
- SECURITY_RESULT
- PERFORMANCE_RESULT
- MIGRATION_RESULT
- DIFF
- HASH
- TOOL_RECEIPT
- RUNTIME_OBSERVATION
- REVIEW_RESULT
- APPROVAL
- RECOVERY_RESULT
- COVERAGE_DISCLOSURE
- CROSS_ARTIFACT_ANALYSIS
- SECURITY_FINDING
- SARIF

## ۲۴.۲. ویژگی Evidence معتبر

Evidence باید:

- به Claim یا Gate مشخص متصل باشد؛
- Scope و Environment را نشان دهد؛
- producer و timestamp داشته باشد؛
- result را بدون حذف Failureهای مرتبط ثبت کند؛
- limitation را آشکار کند؛
- در صورت امکان reproducible باشد.
- exit code را همراه semantic آن تفسیر کند؛ exit code صفر بدون coverage و run status، اثبات کامل امنیت یا صحت نیست.

## ۲۴.۳. Evidence Freshness

Evidence پس از تغییر Artifact مرتبط ممکن است stale شود. Completion Evaluator باید dependency بین Artifact و Evidence را بداند و Verification لازم را دوباره فعال کند.

## ۲۴.۴. Self-report

گزارش Agent می‌تواند Summary باشد، اما به‌تنهایی جای Test، Diff، Review یا Approval را نمی‌گیرد.

---

# ۲۵. Error Taxonomy

| Code | رفتار پایه |
|---|---|
| AMBIGUOUS_INTENT | NEEDS_CLARIFICATION |
| INVALID_INPUT | BLOCKED یا NEEDS_CLARIFICATION |
| POLICY_DENIED | FAILED یا ESCALATED |
| APPROVAL_REQUIRED | WAITING_APPROVAL |
| APPROVAL_EXPIRED | WAITING_APPROVAL |
| CAPABILITY_MISSING | Route again یا ESCALATED |
| TOOL_UNAVAILABLE | fallback مجاز یا BLOCKED |
| TOOL_FAILURE | controlled retry |
| EXECUTION_FAILED | Diagnose |
| VERIFICATION_FAILED | Repair یا Escalate |
| NO_PROGRESS | Circuit Breaker |
| BUDGET_EXHAUSTED | ESCALATED یا FAILED |
| CONFLICTING_EVIDENCE | Independent Review |
| EXTERNAL_STATE_CHANGED | Re-discover و re-plan |
| SCOPE_DRIFT | Stop و reauthorize |
| RECOVERY_FAILED | فوری Escalate؛ Risk دوباره ارزیابی شود |

Error نباید با حذف Test یا کم‌کردن Gate پنهان شود.

---

# ۲۶. Run Ledger و Knowledge Preservation

Ledger باید:

- chronological
- append-only
- queryable
- privacy-aware
- linked to Task، Run، Step و Artifact

باشد.

Repository یا Project Knowledge Store مرجع پایدار است. Handoff فقط وقتی تولید می‌شود که Agent یا انسان دیگری واقعاً باید ادامه دهد.

Handoff حداقل:

- current objective
- completed work
- changed artifacts
- decisions
- evidence
- unresolved blockers
- remaining budget
- next safe action

را دارد.

R0 و R1 به‌طور پیش‌فرض Handoff مستقل نیاز ندارند.

---

# ۲۷. SENS Integration Contract

v0.8 Dashboard یا Telemetry platform طراحی نمی‌کند، اما Eventهای کنترلی باید قابلیت تبدیل به SENS signal را داشته باشند.

Event پایه:

- event_id
- event_type
- task_id
- run_id
- step_id
- actor
- timestamp
- status
- duration
- cost/token در صورت مجاز و مرتبط
- tool/skill references
- evidence references
- error code
- privacy classification

قواعد:

- Secret و sensitive content نباید بی‌هدف ثبت شود.
- Retention و sampling باید Policy-driven باشند.
- Telemetry باید ارزش مهندسی یا عملیاتی داشته باشد.
- SENS signal به‌تنهایی Authority ایجاد نمی‌کند.

---

# ۲۸. Authorized Security Validation Adapter Contract

این بخش قرارداد Provider-neutral برای ابزارهایی مانند Strix است. Strix فقط یک binding اختیاری است؛ SAGE core به نصب، CLI، Cloud یا مدل خاص وابسته نیست.

## ۲۸.۱. Activation

Security adapter تنها وقتی Candidate است که Affected Domain و Risk آن را لازم کنند:

| Risk | Default activation |
|---|---|
| R0 | `NONE` مگر security-relevant evidence خلاف آن را نشان دهد |
| R1 | `LIGHT` با native checks |
| R2 | `QUICK` یا `STANDARD` فقط برای سطح حملهٔ مرتبط |
| R3 | `STANDARD` policy-driven و independent disposition |
| R4 | `DEEP` فقط با scope و Human Approval صریح |

Profile نام intensity است، نه مجوز. انتخاب `DEEP` بدون Authority معتبر MUST fail closed شود.

## ۲۸.۲. Preconditions

پیش از invocation:

- ownership یا written authorization تأیید شود؛
- Security Scope معتبر و منقضی‌نشده وجود داشته باشد؛
- target allowlist دقیق resolve شود و denylist اعمال گردد؛
- روش‌های ممنوع، rate، concurrency، time و cost budget تعیین شوند؛
- credential/data handling و reporting destination روشن باشد؛
- local، managed یا CI mode صریح انتخاب شود؛
- rollback/containment و emergency stop قابل‌اجرا باشد.

نبود هرکدام نتیجهٔ `APPROVAL_REQUIRED`، `INVALID_SCOPE` یا `BLOCKED` است؛ fallback پنهان ممنوع است.

## ۲۸.۳. Invocation و Bounded Loop

~~~text
AUTHORIZE
→ VALIDATE SCOPE
→ SELECT PROFILE + ADAPTER
→ PLAN / DRY RUN WHEN AVAILABLE
→ SCAN
→ NORMALIZE FINDINGS + COVERAGE
→ DISPOSITION
→ OPTIONAL REPAIR WITH SEPARATE WRITE AUTHORITY
→ TARGETED RESCAN
→ STOP / REPORT
~~~

حداکثر scan/repair/rescan attempts در Run Budget ثبت می‌شود. Finding به‌خودی‌خود مجوز Fix ایجاد نمی‌کند. تغییر application، infrastructure، credential یا production state نیازمند Authority همان mutation است.

## ۲۸.۴. Security Finding Contract

هر Finding حداقل شامل:

- finding_id، tool/vendor ID و deduplication key؛
- title، category/CWE/OWASP در صورت وجود و severity/confidence؛
- affected target/component/location؛
- evidence و reproduction summary با redaction؛
- exploitability، impact و environmental assumptions؛
- status: `OPEN|CONFIRMED|FALSE_POSITIVE|ACCEPTED_RISK|FIXED|MITIGATED`؛
- remediation، owner و verification requirement؛
- source run، profile، scope و timestamp.

## ۲۸.۵. Evidence Normalization

Adapter SHOULD خروجی‌های بومی را بدون حذف semantic به این Artifactها normalize کند:

- run receipt شامل command/method، version، profile، status، budget و exit-code meaning؛
- coverage disclosure شامل tested، skipped، unreachable و limitation؛
- structured findings JSON؛
- human-readable report؛
- SARIF در صورت پشتیبانی؛
- sanitized logs و failure artifacts؛
- rescan comparison.

برای binding فعلی Strix، exit codeهای documented باید به semantic ثبت‌شده map شوند؛ `0` فقط پاک‌بودن محدودهٔ تحلیل‌شده را نشان می‌دهد، `2` می‌تواند وجود vulnerability باشد نه crash، و وضعیت واقعی Run باید از artifact اجرا نیز بررسی شود.

## ۲۸.۶. SENS و Privacy

Telemetry امنیتی proportional است. SENS می‌تواند count، severity، duration، adapter version، coverage summary و disposition را دریافت کند؛ payload exploit، secret، token، personal data یا full request/response فقط با Policy و نیاز اثبات‌شده ثبت می‌شود.

## ۲۸.۷. Strix Binding Status

- Adapter ID پیشنهادی: `security.strix`
- Upstream snapshot: tag `v1.6.2`، commit `ff5c8cc8e46d8e60c2bc2439f7bcb07c05ca3db2`
- Local و managed mode باید جدا route شوند.
- نصب Skill/CLI، Docker startup، provider key و pentest invocation خارج از این Draft معماری‌اند.
- در اجرای این Integration هیچ Strix scan انجام نشده است.

---

# ۲۹. Machine-Readable Contract Examples

مثال‌های YAML این بخش از draft.2 حفظ شده‌اند و نمایش مفهومی legacy هستند؛ مستقیماً با Schema جدید اعتبارسنجی نمی‌شوند. نمونه‌های اجرایی JSON در `fixtures/v0.8/` و قرارداد wire-format در `schemas/v0.8/sage-contracts.schema.json` مرجع serialization جاری‌اند. هنگام تبدیل YAML باید discriminator، schema_version و field mapping جدید اعمال شود؛ پذیرش خام YAML به‌عنوان قرارداد معتبر ممنوع است. Runtime production به policy enforcement و validation کامل‌تر نیاز دارد.

## ۲۹.۱. Task Packet

~~~yaml
schema_version: sage.task-packet/v0.8
task_id: TASK-20260904-001
request_type: DESIGN
objective: Design SAGE v0.8 execution protocol
requested_outcome:
  - authoritative draft document
scope:
  allowed:
    - create one document in workspace outputs
  forbidden:
    - modify SAGE v0.7 source
authority:
  status: granted
  approval_ref: APR-example
risk:
  level: R3
  confidence: 0.90
  reasons:
    - foundational architecture decision
affected_domains:
  - architecture
  - agentic_tool_security
  - documentation
acceptance:
  - risk classification is executable and explainable
  - conditional gates cannot disappear silently
  - skills cannot expand authority
~~~

## ۲۹.۲. Gate Plan

~~~yaml
schema_version: sage.gate-plan/v0.8
task_id: TASK-20260904-001
gates:
  - gate_id: scope-intent
    required: true
    blocking: true
    evidence_required:
      - approved-scope
    status: PASS
  - gate_id: independent-review
    required: true
    independent_review: true
    blocking: true
    activation_reason: R3 foundational protocol
    status: PENDING
  - gate_id: data-migration
    required: false
    status: NOT_APPLICABLE
    activation_reason: no persistent schema change
~~~

## ۲۹.۳. Portable Skill Descriptor

~~~yaml
schema_version: sage.skill/v0.8
id: sissad/controlled-feature-development
version: 1.0.0
title: Controlled Feature Development
description: Build a non-trivial feature through scoped planning, implementation, verification, and review.
intents:
  - CHANGE
domains:
  - application_logic
  - frontend
risk_range:
  min: R1
  max: R3
invocation_policy: implicit
inputs:
  required:
    - objective
    - acceptance_criteria
    - allowed_changes
outputs:
  required:
    - artifact_refs
    - evidence_refs
side_effects:
  - workspace_write
permissions:
  requested:
    - repository_read
    - scoped_workspace_write
required_capabilities:
  - code_edit
  - targeted_verification
context_requirements:
  always:
    - task_packet
  conditional:
    - when: architecture affected
      load: relevant_architecture
evidence_contract:
  claims:
    - claim: acceptance satisfied
      requires:
        - test_result
        - diff
failure_modes:
  - PRECONDITION_FAILED
  - VERIFICATION_FAILED
retry_policy:
  controlled: true
  defer_to_run_budget: true
stop_conditions:
  - scope_drift
  - no_progress
native_bindings:
  codex:
    entrypoint: SKILL.md
~~~

## ۲۹.۴. Evidence Record

~~~yaml
schema_version: sage.evidence/v0.8
evidence_id: EVD-example
task_id: TASK-20260904-001
run_id: RUN-example
gate_id: targeted-tests
kind: TEST_RESULT
producer:
  type: tool
  id: local-test-runner
scope:
  artifacts:
    - src/example.ts
result: PASS
timestamp: 2026-09-04T12:00:00+03:30
reproducibility:
  command_ref: verify-targeted
limitations:
  - does not cover production integration
~~~

## ۲۹.۵. Agent Capability Descriptor

~~~yaml
schema_version: sage.agent-capability/v0.8
agent_id: sissad/code-agent
version: 1.0.0
roles:
  - implementer
  - reviewer
model_binding:
  provider: adapter-ref
  model_ref: model-ref
capabilities:
  - id: code_edit
    level: verified
    evidence_refs:
      - benchmark-code-edit-v1
  - id: architecture_review
    level: declared
modalities:
  - text
context:
  max_tokens: provider-reported
tool_classes:
  - repository_read
  - scoped_workspace_write
environments:
  - local_sandbox
privacy_modes:
  - local
  - cloud_allowed
risk_eligibility:
  max_implement: R3
  max_review: R4
independence:
  can_review_own_implementation: false
  model_family: provider-reported
health:
  status: available
authority:
  persistent_grant: forbidden
compatibility:
  protocol:
    - sage.execution/v0.8
~~~

## ۲۹.۶. Tool Descriptor

~~~yaml
schema_version: sage.tool/v0.8
tool_id: local/test-runner
version: 1.0.0
capabilities:
  - targeted_test
side_effect_class: LOCAL_REVERSIBLE
schemas:
  input_ref: schemas/tools/test-runner-input.schema.json
  output_ref: schemas/tools/test-runner-output.schema.json
permissions:
  required:
    - repository_read
    - workspace_temp_write
network:
  required: false
environments:
  - local_sandbox
idempotency:
  supported: true
timeouts:
  default_seconds: 300
evidence_outputs:
  - TEST_RESULT
  - TOOL_RECEIPT
recovery:
  rollback_supported: false
  cleanup_required: true
native_binding:
  adapter: local-process
~~~

## ۲۹.۷. Provider Adapter Descriptor

~~~yaml
schema_version: sage.provider-adapter/v0.8
adapter_id: provider/example
version: 1.0.0
interface:
  - describe_capabilities
  - validate_configuration
  - prepare_request
  - execute
  - stream_events
  - cancel
  - normalize_result
  - health_check
bindings:
  provider: example
semantics:
  preserves:
    - task_scope
    - granted_authority
    - evidence_references
permission_mapping:
  widening: forbidden
errors:
  normalize_to: sage.error/v0.8
events:
  normalize_to: sage.run-event/v0.8
idempotency:
  passthrough_when_supported: true
compatibility:
  protocol:
    - sage.execution/v0.8
~~~

---

# ۳۰. Reference Algorithms

## ۳۰.۱. Two-Pass Risk Classification

~~~text
function preliminaryClassify(task):
    knownFloors = detectKnownMandatoryFloors(task)
    provisional = deriveConservativeLevel(task, knownFloors)
    discoveryBoundary = defineDiscoveryBoundary(provisional, task.authority)
    return PreliminaryRisk(provisional, knownFloors, discoveryBoundary)

function finalClassify(task, preliminary, discovery):
    dimensions = assessDimensions(task, discovery)
    floors = detectMandatoryFloors(task, discovery)
    base = deriveLevel(dimensions)
    level = max(base, floors, preliminary.provenFloors)
    confidence = assessConfidence(discovery)

    if confidence < 0.50 and task.hasMutation:
        return NEEDS_CLARIFICATION or ESCALATED

    if uncertaintyCouldRaiseRisk(level):
        level = level + 1, capped at R4

    return RiskAssessment(level, confidence, reasons, evidence)
~~~

## ۳۰.۲. Compile Gates

~~~text
function compileGates(risk, domains, acceptance, policies):
    plan = baseMatrix(risk)

    for each conditionalGate in plan:
        result = evaluateCondition(conditionalGate, domains, acceptance)
        if result is true:
            activate(conditionalGate)
        else if result is false:
            markNotApplicableWithReason(conditionalGate)
        else:
            markUnresolvedAndBlocking(conditionalGate)

    applyDomainGates(plan, domains)
    applyPolicies(plan, policies)
    attachEvidenceRules(plan)
    return explainable(plan)
~~~

## ۳۰.۳. Route Skill

~~~text
function routeSkill(taskPacket, registry, policy):
    candidates = registry.discover(taskPacket.intent, taskPacket.domains)
    eligible = hardFilter(candidates, risk, capability, policy, permission, input)

    if eligible is empty:
        return GENERAL_AGENT if policyAllows else ESCALATE

    selected = score(eligible, configuredWeights)
    return selected with routingReceipt
~~~

## ۳۰.۴. Route Agent and Tool

~~~text
function routeAgentAndTool(taskPacket, agentRegistry, toolRegistry, policy):
    agents = hardFilterAgents(
        agentRegistry,
        taskPacket.requiredCapabilities,
        taskPacket.risk,
        taskPacket.environment,
        taskPacket.independence,
        policy
    )

    tools = hardFilterTools(
        toolRegistry,
        taskPacket.requiredToolCapabilities,
        taskPacket.allowedSideEffects,
        taskPacket.environment,
        policy
    )

    if agents is empty or tools are insufficient:
        return ESCALATE

    agent = scoreEligibleAgents(agents)
    session = createRuntimeSession(
        agent,
        taskPacket.assignment,
        deriveGrantedAuthority(taskPacket.approvals, policy),
        taskPacket.budget
    )

    return session, tools, routingReceipt
~~~

## ۳۰.۵. Execute Run

~~~text
function executeRun(taskPacket):
    assertAuthority(taskPacket)
    assertPreconditions(taskPacket)

    for step in executionPlan:
        if step.changesScope:
            stopAndReauthorize()

        execute(step)
        evidence = verify(step)

        while evidence fails:
            if circuitBreakerTrips():
                return independentDiagnosisOrEscalate()
            repairWithinScope()
            evidence = reverify(step)

    reviewWhenRequired()
    return completionEvaluator()
~~~

## ۳۰.۶. Evaluate Done

~~~text
function evaluateDone(run):
    assert all required acceptance criteria are satisfied
    assert all blocking gates are PASS or validly WAIVED
    assert all evidence is fresh and in scope
    assert all reviews are resolved
    assert all approvals are valid
    assert no blocking error remains
    assert approved scope equals completed scope
    return DONE
~~~

---

# ۳۱. Acceptance Scenarios

## ۳۱.۱. R0 — اصلاح Typo در Documentation

Expected:

- Risk: R0
- Workflow: MICRO
- Gate: scope + targeted visual/text check
- No ADR
- No Council
- No full regression
- DONE با Diff و بررسی هدفمند

## ۳۱.۲. R1 — تغییر Style محلی و قابل‌بازگشت

Expected:

- Risk: R1
- UX/accessibility فقط در صورت اثر واقعی فعال
- targeted UI check
- rollback ساده
- no independent review by default

## ۳۱.۳. R2 — افزودن Feature معمولی

Expected:

- Acceptance contract
- relevant architecture check
- implementation + targeted/integration tests
- relevant documentation
- review
- CI یا verify entrypoint

## ۳۱.۴. R3 — تغییر Public API همراه Migration

Expected:

- Mandatory Floor R3
- contract compatibility
- migration + integrity verification
- rollback یا roll-forward
- architecture impact
- independent review
- documentation/versioning
- CI PASS

## ۳۱.۵. R4 — تغییر destructive در Production

Expected:

- Mandatory Floor R4
- exact target resolution
- Human Approval پیش از Action
- recovery evidence
- independent verification
- observability
- restricted attempt budget
- reapproval on scope or fallback change

## ۳۱.۶. پنج خط تغییر در Authorization

Expected:

- LOC کوچک باعث R0/R1 نمی‌شود
- Security floor حداقل R3 و برحسب Blast Radius ممکن است R4
- security tests + regression + independent review

## ۳۱.۷. Refactor بزرگ داخلی بدون Contract change

Expected:

- اندازهٔ Diff به‌تنهایی R3 نیست
- اگر reversible و well-tested باشد می‌تواند R2 بماند
- architecture و regression gates برحسب اثر فعال می‌شوند

## ۳۱.۸. Intent مبهم

Expected:

- NEEDS_CLARIFICATION
- فقط Discovery read-only مجاز
- هیچ Mutation پیش از روشن‌شدن Outcome

## ۳۱.۹. Skill مناسب ولی Permission ناکافی

Expected:

- Skill توسط Hard Filter رد یا WAITING_APPROVAL می‌شود
- Capability به Authority تبدیل نمی‌شود
- fallback پنهان ممنوع

## ۳۱.۱۰. Verification Failure تکراری

Expected:

- failure signature ثبت می‌شود
- same-fix/no-progress تشخیص داده می‌شود
- Circuit Breaker فعال می‌شود
- independent diagnosis یا Escalation

## ۳۱.۱۱. Feature با Spec Drift

Expected:

- Cross-Artifact Analyzer اختلاف را ثبت می‌کند؛
- Implementation بی‌صدا از Spec جدا نمی‌شود؛
- deviation در Scope موجود resolve یا برای reapproval متوقف می‌شود؛
- Convergence پس از اصلاح، acceptance و evidence links را دوباره بررسی می‌کند.

## ۳۱.۱۲. اتصال Database

Expected:

- schema/migration و recovery متناسب؛
- secret خارج از config committed؛
- یک write fixture، read-back و value comparison؛
- tenant/access boundary در صورت ارتباط؛
- cleanup یا rollback fixture.

## ۳۱.۱۳. Security Validation با Strix

Expected:

- Strix صرفاً به‌عنوان optional adapter انتخاب می‌شود؛
- Security Scope و authorization پیش از scan لازم‌اند؛
- profile با Risk متناسب است؛
- exit code با run status، coverage و findings تفسیر می‌شود؛
- Finding مجوز Fix ایجاد نمی‌کند؛
- rescan بودجه‌دار است و secret/exploit payload بی‌هدف وارد SENS نمی‌شود.

---

# ۳۲. Conformance Tests برای پیاده‌سازی آینده

یک Orchestrator سازگار با v0.8 باید این آزمون‌ها را پاس کند:

۱) ورودی و Policy یکسان، Gate Plan توضیح‌پذیر و معادل تولید کند.  
۲) Mandatory Floor را با Average پایین نیاورد.  
۳) Gate ستاره‌دار را بدون ACTIVE، NOT_APPLICABLE یا UNRESOLVED رها نکند.  
۴) بدون Authority معتبر وارد EXECUTING نشود.  
۵) Skill نتواند Permission جدید ایجاد کند.  
۶) Scope drift را متوقف و دوباره طبقه‌بندی کند.  
۷) DONE را با Gate blocking ناموفق رد کند.  
۸) Evidence stale را تشخیص دهد.  
۹) Loop بی‌نهایت ایجاد نکند.  
۱۰) R0 را به Workflow سنگین تبدیل نکند.  
۱۱) R3/R4 را فقط با self-review نهایی نکند.  
۱۲) Error را با حذف Verification پنهان نکند.  
۱۳) native Skill files را بدون نیاز به SAGE-specific metadata آلوده نکند.  
۱۴) Ledger را بدون Secret leakage قابل‌ممیزی نگه دارد.  
۱۵) BLOCKED، FAILED و ESCALATED را از هم جدا کند.  
۱۶) Preliminary Classification را پیش از Discovery و Final Classification را پس از Evidence لازم اجرا کند.  
۱۷) Authority را به Runtime Agent Session بدهد، نه هویت دائمی Agent.  
۱۸) Tool فاقد Side Effect Class معتبر را از Routing خودکار حذف کند.  
۱۹) Provider Adapter نتواند Scope یا Permission را هنگام Mapping گسترش دهد.  
۲۰) Clarification Gate پرسش کم‌اثر را Blocking نکند و ambiguity مؤثر را پیش از Mutation متوقف کند.  
۲۱) Cross-Artifact Analyzer Requirement بدون Evidence یا Implementation منحرف را کشف کند.  
۲۲) Convergence Engine در no-progress، scope drift یا budget exhaustion متوقف شود.  
۲۳) Anti-Overengineering Gate ceremony غیرضروری R0/R1 را حذف کند، بدون حذف control اجباری.  
۲۴) Instruction Projection منشأ Rule را حفظ و drift را گزارش کند.  
۲۵) Workflow Package نصب/حذف را idempotent و ownership-aware نگه دارد.  
۲۶) Data integration بدون write/read proof به DONE نرسد.  
۲۷) Security adapter بدون authorization و Security Scope route نشود.  
۲۸) Security exit code بدون coverage و run status به PASS کامل تبدیل نشود.  
۲۹) Skill پیچیده syntax-valid ولی scope-expanding را در forward-test رد کند.  
۳۰) Spec deviation بدون Rationale و در صورت نیاز reapproval پذیرفته نشود.

---

# ۳۳. Repository Layout پیشنهادی

~~~text
SAGE-Data-Sours/
├── SAGE_v0.7_MASTER_BASELINE.md
├── SAGE_HANDOFF_v0.7_to_v0.8.md
├── SAGE_v0.8_EXECUTION_PROTOCOL_AND_SKILL_CONTRACT.md
├── SOURCE_REGISTRY.md
├── history/
├── sources/
│   ├── supplied-originals/
│   ├── integration-deltas/
│   ├── legacy-derived/
│   └── upstream/
├── schemas/v0.8/
│   ├── sage-contracts.schema.json
│   ├── sage-policies.schema.json
│   └── sage-architecture.schema.json
├── policies/v0.8/
│   ├── core-policy.json
│   ├── security-adapter-policy.json
│   └── architecture-policy.json
├── fixtures/v0.8/
├── tools/
│   └── Test-SageContracts.ps1
├── reviews/
└── reports/
~~~

این Layout در `draft.3` به‌عنوان reference implementation حداقلی ساخته و با Fixtureهای R0، R2 و R4 بررسی می‌شود؛ Runtime نهایی Orchestrator همچنان خارج از دامنه است.

---

# ۳۴. Architecture Modeling و Diagram-as-Code

Architecture Modeling در SAGE یک قابلیت درجه‌اول است، اما مدل معماریِ تأییدشده تنها Source of Truth است؛ دیاگرام‌ها View/Projection و خروجی‌های SVG/PNG/PDF صرفاً Presentation Artifact هستند.

## ۳۴.۱ قرارداد و حاکمیت مدل

- SAGE از یک `Architecture Model API` مستقل از Provider استفاده می‌کند؛ LikeC4 Adapter پیش‌فرض و Structurizr Alternative درجه‌اول است.
- هر Element و Relationship باید `architecture_id` پایدار، Owner و Provenance داشته باشد.
- Authority فقط یکی از `APPROVED / INFERRED / OBSERVED / PROPOSED / DEPRECATED` است. مدل Inferred یا Observed حق بازنویسی خاموش مدل Approved را ندارد.
- Reverse Architecture Discovery از کد، IaC و Runtime/SENS/UEG فقط Evidence و Proposal تولید می‌کند.
- Architecture Delta باید Base Model Version، تغییرات و Viewهای متاثر را ثبت کند.

قرارداد ماشین‌خوان در `schemas/v0.8/sage-architecture.schema.json` و Policy در `policies/v0.8/architecture-policy.json` نگهداری می‌شود.

## ۳۴.۲ Policy، Fitness و Gate

Architecture Policy-as-Code و Fitness Functionها برای تغییرات دارای Architecture Impact فعال می‌شوند و حداقل این موارد را بررسی می‌کنند: حل‌شدن Stable IDها، نبود Forbidden Dependency و Boundary Violation، نبود Edge غیرمجاز و حفظ یک Canonical Model. خروجی `PASS / FAIL / REVIEW_REQUIRED` است.

R0/R1 ایزوله به‌طور پیش‌فرض دیاگرام یا بررسی سنگین معماری نمی‌خواهند؛ فعال‌سازی بر اساس Risk، Task Type، Data/Security Impact و سؤال مهندسی انجام می‌شود.

## ۳۴.۳ Diagram-as-Code و Router

Renderer از Model جداست: D2 برای Viewهای polished، Mermaid برای Markdown/ADR/PR، PlantUML اختیاری، Graphviz برای Graph/Layout و Kroki فقط Gateway اختیاری است. Layout از طریق `LayoutEngine` با ELK برای Graphهای پیچیده، Graphviz به‌عنوان fallback و Dagre برای موارد سبک انجام می‌شود. هیچ Rendererای Source of Truth نیست.

فقط Viewهای مرتبط تولید می‌شوند؛ نمونه‌ها شامل System Context، Dependency، Sequence، Deployment، Data Flow، Security/Trust Boundary، Agent/Tool Flow، Blast Radius و Drift است.

## ۳۴.۴ اتصال به SENS/UEG و Convergence

SAGE مدل Approved را نگه می‌دارد، UEG روابط موردانتظار و SENS روابط مشاهده‌شده را فراهم می‌کند. مقایسهٔ Planned ↔ Observed به `CONVERGED / PARTIALLY_CONVERGED / NOT_CONVERGED / REVIEW_REQUIRED` منجر می‌شود. Drift مادی و توضیح‌داده‌نشده، در صورت فعال‌بودن Architecture Gate، Completion را متوقف می‌کند.

## ۳۴.۵ قواعد Agent و ضد Overengineering

Agent باید پیش از تغییر مهم مدل را Query کند، Architecture Delta بسازد، فقط Viewهای لازم را تولید و روابط نامطمئن را علامت‌گذاری کند. Agent نباید رابطه اختراع کند، هنگام کدنویسی خاموش مدل را تغییر دهد، PNG/SVG را منبع حقیقت بداند یا مدل Inferred را بدون Review به Approved ارتقا دهد.

این قابلیت با Consistency Analyzer، Convergence Engine، Evidence Ledger، Security Boundary و Dynamic DoD یکپارچه است. Fixture مرجع آن `fixtures/v0.8/architecture-model.json` است.

---

# ۳۵. تصمیم‌های تثبیت‌شده در Draft v0.8

## DEC-v0.8-01 — v0.7 Preserved

v0.8 قانون اساسی v0.7 را Extend می‌کند و Source آن را بازنویسی نمی‌کند.

## DEC-v0.8-02 — Risk Uses Floors

Risk از Mandatory Floor و Dimension analysis به‌دست می‌آید، نه Average یا LOC.

## DEC-v0.8-03 — Conditional Gates Are Compiled

ستاره‌های Matrix به شرط صریح و خروجی قابل‌ممیزی تبدیل می‌شوند.

## DEC-v0.8-04 — Skill Cannot Grant Authority

Skill فقط نیاز Permission را اعلام می‌کند؛ Policy Engine آن را Grant یا Deny می‌کند.

## DEC-v0.8-05 — Portable Sidecar

قرارداد قابل‌حمل SAGE در sidecar/registry نگهداری می‌شود و فایل بومی Provider حفظ می‌شود.

## DEC-v0.8-06 — Progressive Disclosure

Skill فقط Context موردنیاز را Load می‌کند.

## DEC-v0.8-07 — Completion Is Compiled

DoD برای هر Task از Acceptance، Gate، Evidence و Approval ساخته می‌شود.

## DEC-v0.8-08 — Controlled Repair

Repair loop بودجه و Circuit Breaker دارد.

## DEC-v0.8-09 — Independent Review

R3 و R4 به Review مستقل نیاز دارند.

## DEC-v0.8-10 — Provider Neutrality

Control Protocol به Provider خاص وابسته نمی‌شود؛ Adapterها مسئول Mapping هستند.

## DEC-v0.8-11 — Two-Pass Classification

Classification شامل Preliminary Risk پیش از Discovery و Final Risk پس از Evidence لازم است.

## DEC-v0.8-12 — Runtime Authority

تعریف Frozen مربوط به Agent حفظ می‌شود. Authority فقط به Runtime Agent Session و در Scope یک Task/Run Grant می‌شود.

## DEC-v0.8-13 — Explicit Registry Contracts

Agent Capability، Tool و Provider Adapter دارای Contract مستقل، قابل‌نسخه‌بندی و Provider-neutral هستند.

## DEC-v0.8-14 — Source Integration Is Traceable

Reference، Delta و upstream snapshot با Hash/Commit ثبت می‌شوند؛ Rule فقط پس از disposition صریح وارد معماری می‌شود.

## DEC-v0.8-15 — Specification Must Converge with Evidence

Clarification، consistency analysis و convergence به‌صورت Gateهای محدود و بودجه‌دار تعریف می‌شوند؛ انطباق ظاهری جای Evidence را نمی‌گیرد.

## DEC-v0.8-16 — Workflow Composition Is Versioned

Profile، extension و package قابل‌ترکیب‌اند اما precedence، pinning، dry-run، idempotency و ownership-aware removal باید آشکار باشد.

## DEC-v0.8-17 — Provider Instructions Are Projections

فایل‌های بومی Agent/Provider projection قواعد معتبرند و منبع حاکم، provenance و conflict status را حذف نمی‌کنند.

## DEC-v0.8-18 — Security Tools Are Conditional Adapters

Strix و ابزار مشابه جزء Core نیستند. فعال‌سازی فقط با Risk trigger، authorization، Security Scope، budget و evidence normalization ممکن است.

## DEC-v0.8-19 — JSON Schema 2020-12

قراردادهای ماشین‌خوان reference در v0.8 از JSON Schema Draft 2020-12 استفاده می‌کنند.

---

# ۳۶. موارد باز برای تصمیم آینده

این موارد عمداً در Draft جاری نهایی نشده‌اند:

- Registry backend: file، database یا service
- نحوهٔ cryptographic signing برای Evidence و Approval
- Agent benchmark و reputation
- distributed locking و concurrent run control
- capability tokenهای sandbox
- transport و binding اختصاصی هر Provider Adapter
- SENS event transport و retention
- UI برای Gate Plan و Approval
- policy inheritance در monorepoهای پیچیده
- packaging و installation واقعی SAGE Skills
- policy دقیق برای نگهداری exploit evidence و security artifact retention
- mapping نهایی همهٔ Provider projectionها

این موارد نباید مانع ارزیابی معماری v0.8 شوند، اما پیش از Runtime production باید تعیین تکلیف شوند.

---

# ۳۷. Definition of Done برای خود v0.8

Draft v0.8 زمانی آمادهٔ Formalization است که:

- با Constitution v0.7 تناقض Blocking نداشته باشد؛
- State Machine کامل و بدون Transition خطرناک شناخته‌شده باشد؛
- Risk Floorها با سناریوهای R0–R4 سازگار باشند؛
- Gate ستاره‌دار قابل Compile باشد؛
- Skill Contract با Progressive Disclosure و Native Compatibility سازگار باشد؛
- Two-Pass Classification با Handoff و Execution Model v0.7 سازگار باشد؛
- Agent Capability، Tool Registry و Provider Adapter contract قابل‌پیاده‌سازی باشند؛
- Runtime Engineering Brief، Goal و Change Scope contract قابل‌پیاده‌سازی باشند؛
- Clarification، consistency، anti-overengineering و convergence rules با fixture آزموده شوند؛
- Workflow Package و Instruction Projection provenance و precedence را حفظ کنند؛
- Security adapter بدون authorization و Scope قابل اجرا نباشد؛
- JSON Schema 2020-12، policy، fixture و validator reference معتبر باشند؛
- Authority فقط در Runtime Agent Session و با Scope محدود Grant شود؛
- Permission از Capability جدا مانده باشد؛
- Completion بدون Evidence ممکن نباشد؛
- Circuit Breaker قابل‌پیاده‌سازی باشد؛
- سناریوهای Conformance بازبینی شوند؛
- یک Review مستقل انجام شود؛
- کاربر وضعیت Formalized Baseline را صریحاً تأیید کند.

---

# ۳۸. نتیجه

SAGE v0.7 پاسخ می‌داد:

> چه اصولی باید رعایت شوند؟

SAGE v0.8 پاسخ می‌دهد:

> این اصول چگونه به تصمیم، Workflow، Permission، Skill، Evidence و Completion قابل‌اجرا تبدیل می‌شوند؟

خلاصهٔ پروتکل:

~~~text
INTENT
→ AUTHORITY
→ RISK
→ DOMAINS
→ GATES
→ PLAN
→ CONTEXT
→ ROUTE
→ EXECUTE
→ VERIFY
→ ANALYZE / CONVERGE / REPAIR OR REVIEW
→ EVIDENCE
→ DYNAMIC DoD
→ DONE / ESCALATE
~~~

اصل نهایی v0.8:

> SAGE must make the safe path explicit, the required evidence computable, and unnecessary ceremony removable.
