# SAGE — Vibe Engineering Protocol & Runtime Kit

SAGE is a provider-neutral protocol and runtime kit for turning vibe-coding intent into scoped, reviewable, evidence-backed engineering work. Its core governs the lifecycle; an optional bounded runtime generates and checks code for supported local profiles. It is not a domain-specific application or a universal software factory.

## Development branch: bounded autonomous execution

The additive [`sage-runtime` package](runtime/autonomous/README.fa-en.md) connects
the protocol to actual, authorized local work: structured planning, on-demand
SAGE/ECC sources, exact plan approval, controller-applied files, sandbox checks,
fresh-session review and bounded repair/resume. It starts **non-live by default**.
The preserved reference lifecycle below remains Dry-Run; installation does not
activate hooks, deploy software or publish anything. This development addition
is not part of the historical `v0.8.4` tag or a security certification.

```powershell
python -m pip install ./runtime/autonomous
sage doctor
sage build "Build a small Python stdlib library with unittest tests" --output C:\SageWork\new-project
# Add --live --approval-id TASK-ID only for your explicitly authorized task.
```

نسخهٔ توسعه، چرخهٔ اجرایی واقعی و محدود دارد؛ فایل تولیدی ابتدا داده است و فقط
کنترل‌کنندهٔ SAGE آن را پس از بررسی محدوده می‌نویسد. آزمون واقعی به محیط ایزوله
نیاز دارد. پروژهٔ قدیمی را می‌توان با `--source` به خروجی تازه کپی و اصلاح کرد؛
اصل پروژه تغییر نمی‌کند. [معماری و مرزها](SAGE_AUTONOMOUS_RUNTIME_DELTA.md).

## فارسی

OpenHands SDK `1.58.1` was evaluated as a second coding engine. Two isolated
SAGE deliveries passed, but incremental value under the current worker contract
was not demonstrated, so no SDK dependency or production adapter was added.
The default and Ruflo binding remain unchanged.
[Decision and evidence](docs/verification/OPENHANDS_SDK_v1.58.1_EVALUATION.fa-en.md).

بررسی OpenHands پایان یافت؛ اتصال آزمایشی موفق بود، اما فایدهٔ افزودهٔ کافی
اثبات نشد و به محصول اضافه نشد. جزئیات و محدودیت‌ها در گزارش بالاست.

SAGE یک پروتکل و کیت Runtime برای تبدیل وایب‌کدینگ به کار مهندسیِ دارای Scope، تست، امنیت، شواهد و قابلیت Rollback است.

## What it provides

- deterministic intake, clarification and risk classification (R0–R4)
- architecture modeling and Diagram-as-Code contracts
- generic Agent/Skill/Tool/Provider discovery and routing
- authority, scope, security and approval gates
- workflow state machine and tamper-evident evidence ledger
- convergence checks between specification, implementation and observed reality
- an optional, attributed capability library combining SAGE with 311 ECC Skills
  and 71 ECC agent definitions, with per-item overlap decisions and on-demand
  source packets

## Capability library — SAGE × ECC

Open [`docs/catalog/index.html`](docs/catalog/index.html) locally for the Persian
searchable catalog. It includes 425 definitions: 337 Skills and 88 agent/role
profiles across SAGE and ECC. These are attributed source definitions; functional
coverage and live bindings are tracked separately.

```bash
python extensions/ecc/sage_ecc.py search "Rust review" --json
python extensions/ecc/sage_ecc.py plan --task "Review a Rust service" --scope "src/" --json
python extensions/ecc/sage_ecc.py show ecc.agent.code-reviewer --json
```

کتابخانهٔ قابل‌جست‌وجوی فارسی، رابطهٔ هر قابلیت با سیج و دلیل اضافه‌شدن یا تقویت
را نشان می‌دهد. ابزار Python منابع انتخاب‌شده و مجوزهای آن‌ها را در یک بستهٔ
مستقل آماده می‌کند. دستورها، تنظیمات میزبان و حلقه‌های خودکار ECC با این کار
فعال نمی‌شوند. [راهنمای استفاده](extensions/ecc/README.fa-en.md)،
[ماتریس کامل تطبیق](extensions/ecc/review/OVERLAP-MATRIX.fa.md) و
[تصمیم معماری](SAGE_v0.8_ECC_CAPABILITY_DELTA.md) جزئیات را ثبت می‌کنند.

