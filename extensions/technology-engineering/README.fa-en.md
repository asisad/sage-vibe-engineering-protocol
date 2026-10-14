# Technology Engineering — افزونهٔ اختیاری SAGE

Version: 0.1.0 source-branch extension; compatible with the 0.8.4 core package.
No host installation, code-generation provider or new GitHub release is implied.

## فارسی

این افزونه کمک می‌کند انتخاب زبان و فناوری برای هر بخش، دلیل، منبع، محدودیت
و روش آزمون داشته باشد. ۱۷ پروفایل متخصص و ۱۸ Skill دارد؛ همه On-demand هستند.
پشتهٔ فعلی حفظ می‌شود مگر آنکه تغییرش دلیل فنی و هزینهٔ قابل‌قبول داشته باشد.
پیشنهاد با تصویب فرق دارد و تست اجرا‌نشده هرگز PASS نیست.

```powershell
# Review a synthetic decision; no build or external action is performed.
.\sage.ps1 technology -DecisionPath fixtures/extensions/technology-engineering/keep-current-stack.json

# Generate a source-only Mermaid projection in the JSON response.
.\sage.ps1 technology -DecisionPath fixtures/extensions/technology-engineering/keep-current-stack.json -View

# Validate the link to an explicitly supplied architecture model.
.\sage.ps1 technology -DecisionPath fixtures/extensions/technology-engineering/keep-current-stack.json -ArchitecturePath fixtures/extensions/technology-engineering/architecture-model.json

# Discover a declared specialist profile, not an instantiated agent.
.\sage.ps1 specialists -Capability language.python

# A task requiring the extension cannot silently omit its decision.
.\sage.ps1 lifecycle -RequireTechnologyDecision

# Reference tests (local temporary receipts and ledgers only).
.\tools\Test-SageTechnologyEngineering.ps1
```

The lifecycle example without a decision intentionally returns BLOCKED.
To use a real decision, supply `-DecisionPath` and the corresponding `-RunPath`;
their task IDs must match. The three included fixtures are synthetic examples
and cannot be used to assert project-level verification.

## English

The optional extension formalizes requirements-driven language/toolchain choice,
alternatives, tradeoffs, versioned references, stable architecture links and
verification plans. It preserves the five-stage lifecycle and eight core Skills.
There is no Rust-first or fixed always-on team rule. The matching profiles are
declared capabilities only; actual compilers/agents and tool adapters are not
provisioned by this extension.

`technology -Phase PLAN` checks the decision structure/relations while retaining
NOT RUN builds/tests. `-Phase VERIFY` requires the declared mandatory checks and
scoped local artifact hashes; exit code 2 means BLOCKED. Hash integrity is not
proof of compiler execution, benchmark correctness or production safety.
`-View` produces Mermaid source, not a rendered image or approved architecture.

Read `docs/specialist-contract.md` for provenance, authority and physical-system
boundaries. The normative delta is `SAGE_v0.8_TECHNOLOGY_ENGINEERING_DELTA.md`
at the repository root. No toolchain, hardware, Strix scan or provider is started.
