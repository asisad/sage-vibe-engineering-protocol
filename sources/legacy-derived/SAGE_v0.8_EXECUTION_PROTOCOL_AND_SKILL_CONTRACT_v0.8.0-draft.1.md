# SAGE — SiSsad Agentic General Engineering
## Execution Protocol & Skill Contract v0.8

Status: Draft for Review  
Version: 0.8.0-draft.1  
Date: 2026-09-04  
Language: Persian explanatory text; English machine contracts  
Extends: SAGE Master Baseline v0.7  
Replaces: Nothing

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

## ۲.۲. خارج از دامنهٔ v0.8

- پیاده‌سازی Runtime نهایی Orchestrator
- ساخت Dashboard برای SENS
- انتخاب Provider نهایی
- ساخت Model Benchmark Registry واقعی
- تعریف Agent Reputation Score عملیاتی
- پیاده‌سازی Distributed Swarm
- ساخت همهٔ Skillهای مهندسی
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

---

# ۶. معماری اجرایی

~~~text
USER INTENT
    ↓
INTAKE + AUTHORITY
    ↓
TASK ENVELOPE
    ↓
DISCOVERY / CLARIFICATION
    ↓
RISK + AFFECTED DOMAINS
    ↓
GATE COMPILER
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
VERIFY → DIAGNOSE → REPAIR
    ↓
REVIEW / APPROVAL
    ↓
DYNAMIC DoD
    ↓
DONE / BLOCKED / ESCALATED / FAILED
~~~

## ۶.۱. Control Plane

Control Plane شامل این اجزاست:

- Intake Controller
- Risk Classifier
- Domain Detector
- Gate Compiler
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

Fieldهای غیرمرتبط حذف می‌شوند؛ خالی‌کردن Fieldهای مهم برای کوچک‌کردن Context مجاز نیست.

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

---

# ۹. Execution State Machine

## ۹.۱. Stateها

| State | معنا |
|---|---|
| RECEIVED | درخواست دریافت شده |
| DISCOVERING | بررسی Read-only برای فهم Scope |
| NEEDS_CLARIFICATION | Intent یا Scope برای ادامه کافی نیست |
| CLASSIFIED | Risk و Domainها تعیین شده‌اند |
| PLANNED | Gate Plan و Execution Plan آماده‌اند |
| WAITING_APPROVAL | Approval لازم هنوز معتبر نیست |
| READY | Preconditions کامل است |
| EXECUTING | Action در حال انجام است |
| VERIFYING | Evidence در حال تولید یا ارزیابی است |
| REPAIRING | Failure کنترل‌شده در حال اصلاح است |
| REVIEWING | Review لازم در حال انجام است |
| BLOCKED | مانع خارجی یا ورودی ضروری وجود دارد |
| ESCALATED | Task به Authority یا Capability بالاتر ارجاع شده |
| DONE | Dynamic DoD برقرار است |
| FAILED | Stop condition نهایی فعال شده |
| CANCELLED | Authority معتبر Task را متوقف کرده |

## ۹.۲. Transitionهای مجاز

~~~text
RECEIVED
  → DISCOVERING
  → NEEDS_CLARIFICATION
  → CLASSIFIED

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
  → DONE
  → ESCALATED

REPAIRING
  → VERIFYING
  → ESCALATED
  → FAILED

REVIEWING
  → DONE
  → REPAIRING
  → WAITING_APPROVAL
  → ESCALATED

هر State غیرنهایی
  → CANCELLED
~~~

## ۹.۳. Invariantها

- DONE فقط از طریق Completion Evaluator قابل ثبت است.
- Action دارای Side Effect پیش از READY ممنوع است.
- READY فقط با Authority و Preconditions معتبر ایجاد می‌شود.
- تغییر Scope پس از Approval می‌تواند Run را دوباره به WAITING_APPROVAL برگرداند.
- FAILED با BLOCKED یکسان نیست؛ BLOCKED ممکن است پس از تغییر External State ادامه یابد.
- ESCALATED به معنی Failure نیست؛ یعنی Orchestrator فعلی Authority یا Capability کافی ندارد.

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
۸) Discovery خواندنی لازم را انجام دهد؛  
۹) Scope proposal را برای Actionهای نیازمند Approval آماده کند.

Clarification فقط وقتی Blocking است که پاسخ آن نتیجه، Scope، Risk یا Authority را به‌طور معنادار تغییر دهد.

Orchestrator MUST NOT:

- درخواست Diagnose را خودکار به Fix تبدیل کند؛
- Approval برای بررسی را Approval برای Mutation تلقی کند؛
- اجازهٔ تغییر یک فایل را به کل Repository تعمیم دهد؛
- Permission ابزار را به Permission کاربر تبدیل کند؛
- عملیات بیرونی را با عنوان «مرحلهٔ طبیعی کار» پنهان کند.

---

# ۱۱. Risk Classifier v0.8

## ۱۱.۱. ابعاد Risk

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

## ۱۱.۲. Mandatory Floorها

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

## ۱۱.۳. Confidence