## Optional Ruflo real MCP runtime

The development `sage-runtime 0.2.0` additionally has a real, isolated Ruflo
task-coordinated **external Codex worker** binding. It is opt-in per run,
preserves SAGE ownership and does not enable native Ruflo LLMs or its whole
catalog. See [live binding and setup](extensions/ruflo/LIVE_BINDING.fa-en.md)
and [observed acceptance](extensions/ruflo/live-acceptance.json), with a
[bilingual local delivery report](docs/RUFLO_LIVE_ACCEPTANCE.fa-en.md).

در نسخهٔ توسعهٔ ۰٫۲٫۰، هماهنگی کار با Ruflo و اجرای واقعی عامل Codex زیر کنترل
SAGE متصل شده‌اند؛ این با فعال‌کردن تمام عامل‌ها یا `agent_execute` داخلی Ruflo
یکسان نیست. راهنما و شواهدِ بالا مرز دقیق این اتصال را نشان می‌دهند.

The Ruflo integration is a separately gated, version-pinned executable MCP
adapter. It **does not** automatically install or start upstream services.
It preserves SAGE's authority, scope, evidence and existing DRY_RUN baseline.
Unlike the ECC static catalog, this integration can negotiate with an actual
MCP server, discover available tools and invoke approved tools.

Source/overlap/risks: [Ruflo integration guide](extensions/ruflo/README.fa-en.md),
[capability mapping](extensions/ruflo/CAPABILITY-MAP.fa.md), and
[explicit policy](extensions/ruflo/policy.json).

Use Python 3.11+ (and Node 20+ for the real upstream runtime):

    python extensions/ruflo/sage_ruflo.py status
    python extensions/ruflo/sage_ruflo.py probe --workspace /absolute/disposable/workspace --live
    python extensions/ruflo/sage_ruflo.py list --workspace /absolute/disposable/workspace --live

PowerShell 7:

    .\sage.ps1 ruflo -RufloAction status

Tools/call and multi-step batches require exact tool allowlists, a time-limited
approval document, and for mutating/unknown tools a matching approved native
SAGE RunContract with passing gates, an explicit host-access acknowledgement
and a separately isolated workspace. The adapter is **not an OS sandbox**.
Returned execution is labeled EXECUTED_UNVERIFIED until an independent SAGE
acceptance test proves the requested result. Synthetic and errored results
cannot be accepted as evidence.

The source extension and fake-server contract tests do not prove live Ruflo
was installed on the user's PC, model credentials, or autonomous product
creation. Host receipts and a real code-change acceptance run are separate
release gates; see the integration guide.

## Quick start

Use PowerShell 7:

```powershell
.\sage.ps1 validate
.\sage.ps1 demo
.\sage.ps1 discover -Capability json-schema-validation
.\sage.ps1 operations
.\sage.ps1 interfaces -Capability json-schema-validation
.\sage.ps1 lifecycle

# Optional Python SDK
python -m pip install ./sdk/python
python -m sage_sdk validate ./fixtures/v0.8.2/deployment-contract.json
```

The demo is intentionally domain-neutral and does not contact networks or execute external tools. Live adapters require a separately reviewed target, scope and approval.

`interfaces` validates/discovers the synthetic reference descriptors and returns
advisory candidates. Use `-RegistryPath` for an owned descriptor directory;
selection is not evidence of a functioning live CLI/MCP/host connection.

## Repository map

