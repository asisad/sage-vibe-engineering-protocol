# SAGE Quickstart — فارسی / English

## فارسی

SAGE وایب‌کدینگ را به یک جریان مهندسی قابل‌ردیابی تبدیل می‌کند.

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
.\sage.ps1 ci
```

اجرای Production در این نسخه فقط Dry-Run است؛ هیچ Target خارجی یا سرور واقعی بدون Scope و Approval اجرا نمی‌شود.

## English

SAGE turns vibe coding into a traceable engineering workflow.

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
.\sage.ps1 ci
```

Production execution is Dry-Run only in this release. External targets require an explicit scope and approval.
