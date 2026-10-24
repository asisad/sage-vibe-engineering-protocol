# SAGE bounded autonomous execution — implementation contract

Approved 2026-10-24: development branch only, no GitHub push/release. The initial
0.1 delivery and the separately approved 0.2 Ruflo delivery each have their own
durable, non-resettable limit of 12 model jobs; this is not a permanent grant.
The Ruflo acceptance consumed six new jobs. Existing
0.8.4 baseline, ECC source pins, source-only semantics and Strix gates stay intact.

This is an additive Python standard-library runtime. It does not replace the
existing PowerShell reference engine or install native ECC hooks/agents.

## Runtime flow

Intake -> bounded SAGE/ECC discovery -> model plan -> explicit plan approval
(or narrowly preauthorized low-risk local-plan approval) -> structured file
generation -> isolated checks -> independent model review -> bounded
repair -> delivery. Missing requirements/tools/permission cause a visible stop.

Generated source is data until the controller validates/writes it. Model jobs
use read-only Codex sessions, structured JSON and disabled user configuration;
no shell commands, model names, grants or providers come from source packets.
Checks run only using fixed runtime-owned profiles in a verified native sandbox
or an explicitly selected, locally provisioned Docker image. No
unsandboxed fallback, dependency installation, network service, deploy or push.

Initial execution profiles: python-stdlib, node-stdlib, static-web. Other stacks
must stop with a clear capability gap, not silently substitute a language.

## Source layout and ownership for this implementation

- `src/sage_runtime/engine.py`, `schemas.py`, `discovery.py`: root integrator.
- `providers.py`, `process.py`, `verify_profile.py` and provider tests: transport.
- `safety.py`, `storage.py` and their tests: policy/storage worker.
- packaging, `cli.py`, entrypoints, bilingual guide: packaging worker.
- integration, regression, live acceptance and final reports: root integrator.

The 0.2 addition is `ruflo.py`: a fixed-tool, metadata-only Ruflo MCP coordinator
around the existing Codex worker. It does not delegate SAGE authority or enable
native Ruflo `agent_execute`. See `extensions/ruflo/LIVE_BINDING.fa-en.md` and
`extensions/ruflo/live-acceptance.json` for the exact mode and live proof.

## Shared Python interfaces

`safety.SageError(code, message)` exposes `.code` and a safe human-readable text.
`safety.Policy` is a dataclass with defaults: max_model_calls=12, max_repairs=2,
max_seconds=900, max_file_bytes=131072, max_project_bytes=2097152,
max_files=64, max_context_bytes=131072. It validates finite bounded values and
serializes using `dataclasses.asdict`. `safe_relative(value)` validates a POSIX
project-relative source path. `write_project_files(workspace, files, policy)`
validates the complete list of `{path,content}` before writes, rejects links,
credentials and protected paths, never deletes, and returns a file/hash manifest.
`project_manifest(workspace)` returns the same sorted path/hash records,
excluding `.git`, and rejects unexpected links and special files.

`storage.RunStore(base)` provides `create(manifest)->run_id`, `load(run_id)`,
`save(run_id,state)`, `event(run_id,event,data)->record`, `events(run_id)`,
`verify(run_id)->bool` and `lock(run_id)` as an OS-released lock context manager.
State/checkpoint integrity must be bound to the append-only hash-chain ledger.
`run_dir(run_id)` returns the private run evidence folder outside the project.
State files and evidence never live in the model-generated project directory.

`providers.ModelResult(payload:dict, receipt:dict)` is a dataclass.
`providers.CodexProvider.generate(stage,prompt,schema,workspace,timeout_seconds)`
returns ModelResult or raises SageError. One controller invocation, no controller
retry/fallback. The CLI's internal HTTP/SSE retries are not a spending guarantee.
`doctor()` reports local version/auth/readiness without printing credentials.
`providers.SandboxRunner.run(profile,workspace,timeout_seconds)` returns a receipt
with status PASS/FAIL/BLOCKED, actual argv, exit code, bounded stdout/stderr,
duration and sandbox identity. No model-auth environment is forwarded to checks.
Provider sessions never execute generated source; fixed checks do so in sandbox.
Historical 0.1 acceptance used Codex 0.163.0; 0.2 Ruflo acceptance used 0.164.0. Native
Windows isolation is unavailable on this host and fails closed. The approved
Docker Python/static-web fallback uses a local immutable image, no network or
auth mounts, read-only source/root, non-root execution and resource limits.
Node has no Docker fallback. Unsupported capabilities must fail closed.

`engine.Engine(kit_root,state_root,provider=None,runner=None)` exposes:
- `create(idea,workspace,approval_id,*,live=False,auto_approve_plan=False,
  max_model_calls=12,max_repairs=2,max_seconds=900,profile=None,source=None,
  coordinator=None)->dict`.
- `run(run_id,*,live=False,pause_after=None)->dict` (resume from durable state).
- `approve(run_id,plan_hash)->dict`, `status(run_id)->dict`, `cancel(run_id)->dict`.
- `clarify(run_id,answer)->dict` (new input stays subject to the same policy).

CLI: `sage doctor`, `sage build IDEA --output ABS_NEW --live --approval-id ID`
with optional `--auto-approve-plan`; `sage status ID`, `sage resume ID --live`,
`sage approve ID --plan-hash HASH`, `sage clarify ID --answer TEXT`, `sage cancel ID`.
Shared `--kit-root` and `--state-root` options select explicit locations. The
installed wheel includes the necessary attributed capability resources.

An explicit `--ruflo-config` on a new build binds an immutable local Docker image
and a separate private metadata tree to its checkpoint. Resume cannot silently
remove that binding. Ruflo must create/assign/confirm each worker job before the
model runs; completion is only a validated model-response hash. SAGE still owns
source writes, isolated tests, review and DONE. Failure never routes around the
coordinator. A hard container lifetime bounds orphaned processes. Under the
exclusive run lock, resume cancels unfinished metadata from this same run before
creating a new job; it does not replay or refund an uncertain model invocation.

Budget is durable: reserve each model call before launch; failed/crashed calls
remain charged, and resume cannot reset limits. Only a checked delivery at the
current project hash may say DONE. Tests cannot be declared passed by a model.
The runtime cannot promise a precise monetary spending cap for account auth;
call count, elapsed time, repair count, payload sizes and observed usage are the
enforceable local controls. No automatic model/provider fallback.

## Live acceptance

Use isolated owned examples, inspect independent behavioral oracles, prove a
generated project, a bounded repair and stop/resume. Count every model launch,
including failed attempts, in one delivery-level budget. Provider unavailable or
sandbox unavailable is BLOCKED, not successful live acceptance.

Official Codex reference consulted 2026-10-24:
https://learn.chatgpt.com/docs/non-interactive-mode
https://learn.chatgpt.com/docs/agent-approvals-security
