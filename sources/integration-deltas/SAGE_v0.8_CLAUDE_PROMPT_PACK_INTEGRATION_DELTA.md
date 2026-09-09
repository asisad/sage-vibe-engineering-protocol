# SAGE v0.8 — Claude Prompt Pack Integration Delta

**Source:** `15 Claude Code Vibe Coding Prompts.pdf`  
**Status:** Proposed integration input for SAGE v0.8  
**Use with:** `SAGE_v0.7_MASTER_BASELINE.md`, `SAGE_HANDOFF_v0.7_to_v0.8.md`, `SAGE_v0.8_SPEC_KIT_INTEGRATION_DELTA.md`

---

# 1. Purpose

This file records the gap analysis between the full 15-prompt Claude Code pack and the current SAGE architecture.

The PDF is a **reference/pattern source**, not a new methodology and not an authoritative architecture.

Each idea is classified as:
- ALREADY COVERED
- IMPROVE EXISTING
- NEW EXECUTION PATTERN / SKILL
- PROVIDER ADAPTER ONLY
- REJECT / REDUNDANT

SAGE must avoid duplicating prompt logic already covered by its Constitution, Execution Protocol, Quality Gates, or Skill Contract.

---

# 2. Executive Conclusion

The PDF strongly aligns with SAGE:
- plan before risky coding;
- spec before implementation;
- repository-aware instructions;
- incremental build steps;
- evidence-based debugging;
- human approval for sensitive changes;
- security review;
- regression and E2E testing;
- clean Git history;
- executable guardrails;
- repeated workflows converted into Skills.

Most concepts already exist in SAGE at the architectural level.

The strongest practical additions for v0.8 are:

1. Repository Bootstrap Profile
2. Current-State → Target-State Delta
3. Spec Deviation Protocol
4. UI/UX Design Contract
5. Build-Stays-Green Principle
6. Risk-First Unknown Resolution
7. Tool/MCP Integration Gate
8. Data Path Proof
9. Structured Security Finding Contract
10. Evidence-First Debugging Protocol
11. Failure-Only Diagnostic Artifact Capture
12. E2E Coverage Disclosure
13. Safe Code Cleanup Pattern
14. Commit Planning
15. Executable Guardrail Adapter
16. Skill Dry-Run / Conformance Testing

---

# 3. Prompt-by-Prompt Review

## 01 — PRD

**Status:** ALREADY COVERED / IMPROVE EXISTING

SAGE already has Product Intent, Spec, Acceptance Criteria, Clarification Gate, and Dynamic DoD.

Add an optional **Product Brief / PRD Profile** for new products or substantial features:
- problem;
- success metrics;
- users/stories;
- scope/non-goals;
- data impact;
- edge/failure cases;
- open questions.

Do not require this for R0–R1.

**Target:** `product-discovery` / `feature-spec`.

---

## 02 — CLAUDE.md project guide

**Status:** IMPROVE EXISTING

SAGE already has Repository Discovery, Context Manager, Repository-as-Source-of-Truth, and project instructions.

Formalize a provider-neutral **Repository Bootstrap Profile** that extracts:
- project purpose;
- important stack versions;
- dev/build/test/lint commands;
- architecture map;
- actual code conventions;
- no-go rules;
- common gotchas.

Provider-specific files such as `CLAUDE.md`, `AGENTS.md`, or future equivalents are **projections/adapters**, not the source of truth.

**Target:** `repository-discovery` + `context-engineering`.

---

## 03 — Deep planning before coding

**Status:** ALREADY COVERED / REINFORCE

Add a standard planning primitive:

```text
Current-State → Target-State Delta
```

For R2+:
- inspect affected files;
- describe current behavior;
- describe target behavior;
- compare alternatives/trade-offs;
- estimate blast radius;
- define rollback where relevant;
- split into verifiable slices.

**Target:** `implementation-planning`.

---

## 04 — Spec-driven development

**Status:** CORE ALREADY COVERED

This aligns with SDAE core, Clarification Gate, Spec Kit integration, Convergence Engine, and Cross-Artifact Consistency.

Add a formal **Spec Deviation Protocol**:

```text
Evidence shows approved Spec is wrong/impossible
→ STOP
→ record deviation evidence
→ propose/update Spec
→ re-evaluate risk and gates
→ resume under policy/approval
```

**Target:** `feature-spec` + `convergence-engine`.

---

## 05 — UI/UX design brief

**Status:** PARTIALLY COVERED

Add a reusable **UI/UX Design Contract**:
- user journey;
- screen/flow hierarchy;
- responsive breakpoints;
- component state matrix;
- typography/color tokens;
- motion;
- accessibility;
- reference inspiration with explicit non-copy rule.

**Target:** `frontend-ui-ux`.

---

## 06 — Incremental implementation plan

**Status:** IMPORTANT IMPROVEMENT

