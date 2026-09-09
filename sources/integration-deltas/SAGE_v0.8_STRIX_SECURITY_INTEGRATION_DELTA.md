# SAGE v0.8 — Strix Security Integration Delta

**Document Type:** Security Architecture / Execution Integration Delta  
**Status:** Proposed Integration Input  
**Target:** SAGE v0.8+  
**External Project:** `usestrix/strix`  
**Decision:** GO for architecture integration; local installation/benchmark remains pending.

## 1. Purpose

Strix is integrated into SAGE as a **Conditional Security Tool / Skill Adapter**. It does not replace SAGE Security Architecture, Risk Classification, Quality Gates, approval rules, or verification.

Its role is deeper application-security testing, penetration testing, vulnerability validation, remediation assistance, and CI security scanning when justified by project risk and exposure.

## 2. Reviewed baseline

The reviewed Strix project supports security work against source code, web applications, APIs, domains and network targets. Relevant capabilities include agentic penetration testing, vulnerability discovery/validation, remediation workflows, CI scanning, and structured evidence such as JSON/Markdown/SARIF and run artifacts.

Reviewed technical baseline:
- License: Apache-2.0
- Local runtime: Python >= 3.12
- Docker used for local sandboxed execution
- Local and managed/cloud execution patterns are available
- Repository contains Strix-oriented security Skills/workflows.

Candidate Skills include:

```text
penetration-testing-with-strix
managed-pentesting-with-strix
fix-security-vulnerabilities-with-strix
ci-security-scanning-with-strix
```

Exact Skill schemas and commands MUST be validated against the installed version.

## 3. Architectural placement

```text
SAGE
 │
 ├─ Risk Classifier
 ├─ Policy Engine
 └─ Security Quality Gate
       │
       ├─ Native Security Controls
       │
       └─ Advanced Security
              │
              ▼
         Strix Adapter
          ├─ Skills
          └─ Runtime
              │
              ▼
          Evidence Store
              │
              ▼
           SENS / UEG
```

Native SAGE security controls remain responsible for baseline checks such as secrets, dependencies, secure configuration, authentication/authorization, input validation, architecture security, and Agent/Tool security.

## 4. Risk-adaptive activation

Strix MUST NOT run for every small edit.

```text
R0
→ No Strix by default.

R1
→ Lightweight native security checks.
→ Strix normally skipped.

R2
→ Targeted/Quick Strix when security-relevant or externally exposed.

R3
→ Standard Strix assessment recommended/required by project policy.
→ Independent security review may activate.

R4
→ Explicit authorized scope.
→ Human approval.
→ Standard/Deep assessment as appropriate.
→ Evidence retention.
→ Independent review.
→ Remediation + re-scan.
```

Security-sensitive changes that may activate deeper testing include authentication, authorization, payments, sensitive data, public APIs, uploads, multi-tenancy, admin interfaces, database access control, Agent permissions, MCP/Tool exposure, and secrets handling.

## 5. Security verification loop

```text
SCOPE
 ↓
SCAN
 ↓
VALIDATE FINDING
 ↓
TRIAGE
 ↓
FIX
 ↓
RE-SCAN
 ↓
VERIFY
 ↓
PASS
```

If the vulnerability remains:

```text
RE-SCAN FAIL
 ↓
DIAGNOSE
 ↓
REPAIR
 ↓
RE-SCAN
```

The loop MUST be bounded by attempt, time and cost budgets.

## 6. Circuit Breaker

Stop or escalate when:
- maximum repair attempts are reached;
- no-progress threshold is reached;
- the same failure signature repeats;
- budget/time is exhausted;
- scope expansion is required;
- risk classification increases;
- required permission is unavailable;
- evidence conflicts;
- potentially destructive action is required.

Then:

```text
CIRCUIT BREAK
 ↓
Independent Reviewer / Second Agent
 ↓
Human Approval when required
```

## 7. Implementer / reviewer separation

For material findings, the Agent implementing a security fix SHOULD NOT be the only reviewer.

```text
Security Agent / Strix
 ↓
Finding
 ↓
Implementation Agent
 ↓
Fix
 ↓
Strix Re-scan
 ↓
Independent Reviewer
 ↓
Security Gate
```

Policy may relax this for low-risk findings.

## 8. Evidence Contract

A scan cannot be represented merely as “security passed”.

Normalize evidence including, where available:

