# SAGE — SiSsad Agentic General Engineering
## Engineering Handoff — v0.7 → v0.8

**Status:** Formalized Baseline / Ready for Execution-Layer Design  
**Current Version:** SAGE v0.7  
**Next Version:** SAGE v0.8  
**Next Phase:** Execution Protocol & Skill Contract

---

# 1. Purpose of This Handoff

This document is the formal transfer point from SAGE v0.7 design/formalization to SAGE v0.8 execution-layer design.

The next agent, model, or engineer should not reopen settled decisions without new evidence or a serious architectural reason.

Primary detailed source:

```text
SAGE_v0.7_MASTER_BASELINE.md
```

The full exported conversation/research is historical source material and must not replace the formal baseline.

# 2. Official Name — FROZEN

**SAGE — SiSsad Agentic General Engineering**

**SDAE — Spec-Driven Agentic Engineering** remains the Spec-Driven core inside SAGE.

```text
SAGE
├── Engineering Constitution
├── SDAE Core
├── Software Architecture
├── Quality Engineering
├── Multi-Agent Orchestration
├── Verification & Repair
├── SENS Integration
├── Documentation-by-Design
└── Operations / Evolution
```

# 3. SAGE Mission

SAGE is a general and extensible software-engineering framework for Human, AI Models, AI Agents, Coding Agents, Specialist Agents, Local Models, Engineering Tools, MCP Tools, CI/CD, and Runtime Evidence.

It is intended to remain Provider-Agnostic and Model-Agnostic.

# 4. Fundamental Engineering Principles — FROZEN BASELINE

1. Spec before non-trivial implementation.
2. Proportional Engineering.
3. No ceremony without engineering value.
4. Repository = Source of Truth.
5. Evidence > Agent Opinion.
6. Verification-Driven Completion.
7. Agents reason; Tools execute and verify; Evidence decides.
8. Model ≠ Agent ≠ Skill ≠ Tool.
9. Provider / Model Agnostic by Design.
10. Human Authority.
11. Observable-by-Design / SENS integration boundary.
12. Documented-by-Design.
13. Independent Review when warranted by risk.
14. Fail intelligently, not indefinitely.
15. Minimum sufficient context.

```text
Agent =
Model
+ Role
+ Skills
+ Tools
+ Context
+ Policies
```

# 5. Anti-Overengineering Principle — CRITICAL

> **The lightest process that safely produces sufficient evidence is preferred.**

> **Every artifact must justify its existence.**

Artifacts/processes should provide Risk Reduction, Evidence, Knowledge Preservation, Operational Value, User Value, or Compliance.

A small change must not automatically trigger Full Spec, Full Architecture Review, ADR, Council, multiple agents, full regression, broad documentation, broad telemetry, or Handoff.

# 6. SAGE Engineering Lifecycle

```text
INTAKE → CLASSIFY → DISCOVER → SPEC → DESIGN → PLAN/CONTRACT
→ BUILD → VERIFY → CONVERGE → REVIEW → DOCUMENT → SHIP
→ OBSERVE → LEARN/EVOLVE → SPEC
```

Only necessary stages activate.

# 7. Risk Classification — FROZEN BASELINE

```text
R0 — TRIVIAL
R1 — QUICK
R2 — STANDARD
R3 — HIGH-RISK
R4 — CRITICAL
```

# 8. Dynamic Quality Gate System

Gate domains include Scope/Intent, Specification, Architecture Impact, ADR, Build, Tests, Integration/Contract, Regression, Static Analysis, Software Security, Agent Security, Data/Migration, Performance, Load/Stress/Soak, UX, Accessibility, SENS/Observability, Documentation, Dependency, Licensing, Independent Review, scripts/verify, CI, Rollback/Recovery, and Human Approval.

Activation depends on Risk + Affected Domain + Change Type + Architecture Impact + Quality Attributes.

# 9. Dynamic Definition of Done

```text
DONE =
Acceptance Criteria satisfied
+ Required Quality Gates passed
+ Required Evidence produced
+ No unresolved blocking failure
+ Required project state/docs updated
+ Required approval obtained
```

# 10. Software Architecture Policy

SAGE does not impose a single architecture style. Architecture is selected from requirements, quality attributes, constraints, scale, risk, and expected evolution.

> **Architecture exists to manage complexity and change, not to demonstrate patterns.**

# 11. Architecture Knowledge

Baseline:

```text
ARCHITECTURE.md
ADRs/
CURRENT_STATE.md
```

Lean arc42 is accepted. ADR remains conditional.

# 12. Multi-Agent / Multi-Model Architecture

Core conceptual chain:

```text
HUMAN / PRODUCT OWNER
        ↓
MASTER ENGINEERING CONSTITUTION
        ↓
SAGE
        ↓
ENGINEERING ORCHESTRATOR
        ↓
Workflow / Context / Policy
        ↓
Capability Router
        ↓
Agent Registry / Provider Adapters
        ↓
Role Assignment
        ↓
Skill Router
        ↓
Tool Router
        ↓
Execution
        ↓
Verification
        ↓
Evidence
```

# 13. Engineering Orchestrator

Responsibilities: Understand, Classify, Decompose, Select Workflow, Select Agent, Select Skills, Select Tools, Package Context, Execute, Verify, Review, Integrate, Update State.

# 14. Capability-Based Routing

Routing must not hardcode model roles. It may consider Capability, Task Type, Context Capacity, Tool/Repository Access, Historical Quality, Cost, Latency, Privacy, Availability, and Confidence.

Local Models are first-class participants.

# 15. Engineering Council

Conditional capability for major architecture, uncertainty, security, dependencies, refactors, or competing alternatives.

```text
Independent Proposals
→ Cross Critique
→ Evidence Gathering
→ Revision
→ Decision
→ Minority Report
→ ADR if warranted
```

> **Evidence > Consensus**

# 16. Autonomous Verification & Repair Loop

```text
IMPLEMENT → VERIFY → FAIL → DIAGNOSE → REPAIR → RE-VERIFY
```

Controlled by Attempt, Time, Token/Cost budgets and No-Progress / Repeated-Failure / Same-Fix detection.

# 17. Circuit Breaker / Cross-Agent Diagnosis

On no progress:

```text
Primary Agent
→ Circuit Breaker
→ Independent Agent / Different Model
→ Fresh Root-Cause Analysis
→ Compare Evidence
→ New Repair
→ Verify
```

Then Specialist Agent → Council if justified → Human Escalation.

# 18. Testing Architecture

Risk-based testing may include Unit, Component, Integration, Contract, Regression, Migration, UI, E2E, Architecture, Security, Performance, and Recovery.

Scale-sensitive systems may require Load, Stress, Spike, Soak/Endurance, Scalability, and Recovery tests.

# 19. Security Architecture

Two independent areas:

```text
Software / Application Security
Agentic / Tool Execution Security
```

Policy levels: AUTO, REVIEW, APPROVAL, FORBIDDEN.

# 20. Database / Persistence

Schema is a versioned engineering artifact. Significant changes may require Migration, Compatibility Analysis, Integrity Verification, and Rollback/Roll-forward Strategy. Destructive migrations normally require Human Approval.

# 21. Dependency & Licensing

Significant dependencies may be evaluated for Need, Maintenance, Security, License, Compatibility, Size, Performance, Offline Impact, Vendor Lock-in, and Replacement Cost.

License Governance covers Code, Library, Model, Dataset, Asset, and Plugin.

# 22. Git / Versioning

Baseline: Conventional Commits. Semantic Versioning where a Public Contract exists.

# 23. Documentation-by-Design

Documentation grows with the product. Only documentation relevant to the change should update.

# 24. SENS Integration Boundary

SENS detailed design remains in its separate task/project.

SAGE defines only the **SENS Integration Contract** and **Observable-by-Design** requirement.

Telemetry must remain proportional; low-value log/data explosion is undesirable.

# 25. Context Engineering

Agents should receive minimum sufficient context, not the whole repository/chat history by default.

# 26. Handoff Policy

Handoff exists for genuine transfer of work, not mandatory bureaucracy.

# 27. Skills Layer

**SiSsad Engineering Software Skills** is one component of SAGE.

- Skill = HOW
- Agent = WHO
- Tool = WITH WHAT
- Orchestrator = HOW EVERYTHING IS COORDINATED

# 28. Preliminary Skill Domains

```text
sage-orchestrator
intake-and-risk-router
repository-discovery
feature-spec
bugfix-spec
change-proposal
architecture-design
adr-management
implementation-planning
context-engineering
source-verification
incremental-build
frontend-ui-ux
backend-api
database-migration
test-strategy
structured-debugging
architecture-drift-check
convergence-check
software-security
agent-security
performance-review
dependency-license-audit
code-review
code-simplification
git-versioning
ci-quality-gates
shipping
project-handoff
documentation
sens-integration
```

Names/granularity remain open for v0.8.

# 29. Core vs Conditional vs Extension vs Future

```text
CORE
CONDITIONAL
EXTENSION
FUTURE
```

Risk Classification, Verification, and Repository Source of Truth are CORE.

ADR, Council, and Load Testing are CONDITIONAL.

Advanced Council and specialized Domain Agents may be EXTENSIONS.

Agent Swarms, Reputation Routing, Self-Improving Router, and Continuous AI Watchers remain FUTURE.

# 30. Source / Inspiration Baseline

