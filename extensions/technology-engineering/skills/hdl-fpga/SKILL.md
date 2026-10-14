---
name: hdl-fpga
description: Verilog/SystemVerilog/VHDL, FPGA simulation, synthesis and timing.
---

Adapted from the supplied v0.2 blueprint. Before implementation, read
[the specialist contract](../../docs/specialist-contract.md) and the task's
technology decision. This workflow does not choose its own authority or run
an optional SENS integration.


# hdl-fpga

Use only for the selected task scope. This is an on-demand workflow, not a running agent.

## Procedure
1. Verify target family, clocking, I/O banks, board pin constraints and tool versions.
2. Define RTL function, reset/clock-domain strategy, timing and hardware resource budgets.
3. Write a deterministic testbench and run lint/elaboration/simulation in a sandbox.
4. Assess synthesis and timing closure when correct licensed toolchain is available.
5. Never claim on-hardware pass without an approved device run. Flashing a bitstream must be separately authorized.
6. Report simulation evidence, board-dependent assumptions and safe deployment plan.

## Deliverable
Return target fingerprint, changed files, tool versions, source URLs/revisions, PASS/FAIL/NOT RUN for checks, safe rollback conditions and actions awaiting approval.