| Confidence | رفتار |
|---|---|
| 0.80–1.00 | Classification قابل‌استفاده |
| 0.50–0.79 | Discovery یا Assumption صریح لازم |
| کمتر از 0.50 | اجرای Mutation متوقف؛ Clarify یا Escalate |

اگر Uncertainty به‌طور منطقی بتواند Risk را یک سطح بالا ببرد، سطح بالاتر تا زمان رفع ابهام اعمال می‌شود.

## ۱۱.۴. Downgrade

- Mandatory Floor بدون Evidence جدید قابل Downgrade نیست.
- Downgrade باید reason، evidence و decider داشته باشد.
- R4 به R3 SHOULD نیازمند Human Review باشد.
- کم‌بودن LOC دلیل Downgrade نیست.
- بزرگ‌بودن Diff به‌تنهایی دلیل R3 یا R4 نیست.

## ۱۱.۵. خروجی قابل‌توضیح

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

## ۱۴.۱. R0 نباید متورم شود

R0 به‌طور پیش‌فرض نیاز ندارد:

- ADR
- Council
- Full repository analysis
- Full regression
- Handoff مستقل
- Documentation گسترده

## ۱۴.۲. R4 نباید با Confidence مدل ساده شود

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

---

# ۱۶. Context Packaging Protocol

## ۱۶.۱. Context Layers

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

### Layer 3 — Conditional References

- detailed schema
- provider documentation
- migration procedure
- security policy
- design system
- domain-specific references

Agent فقط Layerهای لازم را دریافت می‌کند.

## ۱۶.۲. Context Item Contract

هر Context item SHOULD شامل:

- source
- version یا hash
- relevance
- freshness
- sensitivity
- authority
- load_condition

## ۱۶.۳. ممنوعیت‌ها

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
  + Authority
~~~

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

## ۲۰.۱. Mutation Boundary

پیش از اولین Mutation:

۱) Scope resolved باشد؛  
۲) Risk و Gate Plan آماده باشد؛  
۳) Approval لازم معتبر باشد؛  
۴) exact target بررسی شده باشد؛  
۵) rollback یا recovery متناسب تعریف شده باشد؛  
۶) Evidence plan مشخص باشد.

## ۲۰.۲. Idempotency

External Mutation و عملیات retryپذیر SHOULD دارای Idempotency Key باشند. اگر مقصد از Idempotency پشتیبانی نمی‌کند، Ledger باید امکان تشخیص اجرای قبلی را فراهم کند.

## ۲۰.۳. Scope Drift

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

## ۲۴.۲. ویژگی Evidence معتبر

Evidence باید:

- به Claim یا Gate مشخص متصل باشد؛
- Scope و Environment را نشان دهد؛
- producer و timestamp داشته باشد؛
- result را بدون حذف Failureهای مرتبط ثبت کند؛
- limitation را آشکار کند؛
- در صورت امکان reproducible باشد.

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

# ۲۸. Machine-Readable Contract Examples

این مثال‌ها informative هستند. Schemaهای رسمی JSON Schema باید در مرحلهٔ Implementation جداگانه ساخته و version شوند.

## ۲۸.۱. Task Packet

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

## ۲۸.۲. Gate Plan

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

## ۲۸.۳. Portable Skill Descriptor

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

## ۲۸.۴. Evidence Record

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

---

# ۲۹. Reference Algorithms

## ۲۹.۱. Classify Risk

~~~text
function classifyRisk(task, discovery):
    dimensions = assessDimensions(task, discovery)
    floors = detectMandatoryFloors(task, discovery)
    base = deriveLevel(dimensions)
    level = max(base, floors)
    confidence = assessConfidence(discovery)

    if confidence < 0.50 and task.hasMutation:
        return NEEDS_CLARIFICATION or ESCALATED

    if uncertaintyCouldRaiseRisk(level):
        level = level + 1, capped at R4

    return RiskAssessment(level, confidence, reasons, evidence)
~~~

## ۲۹.۲. Compile Gates

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

## ۲۹.۳. Route Skill

~~~text
function routeSkill(taskPacket, registry, policy):
    candidates = registry.discover(taskPacket.intent, taskPacket.domains)
    eligible = hardFilter(candidates, risk, capability, policy, permission, input)

    if eligible is empty:
        return GENERAL_AGENT if policyAllows else ESCALATE

    selected = score(eligible, configuredWeights)
    return selected with routingReceipt
~~~

## ۲۹.۴. Execute Run

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

## ۲۹.۵. Evaluate Done

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

# ۳۰. Acceptance Scenarios

## ۳۰.۱. R0 — اصلاح Typo در Documentation

Expected:

- Risk: R0
- Workflow: MICRO
- Gate: scope + targeted visual/text check
- No ADR
- No Council
- No full regression
- DONE با Diff و بررسی هدفمند

## ۳۰.۲. R1 — تغییر Style محلی و قابل‌بازگشت

Expected:

- Risk: R1
- UX/accessibility فقط در صورت اثر واقعی فعال
- targeted UI check
- rollback ساده
- no independent review by default

## ۳۰.۳. R2 — افزودن Feature معمولی

