# SAGE v0.8 — Spec Kit Integration Delta

**Document Type:** Architecture / Execution Delta  
**Status:** Proposed for SAGE v0.8 Integration  
**Applies After:** `SAGE_v0.7_MASTER_BASELINE.md`  
**Handoff Context:** `SAGE_HANDOFF_v0.7_to_v0.8.md`

---

# 1. Purpose

This document records the SAGE v0.8 changes derived from reviewing the current GitHub Spec Kit workflow.

It is intentionally a **Delta**, not a replacement for the SAGE v0.7 baseline.

The following documents remain authoritative:

```text
SAGE_v0.7_MASTER_BASELINE.md
SAGE_HANDOFF_v0.7_to_v0.8.md
```

This Delta adds execution-layer capabilities while preserving all previously frozen SAGE decisions.

# 2. Integration Principle

GitHub Spec Kit is treated as an external reference implementation and source of useful workflow concepts.

SAGE does **not** become dependent on Spec Kit.

Integration follows the SAGE source-adoption policy:

```text
Adopt
Adapt
Reject
Build
```

# 3. New v0.8 Capabilities

Four capabilities are added or formalized:

```text
1. Clarification Gate
2. Cross-Artifact Consistency Analysis
3. Convergence Engine
4. Anti-Overengineering Check
```

These are part of SAGE v0.8 Execution Protocol design.

# 4. Clarification Gate

## Purpose
Prevent implementation from starting while material ambiguity still exists in a non-trivial task.

## Placement

```text
INTAKE
  ↓
CLASSIFY
  ↓
DISCOVER
  ↓
SPEC
  ↓
CLARIFICATION GATE
  ↓
DESIGN / PLAN
```

For R2–R4 tasks, SAGE SHOULD detect material ambiguity before planning or implementation. For R0–R1 tasks, clarification SHOULD remain lightweight and MAY be implicit.

Checks may include ambiguous requirements, missing acceptance criteria, conflicting constraints, undefined terminology, unclear actor/user, unclear success/failure behavior, unclear scope, or unclear destructive impact.

Output:

```text
CLEAR
or
CLARIFICATION_REQUIRED
```

The Clarification Gate MUST NOT create unnecessary question loops for trivial changes.

# 5. Cross-Artifact Consistency Analysis

## Purpose
Detect contradictions, omissions, drift, and orphan requirements between engineering artifacts before implementation or release.

## Placement

```text
SPEC
  ↕
ARCHITECTURE
  ↕
ADR
  ↕
PLAN
  ↕
TASKS
  ↕
TESTS
  ↕
DOCUMENTATION
```

New component:

```text
Artifact Consistency Analyzer
```

Possible inputs:

```text
PRODUCT.md
SPEC
ARCHITECTURE.md
Relevant ADRs
Plan
Tasks
Acceptance Criteria
Tests
Documentation
Current State
```

Checks may include:
- Requirement with no implementation task
- Requirement with no acceptance evidence
- Task with no parent requirement
- Architecture decision contradicted by plan
- ADR contradicted by implementation plan
- Test missing for critical acceptance criterion
- Documentation describing obsolete behavior
- Task outside approved scope

Output:

```text
CONSISTENT
or
INCONSISTENCIES[]
```

Activation:

```text
R0 → OFF
R1 → optional/lightweight
R2 → recommended
R3 → required
R4 → required
```

# 6. Convergence Engine

## Purpose
Ensure implementation actually converges toward the approved Spec, Architecture, Acceptance Criteria, and active Quality Gates.

## Placement

```text
BUILD
  ↓
VERIFY
  ↓
CONVERGENCE ENGINE
  ↓
REVIEW
```

Core loop:

```text
Implementation
      ↓
Evidence Collection
      ↓
Compare Against:
- Spec
- Acceptance Criteria
- Architecture Contract
- Required Quality Gates
      ↓
Gap?
 ┌────┴────┐
YES        NO
 ↓          ↓
Repair    CONVERGED
 ↓
Re-Verify
 ↺
```

Output:

```text
CONVERGED
PARTIALLY_CONVERGED
NOT_CONVERGED
```

Possible gap records:
- missing_requirement
- architecture_drift
- untested_acceptance_criterion
- incomplete_documentation
- unresolved_failure
- scope_deviation

# 7. Convergence + Repair Integration

The Convergence Engine integrates with the existing SAGE Autonomous Verify–Diagnose–Repair Loop.

```text
CONVERGENCE GAP
      ↓
DIAGNOSE
      ↓
REPAIR
      ↓
VERIFY
      ↓
RE-CHECK CONVERGENCE
```

The loop remains protected by Attempt Budget, Time Budget, Token/Cost Budget, No-Progress Detection, Repeated-Failure Detection, and Same-Fix Detection.

If stalled:

```text
Circuit Breaker
      ↓
Independent Agent / Different Model
      ↓
Fresh Diagnosis
      ↓
Evidence Comparison
```

Then, if needed:

```text
Specialist Agent
→ Engineering Council
→ Human Escalation
```

# 8. Anti-Overengineering Check

## Purpose
Ensure SAGE itself does not produce unnecessary architecture, artifacts, tests, reviews, or process overhead.

## Placement

```text
CLASSIFY
  ↓
PROPOSE WORKFLOW
  ↓
ANTI-OVERENGINEERING CHECK
  ↓
MINIMUM SUFFICIENT WORKFLOW
```

Questions include:
- Is every planned artifact necessary?
- Is every planned review necessary?
- Is every planned test relevant?
- Is an ADR really needed?
- Is Council really needed?
- Is this abstraction justified?
- Is this dependency justified?
- Is full-repository context necessary?
- Is the proposed telemetry valuable?
- Is the documentation update relevant?
- Can the same evidence be obtained more cheaply?