```text
Run ID
Authorized target/scope
Scan profile
Start/end time
Completion/coverage status
Findings and severity
Validation evidence
SARIF / JSON / run artifacts
Budget/cost
Remediation status
Re-scan result
Known coverage gaps
```

Core principle:

```text
Process Exit ≠ Security Coverage Complete
```

Quality Gates should evaluate structured completion state, findings, coverage and evidence rather than shell exit status alone.

## 9. Authorization / Scope Contract

Strix MUST only test assets the user/project is authorized to test.

Example:

```yaml
security_scope:
  authorized_targets:
    - local-development-app
    - staging-api
  forbidden_targets:
    - production-unless-explicitly-approved
    - unauthorized-third-party-systems
  network_access: restricted
  destructive_testing: false
  credential_use: scoped
  max_budget: defined
  max_duration: defined
```

Preserve:

```text
Capability ≠ Permission ≠ Authority
```

Runtime security session:

```text
Agent
+ Skill
+ Tool
+ Granted Permissions
+ Granted Authority
+ Scope
+ Budget
+ Policies
```

## 10. Local vs managed execution

### Local

```text
SAGE
 ↓
Strix Adapter
 ↓
Local Strix CLI
 ↓
Docker Sandbox
```

Current identified requirements:
- Python >= 3.12
- Docker
- Strix runtime/dependencies
- applicable model/provider configuration

### Managed

```text
SAGE
 ↓
Strix Adapter
 ↓
Managed Strix Service
```

Policy Engine chooses based on privacy, data classification, cost, network, compliance and project policy.

## 11. Installation and validation plan

Installation has NOT yet been executed. Before activation:

```text
1. Re-read exact current official install instructions.
2. Read exact current official Strix Skills.
3. Record version/commit.
4. Install Skills in isolated/project scope.
5. Install CLI/runtime.
6. Verify Python and Docker requirements.
7. Verify CLI version.
8. Run only an authorized local fixture.
9. Capture structured evidence.
10. Validate SARIF/JSON output.
11. Test failure behavior.
12. Test incomplete/budget-limited behavior.
13. Measure repository/environment/Docker footprint.
14. Measure execution time and approximate model cost.
15. Validate uninstall/rollback.
16. Run SAGE adapter conformance tests.
```

Do not enable global/organization-wide installation until isolated validation passes.

## 12. Footprint measurement

Repository size is NOT installed size.

Measure separately:

```text
Git repository
Python environment
Installed packages
Docker image(s)
Caches
Generated artifacts
Runtime temporary data
Total incremental disk usage
```

A definitive footprint remains pending real installation.

## 13. Anti-Overengineering

Do NOT:
- run deep pentests for trivial/text-only changes;
- run every Strix Skill for every task;
- retain large artifacts from successful trivial runs;
- send the whole repository when targeted context is enough;
- run unlimited repair/re-scan loops;
- duplicate SAGE security subsystems;
- make Strix mandatory where it adds no value.

Prefer:
- risk-adaptive scan depth;
- targeted scope;
- budget/time limits;
- failure-focused diagnostics;
- policy-based evidence retention;
- incremental checks.

## 14. Normalized scan profiles

SAGE may expose provider-neutral profiles:

```text
NONE
LIGHT
QUICK
STANDARD
DEEP
```

Conceptually:

```text
LIGHT    → native SAGE checks
QUICK    → targeted Strix assessment
STANDARD → broader security assessment
DEEP     → approved high-risk assessment
```

Exact CLI mapping belongs in the versioned Strix Adapter, not SAGE Core.

## 15. Security Finding normalization

Example:

```yaml
finding:
  id: SEC-001
  source: strix
  category: authorization
  severity: high
  confidence: high
  target:
    component: api
    location: "..."
  evidence:
    artifact_refs:
      - "..."
  remediation:
    status: open
    proposed_fix: "..."
  verification:
    rescan_required: true
    independent_review_required: true
```

This allows Strix to coexist with other security engines.

## 16. Tool Registry concept

```yaml
id: strix
type: security_testing
provider: usestrix

capabilities:
  source_code_security: true
  web_security: true
  api_security: true
  vulnerability_validation: true
  remediation_support: true
  ci_integration: true
  sarif_output: true

execution:
  local: true
  managed: true

requirements:
  authorization: required
  scoped_target: required

risk:
  active_security_testing: true
  network_interaction: possible
  destructive_actions: policy_controlled
```

