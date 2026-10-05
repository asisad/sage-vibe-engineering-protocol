# SAGE Quickstart — فارسی / English

## فارسی

SAGE وایب‌کدینگ را به یک جریان مهندسی قابل‌ردیابی تبدیل می‌کند.

نسخهٔ محلی 0.8.4 یک Review Candidate است. برای قواعد جدید interface،
`SAGE_v0.8.4_AGENT_NATIVE_INTERFACE_DELTA.md` را کنار Baseline بخوانید.
Bundle شامل پنج Skill چرخه و سه Skill بازبینی interface است؛ Skillهای بازبینی
مراحل اجباری تازه در هر Task ایجاد نمی‌کنند.

### نصب SDK

```powershell
python -m pip install ./sdk/python
```

### اعتبارسنجی قرارداد

```powershell
python -m sage_sdk validate fixtures/v0.8.2/deployment-contract.json
```

### اجرای کنترل‌های SAGE

```powershell
.\sage.ps1 validate
.\sage.ps1 demo
.\sage.ps1 operations
.\sage.ps1 interfaces -Capability json-schema-validation
.\sage.ps1 lifecycle
.\sage.ps1 ci
```

اجرای Production در این نسخه فقط Dry-Run است؛ هیچ Target خارجی یا سرور واقعی بدون Scope و Approval اجرا نمی‌شود.
ترتیب Skillها در رجیستری `skills/registry.json` کنترل می‌شود: `intake → discover → plan → implement → verify`. مرحلهٔ Discover فقط پیشنهاددهنده است و مجوز اجرا نمی‌دهد؛ Implement فقط با Plan تأییدشده مجاز است.

## English

SAGE turns vibe coding into a traceable engineering workflow.

The local 0.8.4 Review Candidate adds versioned interface validation and
advisory discovery. Read the Agent-Native addendum with the preserved baseline.
Three conditional review Skills accompany the five lifecycle Skills.

### Install the SDK

```powershell
python -m pip install ./sdk/python
```

### Validate a contract

```powershell
python -m sage_sdk validate fixtures/v0.8.2/deployment-contract.json
```

### Run SAGE checks

```powershell
.\sage.ps1 validate
.\sage.ps1 demo
.\sage.ps1 operations
.\sage.ps1 lifecycle
.\sage.ps1 ci
```

Production execution is Dry-Run only in this release. External targets require an explicit scope and approval.
The `interfaces` command selects validated descriptor candidates, using
synthetic fixtures by default; it does not execute their declared transports.
The lifecycle order is enforced by `skills/registry.json`: `intake → discover → plan → implement → verify`. Discover is advisory and never grants authority; Implement requires an approved plan.
