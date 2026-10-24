# SAGE × Ruflo — Live coding acceptance (candidate)

This change adds an **independent** verification gate. It does **not** provision a host, start Ruflo, authorize model access, or claim an autonomous agent has completed the task.

## Scope

The evaluation task is deliberately fixed: edit an isolated Python calculator's `add(a,b)` function so that a pre-existing failing unit test passes. Run precisely the same fixture with (1) a directly invoked host coding agent, (2) approved Ruflo MCP, and (3) OpenHands SDK. Keep the same model, prompt, maximum token/cost budget and machine where the engines permit it. Save each run under its own isolated workspace. No runner should touch the SAGE source tree.

## Prepare the fixture (each engine gets its own fresh copy)

From the SAGE checkout, in PowerShell 7:

```powershell
$fixture = Join-Path $env:TEMP 'sage-ruflo-fixture'
New-Item -ItemType Directory -Force "$fixture/src","$fixture/tests" | Out-Null
Set-Content -Encoding utf8 "$fixture/src/__init__.py" ''
Set-Content -Encoding utf8 "$fixture/src/calc.py" "def add(a, b):`n    return a - b`n"
Set-Content -Encoding utf8 "$fixture/tests/test_calc.py" "import unittest`nfrom src.calc import add`nclass TestAdd(unittest.TestCase):`n    def test_sum(self):`n        self.assertEqual(add(2, 3), 5)`n"
python -m unittest discover -s "$fixture/tests" -p test_calc.py
# The initial test MUST fail before the agent is run.
python -c "import hashlib,pathlib; print(hashlib.sha256(pathlib.Path(r'$fixture/src/calc.py').read_bytes()).hexdigest())"
```

The baseline digest must be saved **before** the agent changes the file. In each agent run, instruct it to fix only `src/calc.py` and run the test. For Ruflo, follow [the existing approval-bound runtime guide](../../extensions/ruflo/README.fa-en.md); do not invoke mutating tools without an approved SAGE RunContract and OS-isolated workspace. The current adapter cannot impose OS sandboxing.

Run the gate after the agent stops:

```powershell
python tools/verify_ruflo_live_acceptance.py --engine ruflo --workspace "$fixture" --task-id ruflo.fixture.001 --baseline "<64-char sha256 before>" --output "$env:TEMP/ruflo-acceptance.json"
```

Provide the actual baseline SHA256, not the placeholder. Pass the corresponding `--engine` for other candidates. **PASS requires both** a changed target and a passing independently executed test; a successful Ruflo `tools/call` response alone cannot yield PASS. Keep a separate receipt for model identity, provider cost, total elapsed time, cancellation behaviour, restart/memory retrieval, and the upstream adapter's approval ID. A missing dimension remains NOT_VERIFIED, not a zero or a PASS.

## Safety and operational limits

- No automatic upstream npm install, daemon, host hooks or credential handling.
- Evaluation needs Python, an explicit disposable workspace and an external OS-level isolation boundary.
- Only the bounded Python unittest fixture is executed; no arbitrary shell command argument.
- The verifier records digests and boolean outcomes, not prompts, raw model responses or secrets.
- A successful fixture does not establish full Ruflo swarm, vector RAG, federation, persistent memory or a production SAGE runtime.
- Prefer reviewing evidence from all three engines before changing a SAGE default.
