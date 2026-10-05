# ADR: CLI-Anything Methodology

- **Status:** Accepted
- **Decision:** **ADAPT** the CLI-Anything methodology; SAGE does not depend on
  its code or service.
- **Adopted concepts:** stateful harnesses, human-readable plus `--json`
  output, test/validate/refine workflow, predictable command groups and MCP
  backed adapters where an MCP already exists.
- **License and maintenance:** record a fresh review before importing code.
- **Reference:** https://github.com/HKUDS/CLI-Anything
- **Inspected repository HEAD (2026-10-06):** `34f519533bc175d2fe287ab8316b0dd99bb9cc43`.
- **Selected evidence:** upstream README describes JSON output, REPL/subcommands
  and typed harness workflows. This is methodological reuse; no upstream code
  is copied or installed by this change.
- **Compatibility note:** the originally supplied `guides/mcp-backend.md` link
  does not expose readable guide content in the current review; it is not
  treated as evidence of an implemented backend. Review the actual revision
  before selecting an upstream implementation.
