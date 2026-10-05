# SAGE v0.8.4 — Agent-Native Interface Review Candidate

GitHub channel: **pre-release**. Tag: `v0.8.4`. Security scan: **PENDING**.
This release must not be advertised as a completed Strix scan or a stable,
security-certified package. Full Strix scanning is deferred by user approval
for this publication workflow.

نسخهٔ `0.8.4` قرارداد رابط عامل‌محور را به SAGE اضافه می‌کند و برای بازبینی آماده می‌شود. نسخهٔ تاریخی `0.8.3` حفظ شده است. این بسته دارای گواهی امنیتی نیست؛ اسکن کامل Strix همچنان Pending است.

The `0.8.4` candidate adds agent-facing interface contracts to SAGE. Historical `0.8.3` release records remain preserved. This candidate is not security-certified; a complete Strix scan remains pending.

## Included / تغییرات

- Native API → Thin Bridge → Typed CLI/MCP → Skill architecture contracts.
- CLI, MCP and Bridge standards with ADOPT / ADAPT / BUILD decisions.
- Interface descriptor schema and policy, integrated into discovery and verification.
- Five lifecycle skills plus `interface-audit`, `mcp-review`, and `cli-harness-review`.
- Version-aligned core bundle, skill registry, installable Python SDK and release checks.

The Python SDK currently provides deployment-contract validation. Its installability does not imply that it implements every runtime capability. Interface standards describe conformance requirements; an external integration must provide its own behavioral and smoke-test evidence before it may be marked verified.

## Verification / اعتبارسنجی

Run `./sage.ps1 ci` in PowerShell 7. Preserve the actual command output and confirm that each check covers the advertised behavior. A passing release check establishes package consistency; it does not complete a security scan or certify arbitrary external integrations.

Live execution remains disabled by default. The Strix retry acceptance criteria are recorded in `reports/SAGE_STRIX_SCAN_RETRY_PLAN.md`. Publication, a Git tag and any external execution require the authorized release workflow.

## Reproducible package / بستهٔ قابل‌بازتولید

Git preserves exact file bytes using `.gitattributes`, so the source manifest
and archived-source hashes survive Windows checkout. Final release checks
must pass in a separate clean checkout before publication. Raw scan output,
temporary validation environments and credentials are excluded from Git.