Final fields must conform to the formal SAGE v0.8 Tool Registry Schema.

## 17. Skill Router behavior

Route by capability, not product name:

```text
Security Intent
 ↓
Required Security Capability
 ↓
Security Skill
 ↓
Tool Router
 ↓
Strix selected only if capability + policy + scope match
```

This preserves tool/provider independence.

## 18. SENS integration

Useful normalized telemetry:

```text
Scan started/completed
Duration
Target class
Scan profile
Findings by severity
Validated findings
Repair attempt count
Re-scan result
Budget/cost
Failure reason
Circuit breaker activation
```

Do not ingest secrets, credentials, unnecessary exploit payloads or oversized raw logs by default.

SENS remains out-of-band, fail-open and bounded.

## 19. Security Quality Gate

```text
SECURITY_GATE

Inputs:
- Risk classification
- Exposure classification
- Security-sensitive flags
- Native security results
- Strix evidence if activated
- Independent review if required

PASS:
- required scans completed;
- blocking findings resolved/accepted under policy;
- required re-scans passed;
- evidence valid;
- approvals present.

FAIL:
- blocking validated finding remains;
- required scan incomplete;
- evidence invalid/missing;
- scope violation occurred.

ESCALATE:
- risk changed;
- remediation requires expanded authority;
- evidence conflicts;
- circuit breaker triggered.
```

## 20. Dynamic Definition of Done

For security-relevant work:

```text
Security scope defined             ✓
Required security checks executed  ✓
Blocking findings resolved         ✓
Re-scan completed                  ✓
Evidence recorded                  ✓
Independent review (if required)   ✓
Security Gate PASS                 ✓
```

These do not automatically activate for unrelated R0/R1 work.

## 21. Frozen integration decisions

Accepted architectural direction:

```text
1. Strix is NOT SAGE Core.
2. Strix is a conditional Security Tool/Skill Adapter.
3. SAGE remains provider/tool agnostic.
4. Native SAGE security controls remain.
5. Activation is risk/scope adaptive.
6. Active testing requires authorization.
7. Security loops are bounded by budget/time/attempts.
8. Findings require structured evidence.
9. High-risk remediation may require independent review/human approval.
10. SENS receives normalized proportional telemetry.
11. Installation is validated in isolation first.
12. Actual installed footprint is measured, not guessed.
```

## 22. Pending decisions

Not yet finalized:

```text
Exact Strix version pin
Exact CLI mapping
Actual Docker/Python footprint
Exact Skill installation scope
Managed vs local default
Default budgets/durations
Default R2/R3/R4 profiles
Exact SARIF ingestion
Exact SENS security event schema
Exact CI blocking thresholds
```

## 23. Next action

```text
1. Place this Delta beside the other SAGE v0.8 integration deltas.
2. Compare it with the current Execution Protocol & Skill Contract.
3. Mark requirements COVERED / PARTIAL / MISSING.
4. Extend existing contracts without duplication.
5. Install Strix + official Skills in isolated scope.
6. Run authorized fixture tests.
7. Measure actual footprint/performance/cost.
8. Produce installation/validation evidence.
9. Update this Delta from PROPOSED to VALIDATED if tests pass.
10. Add relevant SAGE conformance tests.
```

## 24. Status

```text
STRIX REPOSITORY REVIEW        COMPLETE
SECURITY CAPABILITY REVIEW     COMPLETE
SAGE ARCHITECTURE FIT          PASS
PROVIDER-AGNOSTIC FIT          PASS
ANTI-OVERENGINEERING FIT       PASS WITH CONDITIONAL ACTIVATION
SECURITY GUARDRAILS            DEFINED
SENS INTEGRATION DIRECTION     DEFINED

LOCAL INSTALLATION             NOT YET EXECUTED
REAL FOOTPRINT MEASUREMENT     PENDING
FIXTURE SECURITY TEST          PENDING
ADAPTER CONFORMANCE TEST       PENDING

ARCHITECTURE DECISION          GO
```

## 25. Final principle

```text
SAGE defines when security testing is required.
The Security Skill defines how assessment is performed.
The Tool Router decides whether Strix is appropriate.
Strix performs authorized security work.
Evidence proves what happened.
Quality Gates decide whether the result is acceptable.
SENS observes the process.
Human authority remains above high-risk actions.
```

Strix strengthens SAGE Security Engineering without turning SAGE into a Strix-specific architecture.
