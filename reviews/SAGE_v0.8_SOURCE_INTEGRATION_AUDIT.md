# SAGE v0.8 Source Integration Audit

Status: Independent review complete; BLOCKING/HIGH findings remediated  
Target: SAGE_v0.8_EXECUTION_PROTOCOL_AND_SKILL_CONTRACT.md  
Target version: 0.8.0  
Date: 2026-09-06

## ۱. روش

۱) Baseline رسمی v0.7 و Handoff بالاترین مرجع پروژه در نظر گرفته شدند.  
۲) PDF سی‌وسه‌صفحه‌ای و learn4.html به‌عنوان Source اصلی خوانده شدند.  
۳) چهار Delta به‌عنوان تحلیل پیشنهادی، نه دستور، با Source اصلی و upstream مقایسه شدند.  
۴) Spec Kit و Strix با snapshot قفل‌شده در SOURCE_REGISTRY.md بررسی شدند.  
۵) هر ایده با یکی از dispositionهای ACCEPTED، ACCEPTED_WITH_CONSTRAINTS، ALREADY_COVERED، DEFERRED یا REJECTED_AS_UNIVERSAL تعیین تکلیف شد.

## ۲. خلاصه

| Source family | نتیجه |
|---|---|
| Spec Kit | الگوهای clarification، consistency، convergence و composable workflow پذیرفته و Provider-neutral شدند. |
| Claude prompt pack | قراردادهای محصول، Spec deviation، UI/UX، data proof، evidence debugging، cleanup، commit planning، guardrail و Skill conformance به‌صورت شرطی پذیرفته شدند. |
| Vibe master prompt | Runtime Engineering Brief و context layering پذیرفته شد؛ persona ثابت و master prompt حجیم رد شد. |
| Strix | فقط به‌عنوان optional Authorized Security Validation adapter پذیرفته شد؛ نصب و scan خارج از معماری ماند. |

## ۳. ماتریس ادغام Spec Kit

| Proposal | Disposition | محل ادغام / دلیل |
|---|---|---|
| Clarification Gate | ACCEPTED | §۱۰.۱؛ فقط ambiguity مؤثر Blocking است. |
| Cross-Artifact Consistency Analyzer | ACCEPTED | Control Plane، §۲۱.۶ و Conformance. |
| Convergence Engine | ACCEPTED_WITH_CONSTRAINTS | §۲۱.۶؛ محدود به Scope، budget و no-progress stop. |
| Anti-Overengineering Check | ACCEPTED_WITH_CONSTRAINTS | §۱۳.۶؛ حق حذف mandatory controls را ندارد. |
| specify → plan → tasks → implement | ALREADY_COVERED/EXTENDED | Workflow FEATURE با clarify، analyze و converge تکمیل شد. |
| Requirement checklist as executable claims | ACCEPTED | DoD و Evidence links؛ checklist جای test فنی را نمی‌گیرد. |
| Bug workflow | ACCEPTED | Adaptive Workflow profile BUG. |
| Idea assessment | ACCEPTED | GO/CLARIFY/KILL و عدم اجبار به Implementation. |
| Extension/Preset/Bundle composition | ACCEPTED_WITH_CONSTRAINTS | Workflow Package با precedence، pinning و ownership. |
| Install transparency and idempotency | ACCEPTED | Workflow Package و Tool/MCP Gate. |
| Copy exact Spec Kit commands/layout | REJECTED_AS_UNIVERSAL | SAGE Provider-neutral باقی ماند. |

## ۴. ماتریس Claude Prompt Pack

