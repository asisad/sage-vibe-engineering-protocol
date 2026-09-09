# SAGE — SiSsad Agentic General Engineering
## Master Baseline v0.7

**Status:** Formalized Baseline  
**Version:** 0.7  
**Scope:** Master Engineering Constitution, Risk Classifier R0–R4, Quality Gate Matrix, Dynamic Definition of Done, Execution Model

This document is the authoritative SAGE v0.7 baseline.

---

# 1. Purpose and Scope

SAGE is a general framework for software engineering through collaboration between humans, AI agents, and engineering tools.

SAGE MUST remain provider-, model-, language-, framework-, and platform-agnostic; scale from small projects to large systems; support traditional, AI-native, agentic, and multi-agent software; cover the lifecycle `Intent → Spec → Architecture → Build → Verify → Ship → Operate → Learn`; and improve engineering quality without making the process itself a source of unnecessary time, token, or cost overhead.

> **Engineering rigor SHALL be proportional to risk, complexity and impact.**

# 2. SAGE Hierarchy

```text
SAGE
│
├── Master Engineering Constitution
├── SDAE Core — Spec-Driven Agentic Engineering
├── Risk & Complexity System
├── Software Architecture System
├── Quality Engineering System
├── Verification System
├── Documentation System
├── SENS Integration Contract
├── Engineering Orchestrator
│   ├── Workflow Engine
│   ├── Context Manager
│   ├── Policy Engine
│   ├── Task Orchestrator
│   └── Verification Engine
├── Agent / Model Fabric
│   ├── Agent Registry
│   ├── Capability Router
│   └── Provider Adapters
├── Skill System
├── Tool / MCP System
└── Repository Knowledge & Evidence
```

SDAE remains inside SAGE and is responsible for the Spec-Driven part of the engineering process.

# 3. Normative Language

- **MUST** — mandatory.
- **SHOULD** — strong default; deviation requires a reason.
- **MAY** — optional/project-dependent.
- **MUST NOT** — prohibited.

# 4. Proportional Engineering

Every task MUST be classified by Risk, Complexity, and Impact before workflow selection.

SAGE MUST NOT automatically require Full Spec, ADR, Engineering Council, Full Repository Analysis, Full Regression Suite, multiple Reviewers, Handoff, broad Documentation updates, or broad Telemetry generation for a small change.

> **No ceremony without engineering value.**

An artifact or engineering activity should provide at least one of: Risk Reduction, Evidence, Knowledge Preservation, Operational Value, User Value, or Compliance. Otherwise it SHOULD NOT be generated.

# 5. Repository as Source of Truth

Persistent project knowledge MUST live in the Repository or Project Knowledge Store. Agent memory or chat history MUST NOT be the sole location for critical project knowledge.

Possible authoritative artifacts include PRODUCT, ARCHITECTURE, CURRENT_STATE, SPEC, ADR, TASK, TEST, REVIEW, HANDOFF, and DOCUMENTATION. Only justified artifacts should exist.

# 6. Specification

For every non-trivial change, What, Why, Expected behavior, Constraints, and Acceptance criteria must be sufficiently clear. A Spec must be precise enough for verification and MUST NOT exist merely to increase documentation volume.

# 7. Software Architecture

SAGE does not mandate a single architecture style. Clean, Hexagonal, Layered, Modular Monolith, Event-Driven, Microservices, and other patterns are tools.

Architecture should derive from Requirements, Quality Attributes, Constraints, Scale, Risk, and Expected Evolution.

Serious systems SHOULD have explicit module boundaries. Agents MUST NOT create unnecessary abstractions merely to satisfy a pattern.

> **Architecture exists to manage complexity and change, not to demonstrate patterns.**

# 8. Architecture Decisions

Important, risky, expensive, controversial, or difficult-to-reverse decisions SHOULD be recorded in ADRs containing at least Context, Decision, Alternatives, Consequences, and Evidence/Rationale. Small decisions MUST NOT become ADRs merely for process compliance.

# 9. Quality Attributes

Non-trivial projects MUST identify important quality attributes such as Security, Reliability, Performance, Maintainability, Usability, Accessibility, Privacy, Scalability, Extensibility, Portability, Interoperability, and Offline Capability. Important attributes SHOULD have measurable criteria.

# 10. Model / Agent / Skill / Tool Separation

```text
MODEL ≠ AGENT ≠ SKILL ≠ TOOL

Agent =
Model
+ Role
+ Skills
+ Tools
+ Context
+ Policies
```

Core workflows MUST NOT depend on a provider name unless a provider-specific capability is actually required.

# 11. Capability-Based Routing

Agents should be selected according to task needs. Routing MAY consider Capability, Task Type, Context Capacity, Tool Access, Repository Access, Quality History, Cost, Latency, Privacy, Availability, and Confidence. Local models must be able to participate as first-class agents.

# 12. Context Minimality

Each agent SHOULD receive only the context necessary for its task.

