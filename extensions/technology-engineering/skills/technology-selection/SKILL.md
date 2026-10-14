---
name: technology-selection
description: Compare implementation languages, frameworks and toolchains for architecturally significant SAGE component decisions; produce an evidence-linked technology decision before implementation.
---

Read [the specialist contract](../../docs/specialist-contract.md). Use the
repository's current stack as a candidate; do not trigger a full comparison
for an isolated typo or routine change within an accepted stack.

For a material choice, identify target constraints and the affected stable
architecture ID. Filter infeasible options before comparing tradeoffs in
security, compatibility, performance, support, licensing and total maintenance
cost. Explain a single feasible option when the platform fixes the choice.
No language has a privileged default, including Rust.

Record alternatives, reasons, versioned official references and a validation
plan in a `sage_technology_decision` document. Do not invent numeric rankings
or claim a speedup from marketing material. Introducing another language needs
an integration/operating-cost rationale and a compatibility check. An actual
performance claim needs a reproducible benchmark receipt for the same revision.

Use the specialist catalog only for capabilities justified by this task. A
profile or `SKILL.md` is not an instantiated agent or proof of expertise.
Keep proposals separate from approval. Resolve uncertainty with a bounded
research task or an approved isolated spike; missing tools are NOT RUN.

Validate through `sage.ps1 technology -DecisionPath <path>` before planning.
Use `-Phase VERIFY` to check required receipt declarations and local artifact
hashes; this does not attest compiler execution or replace independent review.
No toolchain installation, production change or external execution is granted.