Output:

```text
ACCEPT_WORKFLOW
or
SIMPLIFY_WORKFLOW
```

> **The lightest process that safely produces sufficient evidence is preferred.**

# 9. Revised SAGE v0.8 Execution Flow

```text
USER INTENT
    ↓
CLASSIFY R0–R4
    ↓
DISCOVER
    ↓
SPEC
    ↓
CLARIFICATION GATE
    ↓
IDENTIFY AFFECTED DOMAINS
    ↓
SELECT QUALITY GATES
    ↓
PROPOSE WORKFLOW
    ↓
ANTI-OVERENGINEERING CHECK
    ↓
PLAN / TASKS
    ↓
CROSS-ARTIFACT CONSISTENCY CHECK
    ↓
PACKAGE MINIMUM SUFFICIENT CONTEXT
    ↓
SELECT AGENT + SKILLS + TOOLS
    ↓
EXECUTE
    ↓
VERIFY
    ↓
CONVERGENCE CHECK
    ↓
FAIL / GAP?
 ┌──────┴──────┐
YES            NO
 ↓              ↓
DIAGNOSE       REVIEW
 ↓              ↓
REPAIR         DONE CHECK
 ↓
RE-VERIFY
 ↓
CONVERGENCE
 ↺
```

# 10. New / Updated v0.8 Components

```text
Task Classifier
Domain Detector
Clarification Gate
Quality Gate Engine
Workflow Selector
Anti-Overengineering Check
Task Planner
Artifact Consistency Analyzer
Context Packager
Capability Router
Agent Router
Skill Router
Tool Router
Verification Engine
Convergence Engine
Repair Loop Controller
Circuit Breaker
Evidence Collector
Completion Evaluator
```

# 11. Relationship to Existing SAGE v0.7 Components

## No Replacement

The following remain unchanged in principle:

```text
SAGE name
SDAE inside SAGE
R0–R4 Risk Model
Provider-Agnostic design
Model-Agnostic design
Model ≠ Agent ≠ Skill ≠ Tool
Repository = Source of Truth
Dynamic Quality Gates
Dynamic Definition of Done
Human Authority
Capability-Based Routing
Independent Review for high-risk tasks
Controlled Repair Loop
Circuit Breaker
SENS Integration Boundary
Documented-by-Design
Proportional Engineering
```

## Extended

```text
DISCOVERY / SPEC
→ adds Clarification Gate

VERIFICATION
→ adds Artifact Consistency Analysis

VERIFY / REPAIR
→ formalizes Convergence Engine

RISK / WORKFLOW SELECTION
→ adds Anti-Overengineering Check
```

# 12. Relationship to GitHub Spec Kit

```text
Spec Kit ≠ SAGE
```

Spec Kit is primarily a Spec-Driven Development toolkit.

SAGE additionally includes Risk Classification, Software Architecture Governance, Quality Engineering, Multi-Agent / Multi-Model Orchestration, Capability Routing, Agent / Skill / Tool separation, Security, Database/Migration Governance, Performance/Load Testing, Documentation-by-Design, SENS Integration, Autonomous Repair, Circuit Breaking, Human Authority, and Provider Independence.

Spec Kit should be treated as:

```text
Reference implementation
+
Workflow inspiration
+
Potential reusable component source
```

# 13. Apply to Project

An Agent/Codex session continuing SAGE development should read these files in this order:

```text
1. SAGE_HANDOFF_v0.7_to_v0.8.md
2. SAGE_v0.7_MASTER_BASELINE.md
3. SAGE_v0.8_SPEC_KIT_INTEGRATION_DELTA.md
```

Interpretation:

```text
HANDOFF
→ tells the agent where the project currently stands.

MASTER BASELINE
→ contains frozen SAGE v0.7 architecture and rules.

THIS DELTA
→ adds the approved Spec Kit-derived changes for v0.8.
```

The Agent MUST NOT interpret this Delta as permission to redesign frozen SAGE decisions from scratch.

# 14. v0.8 Formalization Impact

Possible artifacts now include:

```text
SAGE_EXECUTION_PROTOCOL.md
SAGE_RISK_CLASSIFIER_SPEC.md
SAGE_QUALITY_GATE_ENGINE.md
SAGE_CLARIFICATION_PROTOCOL.md
SAGE_CONSISTENCY_ANALYZER.md
SAGE_CONVERGENCE_ENGINE.md
SAGE_TASK_PACKET_SCHEMA.md
SAGE_SKILL_CONTRACT.md
SAGE_AGENT_CAPABILITY_SCHEMA.md
SAGE_EVIDENCE_SCHEMA.md
SAGE_VERIFICATION_PROTOCOL.md
SAGE_REPAIR_LOOP_PROTOCOL.md
```

This list is not mandatory. Following Proportional Engineering, related documents SHOULD be merged when separation provides no engineering value.

# 15. Decision Status

```text
Clarification Gate
→ ADOPT / ADAPT INTO SAGE v0.8

Cross-Artifact Consistency Analysis
→ ADOPT / EXPAND INTO SAGE v0.8

Convergence Engine
→ FORMALIZE AS CORE EXECUTION CAPABILITY

Anti-Overengineering Check
→ FORMALIZE EXISTING SAGE PRINCIPLE AS EXECUTION GATE
```

# 16. Next Action

Continue directly with:

# SAGE v0.8 — Execution Protocol & Skill Contract

The next design step should define machine/agent-executable behavior for Classification, Clarification, Domain Detection, Gate Activation, Workflow Selection, Anti-Overengineering, Task Planning, Consistency Analysis, Context Packaging, Agent/Skill/Tool Routing, Execution, Evidence, Verification, Convergence, Repair, Escalation, and Completion.

Do not reopen frozen SAGE v0.7 decisions without new evidence.