Formalize two principles.

### Build-Stays-Green Principle

Each implementation slice SHOULD leave the project in a verifiable and preferably buildable/runnable state.

### Risk-First Unknown Resolution

High-risk unknowns SHOULD be investigated earlier when doing so reduces rework or prevents a wrong architecture path.

Each slice should define:
- touched files;
- intended change;
- verification;
- dependency/migration impact;
- size/complexity.

**Target:** `implementation-planning` + `incremental-build`.

---

## 07 — MCP server integration

**Status:** PARTIALLY COVERED

SAGE already has Tool/MCP architecture, Tool Registry, security, and dependency governance.

Add a **Tool / MCP Integration Gate**:

```text
Existing maintained implementation?
License/security acceptable?
Only minimum required capabilities exposed?
Secrets isolated?
Typed contract/error behavior?
End-to-end tool call verified?
Usage documented?
```

Provider-specific MCP configuration belongs in adapters.

**Target:** `tool-integration` / `mcp-integration`.

---

## 08 — Database integration

**Status:** MOSTLY COVERED

SAGE already has schema versioning, migrations, rollback/roll-forward, integrity, security, and verification.

Add **Data Path Proof** for new persistence integrations:

```text
Migration applied
→ known seed/write
→ read through actual application path
→ compare expected result
→ record evidence
```

This proves the real data path, not only schema existence.

**Target:** `database-integration` / `database-migration`.

---

## 09 — Security gap audit

**Status:** ALREADY COVERED / IMPROVE EVIDENCE

Add a structured Security Finding Contract:

```text
id
severity
category
location
evidence
exploitability
impact
recommended_fix
allowed_autofix
human_review_required
```

SAGE MUST NOT automatically fix security findings outside the granted scope/authority.

**Target:** `software-security`.

---

## 10 — Evidence-based debugging

**Status:** STRONGLY ALIGNED / FORMALIZE

Add a formal **Evidence-First Debugging Protocol**:

```text
REPRODUCE
→ EXPECTED vs ACTUAL
→ RANK HYPOTHESES
→ PROVE / ELIMINATE WITH EVIDENCE
→ ROOT CAUSE
→ FIX
→ SEARCH FOR SAME PATTERN
→ REGRESSION TEST
→ VERIFY
```

This plugs directly into the existing Verify–Diagnose–Repair Loop and Circuit Breaker.

**Target:** `structured-debugging` + Repair Loop Controller.

---

## 11 — Playwright E2E

**Status:** PARTIALLY COVERED

Add three execution rules:

### Critical-Flow Priority
E2E SHOULD prioritize business-critical and user-critical paths.

### Failure-Only Artifact Capture
Large screenshots, traces, and diagnostics SHOULD normally be captured on failure rather than on every successful run.

This aligns with SAGE Anti-Overengineering and proportional SENS telemetry.

### Coverage Disclosure
Test output SHOULD disclose important known coverage gaps, not just PASS/FAIL.

**Target:** `test-strategy` + `frontend-ui-ux`.

---

## 12 — Safe dead-code removal

**Status:** NEW USEFUL MAINTENANCE PATTERN

Add a generalized **Safe Code Cleanup Pattern**:

```text
Discover candidate
→ verify references/usages
→ account for dynamic/string references
→ classify confidence
→ delete/refactor small slice
→ build/test
→ keep uncertain candidates for review
```

Low-confidence deletion SHOULD NOT be automated.

**Target:** `code-simplification` / maintenance skill.

---

## 13 — Clean Git commits

**Status:** MOSTLY COVERED

SAGE already uses Conventional Commits and traceable changes.

Add optional **Commit Planning** for R2+ or broad changes:
- logical commit boundaries;
- files per commit;
- proposed messages;
- keep refactor separate from behavior change where practical;
- exclude secrets and irrelevant generated artifacts.

Do not require human approval between every ordinary commit unless project policy requires it.

**Target:** `git-versioning`.

---

## 14 — Hooks as guardrails

**Status:** IMPORTANT NEW EXECUTION PATTERN

Do not make Claude hooks a SAGE core dependency.

Add a generic **Executable Guardrail Adapter**:

```text
Policy / Gate
      ↓
Platform Adapter
      ↓
Hook / CI Check / Pre-commit / Tool Policy / Sandbox Rule
```

Core principle:

> Stable repeated rules SHOULD move from prompts to executable enforcement where practical.

Examples:
- protected paths;
- lint/typecheck;
- mandatory verification;
- approval points;
- notifications.

Anti-overengineering rule:
Do not run expensive full suites after every tiny edit unless risk/policy requires it.

**Target:** `ci-quality-gates` + `policy-enforcement`.

---

## 15 — Repetitive task → Skill

**Status:** CORE TO v0.8 SKILL CONTRACT

Strongly validates SAGE Skill architecture.

