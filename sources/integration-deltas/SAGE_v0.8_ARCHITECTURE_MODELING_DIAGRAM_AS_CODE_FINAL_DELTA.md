# SAGE v0.8 — Architecture Modeling & Diagram-as-Code Final Integration Delta

**Document Type:** Final Architecture Integration Delta  
**Status:** READY FOR SAGE ARCHITECTURE REVIEW  
**Target:** SAGE v0.8+  
**Scope:** Architecture modeling, diagram-as-code, architecture policy, fitness functions, rendering/layout, reverse architecture discovery, SENS/UEG planned-vs-observed validation  
**Decision:** GO — integrate into SAGE Architecture as a first-class capability.

---

# 1. Purpose

This document finalizes the Architecture Modeling / Diagram-as-Code capability for SAGE.

The goal is not merely to generate diagrams. The goal is to make architecture:

```text
Modelable
Queryable
Reviewable
Testable
Versionable
Render-independent
Agent-accessible
Runtime-verifiable
```

Core principle:

```text
Architecture Model = Source of Truth
Diagrams = Views / Projections
Rendered Images = Presentation Artifacts
Runtime Graph = Observed Reality
```

SAGE owns approved/planned architecture. SENS/UEG observes runtime architecture and compares it against the approved model.

---

# 2. Final Architecture

```text
                         SAGE
                          │
                 Architecture Core
                          │
                 Architecture Model API
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
           LikeC4                Structurizr
          Default                 Alternative
              │
              ▼
        Canonical Model
              │
       ┌──────┼───────────────┐
       ▼      ▼               ▼
    Views   Query/MCP     Architecture Policy
                               │
                               ▼
                        Fitness Functions
                               │
                               ▼
                             CI Gate
              │
              ▼
        Renderer Router
              │
   ┌──────────┼────────┬────────┬───────────┐
   ▼          ▼        ▼        ▼           ▼
  D2       Mermaid  PlantUML  Graphviz    Kroki
                                      (optional gateway)
              │
              ▼
         Layout Engine
         ├─ ELK        ← preferred for complex graphs
         ├─ Graphviz
         └─ Dagre
              │
              ▼
     Human Architecture Review
              │
              ▼
        Implementation
              │
              ▼
      SENS / UEG Runtime Graph
              │
              ▼
       Planned ↔ Observed
```

---

# 3. Reverse Architecture Discovery Path

```text
Code / IaC / Runtime
       ↓
Reverse Architecture Discovery
       ↓
Inferred Model
       ↓
Compare with Approved Model
       ↓
Drift / Proposal
```

Important:

```text
Inferred Model ≠ Approved Model
Observed Runtime ≠ Approved Model
```

Neither code inference nor runtime observation may silently overwrite approved architecture.

Allowed flow:

```text
Inferred / Observed
       ↓
Compare
       ↓
Evidence
       ↓
Proposed Architecture Change
       ↓
Review / Approval
       ↓
Approved Model Update
```

---

# 4. Core Decisions

## 4.1 LikeC4

Status:

```text
KEEP / DEFAULT
```

LikeC4 is the baseline Architecture Model Adapter.

Role:

```text
Architecture-as-Code
Canonical model
Multiple views
Architecture queries
Agent/MCP access
CI validation
```

LikeC4 is not hard-coded into SAGE Core.

```text
SAGE Architecture Model API
        ↓
LikeC4 Adapter
```

This preserves replaceability and provider/tool independence.

## 4.2 Structurizr

Status:

```text
UPGRADE
→ First-class Alternative Adapter
```

Structurizr is an accepted alternative model provider, especially when a project already uses Structurizr or strict C4 modeling is preferred.

Rule:

```text
One project SHOULD have one authoritative architecture model.
```

Do not maintain LikeC4 and Structurizr as competing canonical models.

---

# 5. Architecture Model API

SAGE Core should expose a provider-neutral architecture contract.

Conceptual capabilities:

```text
create_element
update_element
remove_element
create_relationship
update_relationship
remove_relationship
query_dependencies
query_dependents
query_boundary
query_ownership
query_blast_radius
validate_model
generate_view
compare_model
export_model
```

Potential entities:

```text
System
Service
Component
Module
Database
Queue
External System
Deployment Node
Agent
Model
Skill
Tool
MCP Endpoint
Trust Boundary
Data Boundary
Team / Owner
Configuration Item
```

