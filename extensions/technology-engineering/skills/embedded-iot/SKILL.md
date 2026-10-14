---
name: embedded-iot
description: Arduino C++, ESP32/ESP-IDF, MicroPython, embedded Rust and MCU firmware programming.
---

Adapted from the supplied v0.2 blueprint. Before implementation, read
[the specialist contract](../../docs/specialist-contract.md) and the task's
technology decision. This workflow does not choose its own authority or run
an optional SENS integration.


# embedded-iot

Use only for the selected task scope. This is an on-demand workflow, not a running agent.

## Procedure
1. Identify exact SoC/board/FQBN, chip version, voltage/current/pinout, flash size, peripheral constraints, power and real hardware availability.
2. Pick Arduino sketches/C++, ESP-IDF C/C++, MicroPython or Rust esp-hal by target compatibility and performance/maintenance requirements; no universal Rust mandate.
3. Verify device-specific SDK/API docs, toolchain and library versions before code. Never invent pins, PWM channel numbers, supported frequencies or bootloader behavior.
4. Plan safe startup/shutdown, watchdog, brownout/power failure, OTA validation and peripheral faults.
5. Build offline (`arduino-cli compile`, `idf.py build`, relevant Rust target) or simulate. Mark hardware tests NOT RUN if not performed.
6. Upload/flash/erase/eFuse modification is a separately approved action; no ambient access to serial ports or powered circuits.

## Deliverable
Return target fingerprint, changed files, tool versions, source URLs/revisions, PASS/FAIL/NOT RUN for checks, safe rollback conditions and actions awaiting approval.
