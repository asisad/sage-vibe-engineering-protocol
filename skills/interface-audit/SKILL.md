---
name: interface-audit
description: Audit API, bridge, CLI and MCP responsibilities and select an agent-facing interface during SAGE discovery or integration planning.
---

# Interface Audit

Audit an agent-facing integration before routing it. Identify the native API,
bridge, CLI/MCP surface and Skill; record ADOPT/ADAPT/BUILD; verify typed
outputs, errors, timeout, compatibility, security preservation and evidence.
This Skill is advisory and never grants execution authority.

Read `docs/architecture/agent-native-interfaces.md` and the standards matching
the proposed surface. Inputs: required capabilities, side-effect ceiling,
descriptor version, evidence refs and current target/API constraints.
Record the API source and ownership of each layer; use a direct native binding
when no bridge is needed. Treat GUI host tests as separate from headless tests.

Output: an interface descriptor validated by
`schemas/v0.8/sage-agent-interface.schema.json`, an ADOPT/ADAPT/BUILD decision
with license/maintenance rationale, and a coverage report. Use the reference
Discovery module to recommend candidates. Descriptor assertions do not prove
that a live transport works; identify missing runtime evidence explicitly.
Finish when requirements map to evidence or named unresolved gaps.