---

# 6. Stable Architecture Identity

Every architecture element intended to connect with SENS/UEG/CMDB should have a stable identity.

Example:

```text
architecture_id: service.payment-api
```

The same identity SHOULD be reused where practical across:

```text
Architecture Model
Source Code Mapping
CMDB
SENS
UEG
Telemetry Resources
ADRs
Dependencies
Security Findings
Impact Analysis
```

This is required for reliable Planned ↔ Observed comparison.

---

# 7. Architecture Policy-as-Code

Status:

```text
NEW
```

Architecture must not be validated only by humans looking at diagrams.

SAGE should support machine-checkable architecture rules.

Examples:

```text
Frontend MUST NOT access Production Database directly.
Domain Layer MUST NOT depend on UI Layer.
Public API MUST pass through Authorization Boundary.
Payment Service MUST NOT depend on Presentation Layer.
Privileged Agent MUST NOT invoke Restricted MCP Tool without Policy Approval.
Production secrets MUST NOT cross an untrusted boundary.
```

These rules operate on the architecture model and/or code dependency graph.

---

# 8. Architecture Fitness Functions

Status:

```text
NEW
```

Architecture Fitness Functions continuously verify important architectural properties.

Possible implementations depend on project technology:

```text
Java  → ArchUnit
.NET   → NetArchTest
Go     → arch-go
Generic / policy → OPA / custom rules
Runtime → SENS / UEG relationship validation
```

Conceptual flow:

```text
Architecture Policy
       ↓
Fitness Function
       ↓
Automated Verification
       ↓
CI Gate
```

Examples:

```text
No forbidden dependency
No circular architecture dependency
No boundary violation
No direct DB access from prohibited layer
No unauthorized service-to-service edge
No undeclared external dependency
```

Fitness Functions activate proportionally according to Risk and Architecture Impact.

---

# 9. Architecture CI Gate

For architecture-sensitive changes, CI may verify:

```text
Model parses successfully
Model references resolve
Stable IDs remain valid
Required views render
Forbidden relationships do not exist
Architecture fitness functions pass
No unexpected architecture-policy violation
Generated artifacts match current model
```

Possible output:

```text
PASS
FAIL
REVIEW_REQUIRED
```

R0/R1 work should not trigger heavyweight architecture validation unless architecture files or relationships are affected.

---

# 10. Views

Views are projections of the canonical model.

Potential view types:

```text
System Context
System Landscape
Container / Service
Component
Dependency
Sequence
Dynamic
State
Data / ER
Data Flow
Workflow
Deployment
Infrastructure
Security / Trust Boundary
Agent / Model / Skill / Tool Flow
MCP Flow
CI/CD
CMDB Dependency
Blast Radius / Impact
Architecture Drift
```

Rule:

```text
Do NOT generate every diagram type mechanically.
```

SAGE should select only views that help answer the engineering question.

---

# 11. Diagram Selection Policy

Diagram selection should be based on:

```text
Risk
Task Type
Architecture Impact
Data Impact
Security Impact
Runtime Complexity
Human Review Need
```

Examples:

```text
Public API Change
→ Component + Sequence + Trust Boundary

Database Change
→ ER/Data + Dependency

Stateful Workflow
→ State + Sequence

Deployment Change
→ Deployment + Dependency

Agentic Workflow
→ Agent/Tool Flow + Sequence + Trust Boundary

R0/R1 Isolated Edit
→ No architecture diagram by default
```

---

# 12. Renderer Router

The architecture model and renderer layer MUST remain separate.

```text
Canonical Model
       ↓
Renderer Router
```

Current renderer policy:

```text
D2       → preferred polished/static renderer
Mermaid  → lightweight documentation renderer
PlantUML → optional specialist renderer
Graphviz → graph/dependency renderer
Kroki    → optional rendering gateway
```

No renderer becomes the architecture source of truth.

---

# 13. D2

Status:

```text
KEEP
```

Primary purpose:

```text
Polished static diagrams
SVG / PNG / PDF style output
Presentation-quality engineering views
```

D2 is a renderer / diagram language, not the canonical architecture model.

---

# 14. Mermaid

Status:

```text
KEEP
```

Primary purpose:

```text
Markdown
README
ADR
PR
Plan
Lightweight architecture communication
```

Prefer generating Mermaid from the approved model where possible instead of manually maintaining unrelated duplicate diagrams.