Sources/frameworks examined include GitHub Spec Kit, Addy Osmani Agent Skills, AGENTS.md, Cursor Rules, GitHub Copilot Instructions, Kiro Specs, OpenSpec, BMAD, arc42, SOLID, Clean Architecture, Hexagonal Architecture, OWASP ASVS, OWASP Agentic Security guidance, OpenTelemetry, Conventional Commits, and Semantic Versioning.

SAGE is not a clone.

Method:

```text
Adopt
Adapt
Reject
Build
```

# 31. Decisions That SHOULD NOT Be Reopened in v0.8 Without Evidence

```text
Name = SAGE
SDAE remains inside SAGE
Provider-Agnostic
Model-Agnostic
Model ≠ Agent ≠ Skill ≠ Tool
Repository = Source of Truth
Evidence > Agent Opinion
Proportional Engineering
No Ceremony Without Value
R0–R4 Risk Model
Dynamic Quality Gates
Dynamic Definition of Done
Verification-Driven Completion
Controlled Autonomous Repair Loop
Circuit Breaker
Independent Review for high-risk changes
Capability-Based Routing
Human Authority
Observable-by-Design / SENS Contract
Documented-by-Design
Architecture Pattern is not predetermined
SENS detailed design remains a separate project
```

Reopen only for New Evidence, Implementation Failure, Contradiction, or Major Architectural Discovery.

# 32. What Is NOT Yet Finalized

```text
Exact Orchestrator interfaces
Machine-readable Constitution format
Exact Risk scoring algorithm
Exact Gate activation algorithm
Skill manifest/schema
Skill granularity
Skill discovery
Skill composition
Agent registry schema
Provider adapter interface
Tool registry schema
Task Packet schema
Handoff schema
Verification result schema
Evidence schema
Workflow DSL/schema
Retry/Circuit-breaker defaults
Context packaging algorithm
Policy engine representation
Repository final directory structure
CI integration details
SENS integration interface
Benchmark/reputation architecture
Council implementation
```

# 33. Immediate Next Phase

# SAGE v0.8 — Execution Protocol & Skill Contract

Transform SAGE from a Formal Engineering Method into an Agent / Orchestrator Executable Engineering Protocol.

# 34. Primary v0.8 Questions

A. How is Task Classification R0–R4 performed?  
B. How are affected domains detected?  
C. How does Risk + Domains + Change Type activate Quality Gates?  
D. How are Skills selected?  
E. How are capability requirements mapped to Agents?  
F. How are Tools/MCPs selected?  
G. How is a Task Packet constructed/executed?  
H. How is Evidence collected/validated?  
I. When does SAGE Retry, Repair, Change Agent, request Cross-model Diagnosis, invoke Council, or escalate to Human?  
J. How does the Orchestrator determine machine-checkable DONE?

# 35. Proposed v0.8 Deliverables

```text
SAGE_EXECUTION_PROTOCOL.md
SAGE_RISK_CLASSIFIER_SPEC.md
SAGE_QUALITY_GATE_ENGINE.md
SAGE_TASK_PACKET_SCHEMA.md
SAGE_SKILL_CONTRACT.md
SAGE_AGENT_CAPABILITY_SCHEMA.md
SAGE_EVIDENCE_SCHEMA.md
SAGE_VERIFICATION_PROTOCOL.md
SAGE_REPAIR_LOOP_PROTOCOL.md
```

Merge artifacts when separation provides no engineering value.

# 36. v0.8 Design Principle

v0.8 must not become merely a collection of fixed prompts.

```text
Intent
→ Classification
→ Policy
→ Workflow
→ Agent / Skill / Tool Selection
→ Execution
→ Evidence
→ Verification
→ Adaptive Repair
→ Completion
```

# 37. Final Handoff Statement

SAGE v0.7 has a formal baseline for Engineering Constitution, Risk Classification, Quality Gates, Definition of Done, Software Architecture Policy, Multi-Agent Architecture, Verification, Repair, Security, Testing, Performance, Documentation, SENS Integration, and Anti-Overengineering.

The next phase must not redesign this architecture from scratch.

**Start directly from:**

# SAGE v0.8 — Execution Protocol & Skill Contract

> **Make SAGE executable by engineering agents and orchestrators without sacrificing proportionality, evidence, provider independence, human authority, or engineering quality.**

# Handoff Status

```text
SAGE v0.7                COMPLETE / BASELINED
Formalization            COMPLETE
Constitution             BASELINED
Risk Model R0–R4         BASELINED
Quality Gate Matrix      BASELINED
Dynamic DoD              BASELINED
SENS Boundary            DEFINED
Documentation Policy     DEFINED
Multi-Agent Direction    DEFINED

NEXT:
SAGE v0.8
Execution Protocol
+
Skill Contract
```