Expected:

- Acceptance contract
- relevant architecture check
- implementation + targeted/integration tests
- relevant documentation
- review
- CI یا verify entrypoint

## ۳۰.۴. R3 — تغییر Public API همراه Migration

Expected:

- Mandatory Floor R3
- contract compatibility
- migration + integrity verification
- rollback یا roll-forward
- architecture impact
- independent review
- documentation/versioning
- CI PASS

## ۳۰.۵. R4 — تغییر destructive در Production

Expected:

- Mandatory Floor R4
- exact target resolution
- Human Approval پیش از Action
- recovery evidence
- independent verification
- observability
- restricted attempt budget
- reapproval on scope or fallback change

## ۳۰.۶. پنج خط تغییر در Authorization

Expected:

- LOC کوچک باعث R0/R1 نمی‌شود
- Security floor حداقل R3 و برحسب Blast Radius ممکن است R4
- security tests + regression + independent review

## ۳۰.۷. Refactor بزرگ داخلی بدون Contract change

Expected:

- اندازهٔ Diff به‌تنهایی R3 نیست
- اگر reversible و well-tested باشد می‌تواند R2 بماند
- architecture و regression gates برحسب اثر فعال می‌شوند

## ۳۰.۸. Intent مبهم

Expected:

- NEEDS_CLARIFICATION
- فقط Discovery read-only مجاز
- هیچ Mutation پیش از روشن‌شدن Outcome

## ۳۰.۹. Skill مناسب ولی Permission ناکافی

Expected:

- Skill توسط Hard Filter رد یا WAITING_APPROVAL می‌شود
- Capability به Authority تبدیل نمی‌شود
- fallback پنهان ممنوع

## ۳۰.۱۰. Verification Failure تکراری

Expected:

- failure signature ثبت می‌شود
- same-fix/no-progress تشخیص داده می‌شود
- Circuit Breaker فعال می‌شود
- independent diagnosis یا Escalation

---

# ۳۱. Conformance Tests برای پیاده‌سازی آینده

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

---

# ۳۲. Repository Layout پیشنهادی

~~~text
SAGE/
├── baselines/
│   ├── SAGE_v0.7_MASTER_BASELINE.md
│   └── SAGE_v0.8_EXECUTION_PROTOCOL_AND_SKILL_CONTRACT.md
├── schemas/
│   ├── task-packet.schema.json
│   ├── risk-assessment.schema.json
│   ├── gate-plan.schema.json
│   ├── skill.schema.json
│   ├── evidence.schema.json
│   └── run-event.schema.json
├── policies/
│   ├── default-risk-policy.yaml
│   ├── default-gate-policy.yaml
│   └── default-approval-policy.yaml
├── registries/
│   ├── skills.yaml
│   ├── agents.yaml
│   └── tools.yaml
├── examples/
│   ├── r0/
│   ├── r2/
│   └── r4/
└── validators/
    └── conformance/
~~~

این Layout در v0.8 پیشنهاد معماری است؛ ساخت همهٔ فایل‌ها جزو این Draft نیست.

---

# ۳۳. تصمیم‌های تثبیت‌شده در Draft v0.8

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

---

# ۳۴. موارد باز برای تصمیم آینده

این موارد عمداً در Draft جاری نهایی نشده‌اند:

- زبان رسمی Schemaها: JSON Schema نسخهٔ انتخابی
- Registry backend: file، database یا service
- نحوهٔ cryptographic signing برای Evidence و Approval
- Agent benchmark و reputation
- distributed locking و concurrent run control
- capability tokenهای sandbox
- cross-provider adapter API
- SENS event transport و retention
- UI برای Gate Plan و Approval
- policy inheritance در monorepoهای پیچیده
- packaging و installation واقعی SAGE Skills

این موارد نباید مانع ارزیابی معماری v0.8 شوند، اما پیش از Runtime production باید تعیین تکلیف شوند.

---

# ۳۵. Definition of Done برای خود v0.8

Draft v0.8 زمانی آمادهٔ Formalization است که:

- با Constitution v0.7 تناقض Blocking نداشته باشد؛
- State Machine کامل و بدون Transition خطرناک شناخته‌شده باشد؛
- Risk Floorها با سناریوهای R0–R4 سازگار باشند؛
- Gate ستاره‌دار قابل Compile باشد؛
- Skill Contract با Progressive Disclosure و Native Compatibility سازگار باشد؛
- Permission از Capability جدا مانده باشد؛
- Completion بدون Evidence ممکن نباشد؛
- Circuit Breaker قابل‌پیاده‌سازی باشد؛
- سناریوهای Conformance بازبینی شوند؛
- یک Review مستقل انجام شود؛
- کاربر وضعیت Formalized Baseline را صریحاً تأیید کند.

---

# ۳۶. نتیجه

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
→ REPAIR OR REVIEW
→ EVIDENCE
→ DYNAMIC DoD
→ DONE / ESCALATE
~~~

اصل نهایی v0.8:

> SAGE must make the safe path explicit, the required evidence computable, and unnecessary ceremony removable.