---

# 15. PlantUML

Status:

```text
CORRECT / OPTIONAL
```

PlantUML remains useful for:

```text
Sequence
State
Class
Component
Deployment
UML-heavy projects
```

Licensing should not be treated as a simple universal blocker. The exact distribution/license variant used in a project must be checked during dependency/license governance.

PlantUML MUST remain optional and outside SAGE Core.

---

# 16. Graphviz

Status:

```text
KEEP AS SPECIALIZED RENDERER / LAYOUT TOOL
```

Best suited for:

```text
Dependency graphs
Directed graphs
Algorithmic layouts
Large relationship maps
```

Graphviz is not the architecture source of truth.

---

# 17. Kroki

Status:

```text
CORRECT / OPTIONAL GATEWAY
```

Kroki should be treated as an optional multi-format rendering gateway.

```text
Renderer Request
      ↓
Kroki Adapter
      ↓
D2 / Mermaid / PlantUML / Graphviz / other formats
```

It MUST NOT be required by SAGE Core. Security, deployment model, network exposure, and exact licenses of bundled renderers must be reviewed before production use.

---

# 18. Layout Engine Abstraction

Status:

```text
REFINE
```

Layout is separate from modeling and rendering.

SAGE should expose:

```text
LayoutEngine
```

Initial choices:

```text
ELK      → preferred for large/complex/nested graphs
Graphviz → general-purpose graph layout
Dagre    → lightweight/simple hierarchical layouts
```

The architecture must allow additional engines later without redesigning SAGE.

---

# 19. Query / MCP Architecture

Agents should query the architecture model rather than infer everything from screenshots or raw files.

```text
Agent
 ↓
Architecture Query Interface
 ↓
MCP / Adapter
 ↓
Canonical Model
```

Examples:

```text
What depends on this service?
What database does this component use?
What are the external dependencies?
What is the blast radius of this change?
Does this dependency violate architecture policy?
Which trust boundary does this data cross?
```

Architecture query access should be read-only by default unless modification authority is explicitly granted.

---

# 20. Human Architecture Review

For architecture-sensitive work:

```text
REQUEST
 ↓
ANALYZE
 ↓
SPEC / PLAN
 ↓
DOMAIN MODEL
 ↓
ARCHITECTURE DELTA
 ↓
RELEVANT VIEWS
 ↓
HUMAN / INDEPENDENT REVIEW
 ↓
ARCHITECTURE APPROVAL
 ↓
IMPLEMENT
 ↓
VERIFY
 ↓
CONVERGE
 ↓
SENS RUNTIME VALIDATION
```

Review focuses on:

```text
Entities
Boundaries
Ownership
Relationships
Dependencies
Data Flow
Call Direction
State/Lifecycle
External Integrations
Failure Paths
Trust Boundaries
Security Boundaries
Blast Radius
```

Correct syntax is not evidence of correct architecture.

---

# 21. Architecture Delta Workflow

Prefer changing only the relevant part of the model.

```text
Current Approved Model
       +
Proposed Change
       ↓
Architecture Delta
       ↓
Affected Views
       ↓
Review
       ↓
Approved Model Version
```

Benefits:

```text
Lower context use
Clearer review
Better traceability
Reduced drift
Better impact analysis
```

---

# 22. Reverse Architecture Discovery

Status:

```text
NEW
```

SAGE should be able to derive architecture candidates from:

```text
Source Code
Dependency Graphs
IaC
Terraform / Pulumi
Kubernetes
Cloud State
Runtime Telemetry
SENS / UEG
```

Result:

```text
Inferred Model
```

Suggested authority states:

```text
APPROVED
INFERRED
OBSERVED
PROPOSED
DEPRECATED
```

---

# 23. Inferred vs Approved Model Separation

Status:

```text
NEW
```

Core rule:

```text
Inferred Architecture ≠ Approved Architecture
Observed Runtime Architecture ≠ Approved Architecture
```

SAGE must preserve provenance and authority for each model.

Example:

```yaml
architecture_view:
  authority: inferred
  source: source-code-analysis
  confidence: 0.82
```

An Agent may propose an update, but approval changes authority.

---

# 24. SENS / UEG Integration

Status:

```text
KEEP
```

