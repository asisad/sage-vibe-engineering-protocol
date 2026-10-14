---
name: robotics-motion
description: Servo/stepper/robotic motion, PWM, kinematics, drivers, encoders and safety.
---

Adapted from the supplied v0.2 blueprint. Before implementation, read
[the specialist contract](../../docs/specialist-contract.md) and the task's
technology decision. This workflow does not choose its own authority or run
an optional SENS integration.


# robotics-motion

Use only for the selected task scope. This is an on-demand workflow, not a running agent.

## Procedure
1. Obtain physical equipment details: actuator+driver, supply rails, wiring, axis limits, sensor feedback, emergency stop, desired unit system.
2. Separate command/planner logic from actuator-driver and safety supervisor; minimize blocking timing jitter.
3. Validate unit conversions, speed, torque, acceleration, limit switches, failure to receive control commands and safe-stop path.
4. Simulate trajectories and fault cases. Physical execution requires operator and explicit scope of approval.
5. Never infer GPIO-level output directly powers a motor; verify driver and electrical interface.
6. Output interface contract, simulation results, unresolved hardware constraints and clear NOT RUN hardware status.

## Deliverable
Return target fingerprint, changed files, tool versions, source URLs/revisions, PASS/FAIL/NOT RUN for checks, safe rollback conditions and actions awaiting approval.