| Proposal | Disposition | محل ادغام / دلیل |
|---|---|---|
| Product Brief / PRD | ACCEPTED_WITH_CONSTRAINTS | §۲۰.۵؛ فقط با trigger محصول، نه همهٔ Taskها. |
| Repository bootstrap | ACCEPTED | Workflow profile و current→target delta. |
| Deep plan before code | ACCEPTED_WITH_CONSTRAINTS | Plan متناسب با Risk؛ R0 نباید متورم شود. |
| Spec-first contract | ACCEPTED | Goal/Change Scope و Spec deviation. |
| UI/UX Design Contract | ACCEPTED | §۲۰.۵ و Gate trigger رابط کاربر. |
| Incremental implementation | ACCEPTED | Build-Stays-Green و feature slicing. |
| MCP integration controls | ACCEPTED | §۲۰.۳ با source pin، secrets، typed response و rollback. |
| Database integration proof | ACCEPTED | §۲۰.۴ و fixture R2 با write/read proof. |
| Structured security finding | ACCEPTED | §۲۸.۴ و JSON Schema. |
| Evidence-first debugging | ACCEPTED | §۲۱؛ expected/actual، hypothesis، regression evidence. |
| Critical-flow E2E | ACCEPTED_WITH_CONSTRAINTS | Review/Evidence؛ coverage disclosure اجباری. |
| Failure-only screenshots/traces | ACCEPTED_WITH_CONSTRAINTS | کاهش artifact مجاز است، ولی success result و coverage حذف نمی‌شود. |
| Safe dead-code cleanup | ACCEPTED_WITH_CONSTRAINTS | §۲۰.۵؛ نبود reference متنی به‌تنهایی proof نیست. |
| Commit planning | ACCEPTED_WITH_CONSTRAINTS | فقط با درخواست کاربر؛ plan مجوز commit/push نیست. |
| Executable guardrails/hooks | ACCEPTED_WITH_CONSTRAINTS | Adapter شرطی، dry-run و بدون authority inheritance. |
| Convert repetitive task to Skill | ACCEPTED_WITH_CONSTRAINTS | §۱۷.۱۲؛ conformance و forward-test برای موارد پیچیده. |

## ۵. ماتریس Vibe Master Prompt

| Proposal | Disposition | محل ادغام / دلیل |
|---|---|---|
| Role + Context + Goal + Rules | ACCEPTED_AS_BRIEF | Runtime Engineering Brief؛ role به capability محدود شد. |
| Context layers | ACCEPTED/EXTENDED | L0 تا L5 شامل authority، routing، execution، delta، references و evidence. |
| Goal Contract | ACCEPTED | Core object و Schema. |
| Change Scope Contract | ACCEPTED | allowed/restricted/forbidden و deviation. |
| Provider instruction files | ACCEPTED_AS_PROJECTION | source/version و drift باید حفظ شوند. |
| Feature slicing | ACCEPTED | Workflow و Build-Stays-Green. |
| Plan sanity check | ACCEPTED | §۲۰.۵ conditional method. |
| Self-review | ACCEPTED_WITH_LIMIT | Review Protocol؛ self-review مستقل نیست. |
| Always use senior persona | REJECTED_AS_UNIVERSAL | capability fit مهم است، نه persona نمایشی. |
| One giant master prompt | REJECTED_AS_UNIVERSAL | Progressive Disclosure و minimum context حفظ شد. |
| Always stop for approval | REJECTED_AS_UNIVERSAL | Approval برحسب action/risk/policy compile می‌شود. |
| Always use Clean Architecture | REJECTED_AS_UNIVERSAL | architecture gate باید از context واقعی ناشی شود. |

## ۶. ماتریس Strix

| Proposal | Disposition | محل ادغام / دلیل |
|---|---|---|
| Strix as security capability | ACCEPTED_AS_ADAPTER | security.strix optional binding؛ Core dependency نیست. |
| Risk-adaptive activation | ACCEPTED | §۲۸.۱ و security policy. |
| Authorization and scope | ACCEPTED/REQUIRED | §۲۸.۲ و Security Scope Schema. |
| Scan→repair→rescan | ACCEPTED_WITH_CONSTRAINTS | بودجه‌دار؛ Finding مجوز Fix ایجاد نمی‌کند. |
| SARIF/findings/run artifacts | ACCEPTED | Evidence normalization. |
| Exit code interpretation | ACCEPTED | 0/1/2 با run status و coverage تفسیر می‌شوند. |
| Local vs managed | ACCEPTED | modeها جدا route می‌شوند. |
| SENS security telemetry | ACCEPTED_WITH_CONSTRAINTS | proportional و redacted؛ exploit/secret پیش‌فرض ممنوع. |
| Exact CLI/profile defaults as SAGE law | DEFERRED | وابسته به adapter version و environment است. |
| Automatic pentest on security-related work | REJECTED_AS_UNIVERSAL | capability و trigger، authority ایجاد نمی‌کنند. |
| Install or run Strix in this integration | DEFERRED | کاربر آن را جدا مدیریت می‌کند؛ هیچ scan اجرا نشده است. |

