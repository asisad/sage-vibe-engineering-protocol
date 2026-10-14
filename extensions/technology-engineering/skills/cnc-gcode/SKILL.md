---
name: cnc-gcode
description: G-code dialects, CNC machines, laser/3D printer commands, GRBL/LinuxCNC/Marlin/Klipper.
---

Adapted from the supplied v0.2 blueprint. Before implementation, read
[the specialist contract](../../docs/specialist-contract.md) and the task's
technology decision. This workflow does not choose its own authority or run
an optional SENS integration.


# cnc-gcode

Use only for the selected task scope. This is an on-demand workflow, not a running agent.

## Procedure
1. Identify controller and firmware/version, G-code dialect, machine dimensions, tools, machine coordinate systems and active modal state.
2. Distinguish generation/interpretation of commands from actual physical execution.
3. Verify units (mm/inch), absolute/relative mode, feed rate and travel bounds; assess spindle, laser, heater and collision hazards.
4. Prefer parser verification and simulation/dry-run with target-appropriate tools and human review.
5. Never send generated commands to machine, initiate movement, home or energize equipment without explicit approval.
6. Report controller compatibility and remaining assumptions instead of claiming universal G-code portability.

## Deliverable
Return target fingerprint, changed files, tool versions, source URLs/revisions, PASS/FAIL/NOT RUN for checks, safe rollback conditions and actions awaiting approval.
