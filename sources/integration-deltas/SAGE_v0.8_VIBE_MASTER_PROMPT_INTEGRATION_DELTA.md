# SAGE v0.8 — Vibe Master Prompt Integration Delta

**Document Type:** Architecture / Execution Delta  
**Status:** Proposed Integration Input for SAGE v0.8  
**Source Reviewed:** `learn4.html` — “پرامپت طلایی Vibe Coding”  
**Applies With:** `SAGE_v0.7_MASTER_BASELINE.md`, `SAGE_HANDOFF_v0.7_to_v0.8.md`, `SAGE_v0.8_SPEC_KIT_INTEGRATION_DELTA.md`, `SAGE_v0.8_CLAUDE_PROMPT_PACK_INTEGRATION_DELTA.md`

---

# 1. Purpose

این سند `learn4.html` را به‌عنوان یک منبع Prompt/Collaboration با معماری فعلی SAGE مقایسه می‌کند. این منبع یک متد جدید نیست و نباید جای SAGE را بگیرد.

طبقه‌بندی:

```text
ALREADY COVERED
IMPROVE EXISTING
NEW EXECUTION PATTERN
PROVIDER ADAPTER ONLY
REJECT / TOO GENERIC
```

---

# 2. Executive Result

ساختار مرکزی منبع:

```text
ROLE
+ CONTEXT
+ GOAL
+ RULES
```

برای SAGE مفید است، اما نه به‌صورت یک Master Prompt ثابت. SAGE باید آن را به قرارداد اجرایی ساخت‌یافته تبدیل کند:

```text
RUNTIME ENGINEERING BRIEF
=
Role / Capability Requirements
+ Minimum Sufficient Context
+ Goal / Acceptance Contract
+ Policies / Guardrails
+ Risk / Authority
+ Expected Evidence
```

---

# 3. Role

منبع AI را به نقش Senior Software Engineer می‌برد و از آن می‌خواهد تصمیم فنی بد را نقد کند.

**SAGE Status:** `ALREADY COVERED / IMPROVE EXISTING`

SAGE باید به‌جای Persona عمومی، Role/Capability را ساخت‌یافته نگه دارد:

```yaml
role: implementation_engineer
required_capabilities:
  coding: high
  architecture_awareness: medium
  testing: high
  security_awareness: medium
```

**Decision:**  
Generic persona prompt → `REJECT AS CORE`  
Role/Capability Contract → `ADOPT`

---

# 4. Context

منبع پروژه، Stack، فایل‌ها/پوشه‌های مهم، مخاطب و وضعیت فعلی را وارد Context می‌کند.

**SAGE Status:** `ALREADY COVERED / STRONGLY REINFORCE`

Formalize Context Layers:

```text
L0 — Project Identity
L1 — Architecture / Stack
L2 — Current State
L3 — Task-Relevant Files
L4 — Constraints / Policies
L5 — Runtime Evidence (when needed)
```

اصل:

> Minimum sufficient context, not maximum available context.

---

# 5. Goal

منبع Goal و Acceptance Criteria را مشخص می‌کند.

**SAGE Status:** `CORE ALREADY COVERED`

Add compact Goal Contract to Task Packet:

```text
objective
user_value
acceptance_criteria
non_goals
success_metrics (if relevant)
```

R0/R1 may use a shortened form.

---

# 6. Rules

منبع می‌گوید:
- قبل از کد Plan بده
- اگر مبهم بود سؤال بپرس
- فقط فایل‌های مرتبط را تغییر بده
- خروجی runnable بده
- فایل‌های تغییرکرده را گزارش کن
- Self-Review انجام بده

## 6.1 Plan before code

SAGE این را Risk-Adaptive نگه می‌دارد:

```text
R0/R1 → implicit/light plan allowed
R2 → plan required, approval conditional
R3/R4 → explicit plan + review/approval by policy
```

## 6.2 Ask when ambiguous

Already handled by `Clarification Gate`.

## 6.3 Change only relevant files

Add/strengthen **Change Scope Contract**:

```text
allowed_paths
restricted_paths
forbidden_paths
allowed_change_types
```

Material scope expansion triggers reclassification or approval.

## 6.4 Runnable output

Already covered by Verification-Driven Completion.

## 6.5 Changed-files report

Prefer VCS/diff-derived evidence over manual agent claims.

## 6.6 Self-review

SAGE keeps this distinction:

```text
Self Review = first-pass quality check
Independent Review = risk-based second control
Tool Verification = evidence
```

Self-review MUST NOT replace independent review where required.

---

# 7. New Pattern — Runtime Engineering Brief

Proposed provider-neutral runtime object:

```yaml
runtime_engineering_brief:
  task_id: TASK-123

  role:
    type: implementation_engineer
    capabilities:
      coding: high
      testing: high

  context:
    project_summary_ref: PROJECT.md
    architecture_refs:
      - ARCHITECTURE.md
    current_state_ref: CURRENT_STATE.md
    relevant_files:
      - src/auth/login.ts
      - tests/auth/login.spec.ts

  goal:
    objective: "..."
    acceptance_criteria:
      - "..."
    non_goals:
      - "..."

  constraints:
    allowed_paths:
      - src/auth/**
      - tests/auth/**
    forbidden_paths:
      - migrations/**
      - .env

  policy:
    risk_level: R2
    approval_mode: REVIEW
    clarification_required: false

  evidence_required:
    - build
    - targeted_tests
    - changed_files
```