Add **Skill Conformance / Dry-Run** requirements:

```text
Schema validation
Trigger test
Dry-run fixture
Expected output comparison
Failure/edge-case test
Done-criteria test
```

A `SKILL.md` file existing is not enough to declare a Skill valid.

Claude-specific paths such as `.claude/skills/...` remain provider-adapter details.

**Target:** `SAGE_SKILL_CONTRACT`.

---

# 4. What SAGE Already Has

No redesign is needed for these existing decisions:

- Spec-driven development
- R0–R4 risk model
- Dynamic Quality Gates
- Dynamic Definition of Done
- Human approval by risk
- Repository as Source of Truth
- Software Architecture governance
- Database/Migration governance
- Application and Agent security
- Regression/E2E testing
- Evidence-based verification
- Autonomous controlled Repair Loop
- Circuit Breaker and independent diagnosis
- Conventional Commits
- Documentation-by-Design
- Tool/MCP layer
- Skill architecture
- Proportional Engineering / Anti-overengineering

---

# 5. Recommended Additions to v0.8

## CORE execution refinements

```text
Current-State → Target-State Delta
Spec Deviation Protocol
Build-Stays-Green Principle
Evidence-First Debugging Protocol
Executable Guardrail Abstraction
Skill Dry-Run / Conformance
```

## CONDITIONAL capabilities

```text
Product Brief / PRD Profile
UI/UX Design Contract
Tool/MCP Integration Gate
Data Path Proof
Structured Security Finding Contract
Failure-Only E2E Artifacts
E2E Coverage Disclosure
Safe Code Cleanup
Commit Planning
```

## PROVIDER ADAPTER ONLY

```text
CLAUDE.md-specific syntax
Claude hook event names/settings
.claude/skills path
Claude settings.json
```

These MUST NOT become SAGE core architecture.

---

# 6. Integration with the Spec Kit Delta

The existing Spec Kit Delta adds:

```text
Clarification Gate
Cross-Artifact Consistency Analysis
Convergence Engine
Anti-Overengineering Check
```

The PDF patterns strengthen them:

```text
Clarification Gate
+ PRD and Current-vs-Target framing

Consistency Analyzer
+ per-step verification
+ coverage disclosure

Convergence Engine
+ Evidence-First Debugging
+ Regression Protection
+ Data Path Proof

Anti-Overengineering
+ Failure-only diagnostic artifacts
+ minimum tool exposure
+ risk-adaptive executable hooks
```

Both deltas should be consumed together during SAGE v0.8 formalization.

---

# 7. Recommended Source Placement

Keep the original PDF as a reference source, for example:

```text
/sources/reference/
  15-Claude-Code-Vibe-Coding-Prompts.pdf
```

Do NOT load the 33-page PDF into every Agent session.

Use this Delta as the distilled design input.

Recommended read order:

```text
1. SAGE_HANDOFF_v0.7_to_v0.8.md
2. SAGE_v0.7_MASTER_BASELINE.md
3. SAGE_v0.8_SPEC_KIT_INTEGRATION_DELTA.md
4. SAGE_v0.8_CLAUDE_PROMPT_PACK_INTEGRATION_DELTA.md
5. SAGE_v0.8_EXECUTION_PROTOCOL_AND_SKILL_CONTRACT.md
```

---

# 8. Instruction to the SAGE Project Agent

Use this file as an **integration delta**, not as permission to copy all 15 prompts.

For every recommendation:

1. Inspect the current v0.8 draft.
2. If already implemented, mark `COVERED`.
3. If partially implemented, extend the existing contract rather than creating a duplicate.
4. If absent and useful, place it in the correct layer:
   - Execution Protocol
   - Quality Gate
   - Skill Contract
   - Tool/Provider Adapter
   - Verification/Repair Protocol
5. Keep Claude-specific syntax in the Claude adapter.
6. Add/update conformance tests for executable rules.
7. Run Anti-Overengineering Check before creating a new file, skill, or schema.
8. Do not modify frozen v0.7 decisions without new evidence.

---

# 9. Decision Status

```text
PDF REVIEW              COMPLETE
15 PROMPTS               REVIEWED
SAGE GAP ANALYSIS        COMPLETE

ADD / FORMALIZE:
- Repository Bootstrap Profile
- Current-State → Target-State Delta
- Spec Deviation Protocol
- UI/UX Design Contract
- Build-Stays-Green
- Risk-First Unknown Resolution
- Tool/MCP Integration Gate
- Data Path Proof
- Security Finding Contract
- Evidence-First Debugging
- Failure-Only Artifact Capture
- E2E Coverage Disclosure
- Safe Code Cleanup
- Commit Planning
- Executable Guardrail Adapter
- Skill Conformance / Dry Run

NEXT:
Merge validated additions into
SAGE v0.8 Execution Protocol & Skill Contract,
then extend conformance tests.
```