A Task Packet may contain Objective, Relevant Context, Constraints, Acceptance Criteria, Allowed Changes, Forbidden Changes, Relevant Architecture, and Expected Evidence.

> **Minimum sufficient context, not maximum available context.**

# 13. Implementation

Implementation must conform to the Spec, respect the Architecture Contract, avoid unrelated changes, and avoid unjustified scope expansion. An agent MUST NOT replace frameworks/databases, break public contracts, add major dependencies, or redesign architecture for a small task without justification.

# 14. Verification-Driven Completion

> **Agent declaration is not evidence of completion.**

```text
Implementation
      ↓
Verification
      ↓
Evidence
      ↓
Review when required
      ↓
PASS
```

> **Agents reason. Tools execute and verify. Evidence decides.**

# 15. Autonomous Verify–Diagnose–Repair

```text
BUILD
 ↓
VERIFY
 ↓
FAIL
 ↓
DIAGNOSE
 ↓
REPAIR
 ↓
RE-VERIFY
```

The loop MUST be controlled and may enforce Attempt Budget, Time Budget, Token/Cost Budget, Repeated Failure Detection, No-Progress Detection, and Same-Fix Detection.

# 16. Circuit Breaker & Independent Diagnosis

An agent MUST NOT repeat substantially the same failed approach indefinitely. On no progress, trigger a Circuit Breaker and independent Agent/Model diagnosis. Continued failure may escalate to a Specialist Agent, Engineering Council, or Human.

# 17. Independent Review

For high-risk changes, the implementer SHOULD NOT be the only reviewer of its own work. Cross-model review MAY be used, but multiple model opinions do not themselves constitute evidence.

# 18. Testing

Testing must be risk-based and may include Unit, Component, Integration, Contract, Regression, Migration, UI, E2E, Architecture, Security, Performance, and Recovery tests. Bug fixes SHOULD have regression evidence where practical. All test types MUST NOT run for every change.

# 19. Scale & Performance Verification

When performance or scale is a requirement, it must be measurable. Verification may include Load, Stress, Spike, Soak/Endurance, Scalability, and Recovery testing.

Example: `2,000 concurrent users`, `p95 latency ≤ target`, `error rate ≤ target`.

Optimization SHOULD be measurement-driven.

# 20. Security

SAGE separates Software/Application Security from Agentic/Tool Execution Security.

Policy levels:

```text
AUTO
REVIEW
APPROVAL
FORBIDDEN
```

Secrets, credentials, and sensitive information MUST NOT be unnecessarily exposed through context or telemetry.

# 21. Data & Database

Mutable schema should be treated as versioned engineering material. Significant data changes SHOULD include Migration, Compatibility Analysis, Integrity Verification, and Rollback or Roll-forward Strategy. Destructive migrations SHOULD require Human Approval.

# 22. Dependency Governance

Significant dependencies SHOULD be evaluated for Need, Maintenance, Security, License, Compatibility, Performance, Size, Vendor Lock-in, Replacement Cost, and Offline Impact. Adding a dependency MUST NOT be the default solution to every problem.

# 23. Licensing

SAGE must be capable of governing licensing for Source Code, Libraries, Models, Datasets, Assets, and Plugins. An incompatible license MUST NOT be accepted merely for agent convenience.

# 24. Git & Versioning

Changes should remain traceable. Conventional Commits SHOULD be the default baseline. Semantic Versioning SHOULD be used where a component or product exposes a Public Contract. Git history should preserve useful engineering history, not automatically dump agent conversations.

# 25. CI/CD & Quality Gates

Where practical, verification should expose a standard entry point such as `scripts/verify` or a platform-native equivalent. It may include Build, Tests, Lint, Type Check, Security, Architecture, Dependency, License, and Performance. Only relevant gates activate.

# 26. Observable-by-Design / SENS Contract

SAGE must account for evidence/telemetry required by SENS from the architecture stage. SAGE does not define the SENS dashboard or SEOv here.

Relevant projects should be able to provide Events, Logs, Metrics, Traces, Errors, Runtime Context, Performance Signals, and Agent/Tool Execution Signals.

Telemetry MUST NOT be collected without engineering purpose.

> **Observe what has engineering or operational value.**

# 27. Documented-by-Design

Documentation is part of the engineering lifecycle and may include Developer Docs, User Guide, Installation, Configuration, Administrator/Operator Guide, API Docs, Troubleshooting, Architecture Docs, In-App Help, and Release Notes.

Features SHOULD update relevant documentation. Small changes MUST NOT trigger needless rewriting of all documentation.

# 28. Engineering Council

The Council is conditional, not mandatory. It MAY activate for major architecture decisions, high uncertainty, security, important technology selection, major refactors, or competing viable alternatives.

```text
Independent Proposal
→ Cross Critique
→ Evidence
→ Revision
→ Decision
→ Minority Report
→ ADR if warranted
```