Target layer: `Execution Protocol / Task Packet`.

---

# 8. New Pattern — Instruction Projection

منبع پیشنهاد می‌کند قواعد در Custom Instructions، Project Instructions، Cursor Rules و Copilot Instructions ذخیره شوند.

SAGE باید این را به Architecture تبدیل کند:

```text
Authoritative SAGE Project Rules
        ↓
Projection Generator
        ├── AGENTS.md
        ├── CLAUDE.md
        ├── GEMINI.md
        ├── Cursor Rules
        ├── Copilot Instructions
        └── future provider formats
```

Provider-specific instruction files MUST NOT become independent sources of truth.

Target layer: `Provider Adapter / Repository Bootstrap`.

---

# 9. Feature Slicing

منبع توصیه می‌کند Featureهای بزرگ خرد شوند.

**SAGE Status:** `ALREADY COVERED / REINFORCE`

Formal rule:

> Prefer the smallest independently verifiable slice that preserves architectural coherence.

Target layer: `Task Orchestrator`.

---

# 10. Plan Sanity Check

منبع بر بازبینی Plan قبل از اجرا تأکید دارد.

SAGE نباید Subsystem جدید بسازد. این را در Consistency + Anti-Overengineering ادغام می‌کند:

```text
scope aligned?
architecture aligned?
major unknowns identified?
verification defined?
rollback required?
unnecessary complexity introduced?
```

Target layer: `Consistency Analyzer / Anti-Overengineering`.

---

# 11. What Should NOT Be Added

این موارد نباید Universal SAGE Rules شوند:

- Always wait for approval before any code.
- Always behave as a “Senior Developer”.
- Always use Clean Architecture.
- Self-review alone is sufficient.
- One giant master prompt should be copied everywhere.

---

# 12. Relationship to Existing Deltas

Spec Kit Delta already adds:

```text
Clarification Gate
Cross-Artifact Consistency
Convergence Engine
Anti-Overengineering Check
```

Claude Prompt Pack Delta already adds:

```text
Repository Bootstrap
Current-State → Target-State
Spec Deviation Protocol
UI/UX Design Contract
Build-Stays-Green
Evidence-First Debugging
Executable Guardrails
Skill Conformance
```

This Delta adds/refines:

```text
Runtime Engineering Brief
Context Layering
Goal Contract
Change Scope Contract
Instruction Projection Architecture
Role/Capability Requirement
Plan Sanity Check
Self-Review vs Independent Review separation
Feature Slicing rule
```

---

# 13. Layer Placement

| Pattern | SAGE Layer |
|---|---|
| Runtime Engineering Brief | Execution Protocol |
| Role/Capability Requirement | Agent Router / Capability Schema |
| Context Layers | Context Manager |
| Goal Contract | Task Packet / Spec |
| Change Scope Contract | Policy Engine |
| Instruction Projection | Provider Adapter / Repository Bootstrap |
| Plan Sanity Check | Consistency + Anti-Overengineering |
| Feature Slicing | Task Orchestrator |
| Self-Review | Review Skill |
| Independent Review | Quality Gate / Policy |

---

# 14. Apply to Project

Recommended read order:

```text
1. SAGE_HANDOFF_v0.7_to_v0.8.md
2. SAGE_v0.7_MASTER_BASELINE.md
3. SAGE_v0.8_SPEC_KIT_INTEGRATION_DELTA.md
4. SAGE_v0.8_CLAUDE_PROMPT_PACK_INTEGRATION_DELTA.md
5. SAGE_v0.8_VIBE_MASTER_PROMPT_INTEGRATION_DELTA.md
6. SAGE_v0.8_EXECUTION_PROTOCOL_AND_SKILL_CONTRACT.md
```

Keep original `learn4.html` as a reference source, e.g.:

```text
/sources/reference/learn4.html
```

Do NOT load it into every Agent context.

---

# 15. Instruction to SAGE Project Agent

1. Read the current v0.8 draft first.
2. Mark each recommendation:
   - COVERED
   - PARTIAL
   - MISSING
   - REJECTED
3. Extend existing schemas/contracts instead of creating duplicates.
4. Preserve Provider-Agnostic architecture.
5. Keep provider-specific instruction files as projections.
6. Add conformance tests for machine-executable additions.
7. Run Anti-Overengineering Check before creating new files/skills.
8. Do not reopen frozen v0.7 decisions without evidence.

---

# 16. Final Decision

`learn4.html` is useful as a **prompt-structure and collaboration-pattern reference**, not as a replacement methodology.

Its main architectural contribution is translating:

```text
Role + Context + Goal + Rules
```

into:

```text
Runtime Engineering Brief
+ Context Layers
+ Goal Contract
+ Change Scope Contract
+ Instruction Projection
```

Status:

```text
SOURCE REVIEW              COMPLETE
SAGE COMPARISON            COMPLETE
DUPLICATE CHECK            COMPLETE
ARCHITECTURAL DELTA        PROPOSED

NEXT:
Merge only PARTIAL/MISSING items into
SAGE v0.8 Execution Protocol & Skill Contract
and update conformance tests.
```
