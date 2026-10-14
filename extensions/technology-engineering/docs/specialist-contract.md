# On-demand specialist contract / قرارداد متخصص

This optional extension adapts the user's 2026-10-14 v0.2 source templates;
the archived AGENTS.md and role text are source material, not repository-wide
instructions or grants. Existing SAGE constitution, scope and approvals win.

## Decision before implementation

- Reuse a suitable current stack before introducing another language/runtime.
- Choose by task/target and tradeoffs, not the model's self-assessed fluency or
  a fixed Rust/Python/TypeScript priority. Platform constraints can leave only
  one viable option; explain that rather than inventing competitors.
- Record versioned sources and link the component ID/model version, project
  revision, alternatives, constraint results, rationale and validation plan.
- Generate only relevant architecture/flow views from the same decision/model.
- An additional language requires a maintenance/interop-cost rationale and a
  compatibility check. Microservices, FFI and extra stacks are not mandatory.

## Specialist routing and evidence

The catalog contains 17 declared on-demand profiles. These declarations route
portable workflows; they are not deployed agents, available compilers, a host
installation or proof of expertise. The core eight-Skill bundle is preserved.
Use minimal necessary roles and independent review proportionate to risk.
Reference routing uses deterministic greedy capability coverage to avoid
redundant profiles; it is not proof of globally optimal staffing or actual
independent reviewer identity. The host must enforce executor/reviewer separation.
Never execute the literal example commands without checking the actual project,
versions, configured feature combinations, permissions and side effects.

Differentiate generated, documentation-reviewed, build-tested, simulated,
hardware-tested and deployed results. NOT RUN is not PASS. Reviewer agreement
does not substitute for test evidence. The reference validator checks data
relationships and local file hashes; it cannot attest that a compiler really
produced a file or that an external document is truthful/current.

The PLAN review may accept a well-formed proposal with pending builds/tests.
The VERIFY review rejects required NOT RUN/FAIL checks, missing/tampered/outside
artifacts, stale revision references and reference fixtures as project proof.
Neither review grants execution/approval authority.

## Boundaries

SAGE retains engineering decisions. SENS is an optional observation/evidence
integration, not an agent controller. Loss of optional telemetry may fail open;
approval, scope, safety and mandatory evidence gates fail closed. This extension
does not build a SENS service, move graph ownership or change project branding.

Hardware/robotics/CNC/FPGA workflows are optional future task profiles, not
installed tools. Code generation or simulation never authorizes flashing,
energizing, motion, deployment or infrastructure apply. Keep these actions
separately scoped and approved. No device access is exercised by this package.

## Sources and provenance

Original Markdown/ZIP are byte-preserved in `sources/supplied-originals/` and
listed in SOURCE_REGISTRY/MANIFEST. Skill language/domain procedures are adapted
from that package; its blanket Rust routing and always-needed P0 roles are not.

Methodological references inspected 2026-10-14:

- CMU SEI, ATAM, 1998: https://www.sei.cmu.edu/library/the-architecture-tradeoff-analysis-method/
- Microsoft ADR guidance, updated 2026-04-13: https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record

These support reasoning about tradeoffs and recording decisions, not certification
of SAGE or benchmarked superiority of a language. For APIs, consult official docs
matching the actual project's pinned versions at task time. The supplied source
index is an entry point, not a proof of compatibility.