```text
SAGE Approved Architecture
          ↓
         UEG
          ↓
   Expected Relationships

Runtime Telemetry
          ↓
         SENS
          ↓
    Observed Relationships

Expected ↔ Observed
          ↓
Architecture Drift
Dependency Drift
Implementation Drift
Unexpected Runtime Relationship
Impact Analysis
CMDB Validation
```

SENS MUST NOT silently rewrite approved SAGE architecture.

---

# 25. Planned vs Observed Architecture

Status:

```text
KEEP
```

Example:

Approved:

```text
API
 ↓
Service
 ↓
Database
```

Observed:

```text
API
 └────────→ Database
```

Potential result:

```text
ARCHITECTURE_DRIFT
```

SAGE then determines whether implementation is wrong, architecture is outdated, the edge is expected but undocumented, or telemetry mapping is incorrect.

---

# 26. Cross-Artifact Consistency

Architecture participates in SAGE's Consistency Analyzer.

Check:

```text
Spec ↔ Architecture
Architecture ↔ ADR
Architecture ↔ Plan
Architecture ↔ Tasks
Architecture ↔ Tests
Architecture ↔ Security
Architecture ↔ Deployment
Architecture ↔ Documentation
Architecture ↔ Runtime Evidence
```

Possible findings:

```text
Missing relationship
Orphan component
Undocumented dependency
Architecture/ADR conflict
Implementation dependency absent from model
Obsolete model relationship
Unexpected runtime edge
```

---

# 27. Architecture Convergence

Architecture becomes part of the SAGE Convergence Engine.

```text
Approved Architecture
        ↓
Implementation
        ↓
Static + Runtime Evidence
        ↓
Compare
        ↓
CONVERGED
PARTIALLY_CONVERGED
NOT_CONVERGED
```

Unexplained material architecture drift blocks completion when the architecture gate is active.

---

# 28. Architecture Evidence

Architecture evidence may include:

```text
Model version / commit
Architecture delta
Validation output
Fitness-function results
Generated view references
Review result
Approval result
Runtime comparison
Drift findings
Renderer/tool versions
```

Do not trust:

```text
"The architecture looks correct."
```

as sufficient evidence.

---

# 29. Repository Convention

Recommended logical structure:

```text
architecture/
  model/
  views/
  policies/
  decisions/
  generated/
```

Example:

```text
architecture/
  model/
    landscape.c4
    applications.c4
    services.c4

  views/
    context.c4
    runtime.c4
    deployment.c4

  policies/
    architecture-rules.*

  decisions/
    ADR-*.md

  generated/
    svg/
    png/
    mermaid/
    d2/
```

This structure is indicative; do not create directories unless implementation needs them.

---

# 30. Agent Rules

Agents SHOULD:

```text
1. Inspect current architecture before significant implementation.
2. Query the architecture model instead of guessing.
3. Propose architecture deltas for significant changes.
4. Generate only relevant views.
5. Explain changed relationships.
6. Mark uncertain relationships explicitly.
7. Run architecture policies/fitness functions when active.
8. Request review when policy requires it.
9. Keep implementation and approved architecture synchronized.
10. Preserve stable IDs.
11. Allow SENS to compare planned vs runtime relationships.
```

Agents MUST NOT:

```text
Invent relationships for visual completeness.
Silently modify architecture while coding.
Treat generated PNG/SVG as source of truth.
Maintain conflicting canonical models.
Promote inferred architecture to approved without review.
```

---

# 31. Definition of Ready

For architecture-sensitive changes:

```text
Plan exists
Domain model exists where relevant
Architecture impact classified
Architecture delta exists
Relevant views generated
Key relationships reviewed
Unknowns/assumptions identified
Security boundaries reviewed where applicable
Required architecture approval complete
```

---

# 32. Definition of Done

Where architecture is relevant:

```text
Implementation matches approved architecture
Architecture model updated
Generated views current
Architecture validation passes
Fitness functions pass
Tests pass
SENS observability contract satisfied
No unexplained material drift remains
```

---

# 33. Anti-Overengineering

Do NOT:

```text
Generate every diagram type for every task.
Require human architecture review for trivial edits.
Maintain multiple canonical models.
Run expensive architecture checks when irrelevant.
Load the entire architecture model into every Agent context.
Use visually beautiful diagrams as a quality substitute.
Install every renderer/layout engine by default.
```

Prefer:

```text
Minimum relevant views
Scoped architecture context
Architecture deltas
Automated policy validation
Risk-adaptive review
Tool adapters installed only when needed
```

---