> **Consensus cannot override evidence.**

# 29. Human Authority

Baseline autonomy levels are AUTO, REVIEW, and APPROVAL. Higher risk should reduce autonomy. Humans must retain the ability to Approve, Reject, Override, Pause, and Change Constraints.

# 30. Knowledge Preservation & Handoff

A Handoff should only be produced when another agent or human actually needs it to continue the work. R0/R1 should not produce standalone Handoffs by default.

# 31. Learning & Evolution

```text
SHIP
 ↓
OPERATE
 ↓
OBSERVE
 ↓
LEARN
 ↓
IMPROVE
 ↓
SPEC
```

Production evidence MAY trigger bug fixes, architecture changes, performance optimization, security improvements, or Spec evolution.

# 32. Anti-Overengineering Constitution

SAGE MUST NOT become a source of unnecessary complexity. Automation SHOULD reduce repetitive work. Duplicate authoritative artifacts SHOULD be consolidated when duplication adds no independent value.

> **The lightest process that safely produces sufficient evidence is preferred.**

# 33. Risk Classifier v0.7

| Level | Meaning |
|---|---|
| **R0 — Trivial** | Very small change with negligible risk |
| **R1 — Quick** | Limited, reversible change |
| **R2 — Standard** | Normal feature/bug with meaningful impact |
| **R3 — High Risk** | Important architecture/data/security/API/integration change |
| **R4 — Critical** | Destructive, production-critical, safety/privacy/security-critical, or very difficult-to-reverse change |

Classification is not based on lines of code alone.

# 34. Quality Gate Matrix v0.7

Legend: **—** Not required · **A** Automatic/lightweight · **R** Required · **IR** Independent Review · **HA** Human Approval · **\*** only when relevant to affected domain.

| Gate | R0 | R1 | R2 | R3 | R4 |
|---|:---:|:---:|:---:|:---:|:---:|
| Scope/Intent | A | A | R | R | R |
| Spec | — | A | R | R | R |
| Architecture Impact | — | A | A/R | R | R |
| ADR | — | — | Conditional | R* | R* |
| Build | A | R | R | R | R |
| Targeted Tests | A | R | R | R | R |
| Integration/Contract | — | A | R* | R | R |
| Regression | — | R* | R* | R | R |
| Static Analysis | — | A | R | R | R |
| Security | — | A* | R* | R | R+IR |
| Data/Migration | — | — | R* | R | R+HA* |
| Performance | — | — | A* | R* | R* |
| Load/Stress/Soak | — | — | —* | R* | R* |
| UX/Accessibility | — | A* | R* | R* | R* |
| SENS/Observability | — | A* | R* | R | R |
| Documentation | — | A* | R* | R | R |
| Dependency/License | — | A* | R* | R | R |
| Independent Review | — | — | A | IR | IR |
| `scripts/verify` | A | R | R | R | R |
| CI | — | A | R | R | R |
| Rollback/Recovery | — | — | A* | R | R |
| Human Approval | — | — | —* | Conditional | HA |

# 35. Dynamic Definition of Done v0.7

```text
DONE =
Required Acceptance Criteria satisfied
+
Required Quality Gates passed
+
Required Evidence produced
+
No unresolved blocking failure
+
Required documentation/state updated
+
Required approval obtained
```

R0: Change correct + targeted verification.

R2: Acceptance + implementation + tests + relevant quality gates + review + relevant docs + CI PASS.

R4: Acceptance + full relevant verification + independent review + applicable security/data/performance gates + recovery evidence + SENS evidence + documentation + CI PASS + human approval.

# 36. Execution Model

```text
USER INTENT
    ↓
CLASSIFY R0–R4
    ↓
IDENTIFY AFFECTED DOMAINS
    ↓
SELECT MINIMUM REQUIRED WORKFLOW
    ↓
PACKAGE CONTEXT
    ↓
SELECT AGENT + SKILLS + TOOLS
    ↓
EXECUTE
    ↓
VERIFY
    ↓
FAIL?
 ┌──┴──┐
YES    NO
 ↓      ↓
REPAIR  QUALITY GATES
 ↓      ↓
LOOP    REVIEW
 ↓      ↓
STALL?  DONE?
 ↓
SECOND AGENT
 ↓
ESCALATE IF NECESSARY
```

# 37. Baseline Status

SAGE v0.7 establishes the formal baseline for the Master Engineering Constitution, Risk Classification R0–R4, Quality Gate Matrix, Dynamic Definition of Done, Software Architecture Policy, Multi-Agent Direction, Verification & Repair, SENS Integration Contract, Documentation-by-Design, Proportional Engineering, and Anti-Overengineering.

Next phase:

# SAGE v0.8 — Execution Protocol & Skill Contract

Purpose: make these rules machine/agent-executable by defining how an Orchestrator classifies tasks, activates relevant gates, selects skills/agents/tools, collects evidence, controls repair loops, and determines completion.