## ۷. پوشش ماشین‌خوان

فایل schemas/v0.8/sage-contracts.schema.json این Objectها را پوشش می‌دهد:

- Task Packet، Risk Assessment، Gate Plan و Runtime Engineering Brief
- Skill، Agent Capability، Tool و Provider Adapter
- Evidence Record و Run Event
- Workflow Package
- Security Scope و Security Finding
- Run Contract ترکیبی
- Architecture Model، Element، Relationship، View، Delta و Planned↔Observed Runtime Comparison در `schemas/v0.8/sage-architecture.schema.json`

Fixtureها:

- r0-documentation-typo.json: کنترل proportionality و anti-overengineering
- r2-feature-data-path.json: acceptance، build-stays-green، data-path proof و consistency
- r4-authorized-security-validation.json: authorization، Human Approval، target allowlist، prohibited techniques و restricted evidence
- architecture-model.json: Approved source-of-truth، Stable ID، Relationship resolution و Diagram View

## ۸. محدودیت‌های باقیمانده

- Schema مرجع است و Runtime production هنوز ساخته نشده است.
- cross-object identity و زمان‌بندی expiry فقط بخشی در validator reference بررسی می‌شود؛ Runtime نهایی باید validation معنایی کامل‌تری داشته باشد.
- همهٔ Provider projectionها و package installer واقعی هنوز پیاده‌سازی نشده‌اند.
- Strix CLI/runtime و خروجی واقعی آن در این مرحله آزمایش نشده‌اند.
- Formalization نیازمند independent review و تأیید صریح کاربر است.

## ۹. Independent Review Disposition

بازبینی مستقل اولیه، disposition را `CHANGES_REQUIRED — KEEP AS 0.8.0-draft.3` اعلام کرد. موارد اصلی و اصلاح انجام‌شده:

| Finding | اصلاح | وضعیت |
|---|---|---|
| Agent/Tool/Provider schema ناقص | Schema کامل registry descriptorها و Fixtureهای مستقل اضافه شد. | CLOSED |
| Policy و Gateها جدا از هم | Validator اکنون required_gates را با هر Risk Fixture تطبیق می‌دهد. | CLOSED |
| Security scope بدون semantic readiness | مجوز، allowlist، technique conflict، expiry، ترتیب زمان و evaluation_time اضافه و آزموده شد. | CLOSED |
| Brief با حذف Goal/Non-goal | مقایسهٔ کامل Goal Contract و محدودیت‌های Scope در Validator اضافه شد. | CLOSED |
| Manifest ناقص | SOURCE_MANIFEST.json با Hash تمام ۳۲ ورودی و pinهای upstream اضافه شد. | CLOSED |
| Architecture/Diagram capability غایب | Architecture contract، Policy، Fixture و Validator برای Model/Delta/View/Drift اضافه شد؛ LikeC4 default و Structurizr alternative در قرارداد ثبت شد. | CLOSED |
| Runtime/cryptographic enforcement | عمداً خارج از Draft باقی ماند و در محدودیت‌ها اعلام شد. | DEFERRED |

پس از remediation، Validator مرجع ۱۳۸ بررسی را با صفر خطا پاس کرد. با تأیید صریح کاربر در 2026-09-09، Baseline به `Formalized` ارتقا یافت؛ این امر به معنی production-ready بودن Runtime نیست.