- `SAGE_v0.8_EXECUTION_PROTOCOL_AND_SKILL_CONTRACT.md` — formalized protocol baseline
- `schemas/` and `policies/` — machine-readable contracts
- `runtime/reference/` — executable reference behavior
- `runtime/production/` — controlled production boundary (DRY_RUN by default)
- `runtime/production/SageOperations.psm1` — deployment-plan and operations-gate runtime (DRY_RUN by default)
- `skills/` — SAGE lifecycle Skill Pack (`intake → discover → plan → implement → verify`)
- `skills/registry.json` — ordered lifecycle registry and authority boundaries for the Skill Pack
- `bundles/` — versioned role/workflow bundles
- `examples/` — public demonstrators
- `docs/diagrams/` — editable Diagram-as-Code architecture model for SAGE
- `docs/architecture/` — Agent-Native interface standards for API, Bridge, CLI and MCP
- `docs/decisions/` — recorded interface-selection and reuse decisions
- `SAGE_v0.8.4_AGENT_NATIVE_INTERFACE_DELTA.md` — normative Agent-Native extension to the preserved protocol baseline
- `tools/` — validation and CI entrypoints
- `sdk/python/` — installable, dependency-free contract SDK
- `schemas/v0.8/sage-agent-interface.schema.json` — typed Agent-Native interface descriptor
- `SAGE_v0.8.1_AGENTIC_ENGINEERING_ENHANCEMENTS_DELTA.md` — approved enhancement delta (Context, Workflow, Sensors, Evaluation, AI-SSDF)
- `SAGE_v0.8.2_PRODUCTION_DELIVERY_OPERATIONS_DELTA.md` — production delivery and operations contracts
- `docs/RELEASE_READINESS.fa-en.md` — bilingual release gates, delivery status and acceptance criteria
- `docs/INFOGRAPHIC_HANDOFF.fa-en.md` — bilingual brief for architecture/process infographic production

## Status

Source-branch optional extension (2026-10-23): ECC capability catalog 0.1 pins
`affaan-m/ECC` at `90606c8315ee09cafc303515c5f33024db6b9882`. It adds static
per-definition review, a portable descriptor registry, offline catalog UI,
advisory routing and bounded source export. Generic, Codex and Claude exports
are source packets; this extension provisions no native runtime or live website.
The published v0.8.4 release remains separate from these source-branch additions.

Source-branch optional extension (2026-10-14): technology-engineering 0.1 adds
requirements-driven technology decisions, 17 declared on-demand specialist
profiles and 18 optional Skills. See
`extensions/technology-engineering/README.fa-en.md` and
`SAGE_v0.8_TECHNOLOGY_ENGINEERING_DELTA.md`. These source additions are **not in the
published v0.8.4 tag**; it installs no agents/toolchains and performs no live work.

افزونهٔ انتخاب فناوری در شاخهٔ توسعه اضافه شده است: انتخاب مستدل زبان و ساختار، پروفایل
متخصص و برنامهٔ آزمون. این افزوده در Tag قبلی نیست و به معنی اجرای تیم یا نصب
ابزار نیست. هشت Skill هسته و نسخهٔ SDK حفظ شده‌اند.

SENS has a dedicated connection slot at [`integrations/sens/`](integrations/sens/README.fa-en.md).
Its independent implementation can submit a protocol-compatible proposal using
the handoff there. Default mode is DISABLED; offline contracts/preview are not a
deployed SENS service, a live transport or authority to change SAGE.

جایگاه اتصال پروژهٔ مستقل SENS در `integrations/sens/` آماده است. معرفی SENS
فقط پیشنهادی برای بازبینی است؛ نصب، فعال‌سازی یا استقرار خودکار انجام نمی‌شود.

GitHub delivery: `v0.8.4` is a **pre-release / Review Candidate**, not a
security-certified stable release. A complete Strix scan is still pending;
interrupted historical scans are not security evidence. See
`SAGE_v0.8.4_AGENT_NATIVE_RELEASE.md` for the release scope and limitations.

انتشار GitHub نسخهٔ `v0.8.4` از نوع **پیش‌انتشار / نامزد بازبینی** است.
اسکن کامل Strix هنوز انجام نشده و این نسخه تأییدیهٔ امنیتی ندارد.

Version `0.8.0` remains the preserved Formalized Baseline; `0.8.3` remains the historical package. The current local `0.8.4` Review Candidate adds Agent-Native descriptor validation/discovery and eight bundled Skills. The Python SDK provides deployment-contract validation; lifecycle and invocation planning remain reference/Dry-Run. A general autonomous product-building runtime and all live CLI/MCP/host bindings are not established by these tests. External integrations require their own evidence.

The lifecycle bundle is deliberately ordered: discovery is advisory and cannot authorize execution; implementation requires an approved plan; verification returns `DONE`, `BLOCKED` or `ESCALATED` from evidence. Agent-facing interfaces follow `Native API → Thin Bridge → Typed CLI/MCP → Skill`; capability discovery never grants authority. The bundle and `skills/registry.json` must agree before release.