# 34. Tool Positioning Matrix

```text
LikeC4      → Default Architecture Model Adapter
Structurizr → First-class Alternative Model Adapter
D2          → Preferred Polished Renderer
Mermaid     → Lightweight Documentation Renderer
PlantUML    → Optional UML Specialist
Graphviz    → Graph Renderer / Layout
Kroki       → Optional Multi-format Rendering Gateway
ELK         → Preferred Complex Layout Engine
Dagre       → Lightweight Hierarchical Layout
SENS / UEG  → Runtime Observer / Validator
```

---

# 35. NEW / UPGRADE / CORRECT / REFINE / KEEP

## NEW

```text
Architecture Fitness Functions
Architecture Policy-as-Code
Reverse Architecture Discovery
Inferred vs Approved Model separation
Architecture authority/provenance states
```

## UPGRADE

```text
Structurizr → First-class Alternative Adapter
```

## CORRECT

```text
Kroki licensing assumption
→ Do not reject generically; evaluate actual deployment/dependencies.

PlantUML licensing assumption
→ Do not treat as universal blocker; verify actual chosen distribution/license.
```

## REFINE

```text
Layout Engine abstraction
ELK preferred for complex graphs
Graphviz general fallback
Dagre lightweight fallback
```

## KEEP

```text
LikeC4 baseline
D2 polished renderer
Mermaid lightweight renderer
SENS planned-vs-observed architecture
Human Architecture Review
Architecture Model as Source of Truth
```

---

# 36. SAGE Integration Instruction

The SAGE Architecture Agent should NOT blindly append this document.

Perform:

```text
Current SAGE Architecture
        vs
This Final Delta
        ↓
COVERED / PARTIAL / MISSING / REJECTED
        ↓
Minimal Compatible Update
        ↓
Schema / Policy Updates
        ↓
Conformance Tests
        ↓
Review
```

Requirements:

```text
Do not modify frozen SAGE v0.7 decisions without new evidence.
Do not duplicate existing subsystems.
Preserve Provider/Tool independence.
Preserve Proportional Engineering.
Preserve Repository as Source of Truth.
Preserve SENS ownership boundary.
```

---

# 37. Exact Next Action for SAGE

```text
1. Read current SAGE v0.8 Execution Protocol & Skill Contract.
2. Read existing Architecture/Diagram deltas.
3. Treat this file as the latest consolidated architecture-diagram delta.
4. Identify duplicate/obsolete prior diagram proposals.
5. Merge only missing/partial capabilities.
6. Formalize Architecture Model API.
7. Formalize authority states:
   APPROVED / INFERRED / OBSERVED / PROPOSED / DEPRECATED.
8. Add Architecture Policy / Fitness Function hooks.
9. Add Diagram Selection Policy.
10. Add Renderer Router and LayoutEngine abstractions.
11. Keep LikeC4 default and Structurizr alternative.
12. Add Reverse Architecture Discovery contract.
13. Connect approved model identities to SENS/UEG.
14. Add relevant conformance tests.
15. Run Anti-Overengineering Check.
16. Report exactly what changed.
```

---

# 38. Final Architecture Decision

```text
Architecture Modeling
→ FIRST-CLASS SAGE CAPABILITY

Architecture Model
→ SOURCE OF TRUTH

LikeC4
→ DEFAULT MODEL ADAPTER

Structurizr
→ FIRST-CLASS ALTERNATIVE

D2
→ POLISHED RENDERER

Mermaid
→ LIGHTWEIGHT RENDERER

PlantUML
→ OPTIONAL SPECIALIST

Graphviz
→ GRAPH / LAYOUT SUPPORT

Kroki
→ OPTIONAL RENDERING GATEWAY

ELK
→ PREFERRED COMPLEX LAYOUT ENGINE

Architecture Fitness Functions
→ ADOPT

Architecture Policy-as-Code
→ ADOPT

Reverse Architecture Discovery
→ ADOPT

Inferred vs Approved Separation
→ ADOPT

SENS / UEG
→ OBSERVED RUNTIME GRAPH + VALIDATION

Planned ↔ Observed
→ ARCHITECTURE DRIFT / CONVERGENCE
```

Final principle:

> **Model first. Review relationships before code. Enforce important architecture rules automatically. Render from the model. Infer architecture without confusing inference with authority. Implement against the approved model. Let SENS compare planned architecture with runtime reality.**
