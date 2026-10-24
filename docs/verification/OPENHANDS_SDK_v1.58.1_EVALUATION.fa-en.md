# SAGE — OpenHands SDK 1.58.1 evaluation / گزارش نهایی بررسی

Decision: **NOT_ADOPTED_IN_CURRENT_CONTRACT**. Review completed 2026-10-24.
Tracking: [Issue #4](https://github.com/asisad/sage-vibe-engineering-protocol/issues/4).
The Codex default and optional Ruflo binding are unchanged.

**نتیجه:** اتصال آزمایشی OpenHands واقعاً کار کرد، ولی در قرارداد فعلی Worker
فایدهٔ افزوده‌ای که نگهداری موتور دوم را توجیه کند اثبات نشد. وابستگی یا
Adapter دیگری وارد محصول نشده است. این تصمیم دربارهٔ کاربرد فعلی SAGE است؛
حکم کلی دربارهٔ کیفیت OpenHands نیست.

## Preserved baseline / مبنا و مالکیت

SAGE exclusively retains approval, scope, budget, source application, state,
evidence and independent verification. SDK output was data, never authority.
No duplicate planner, memory, skill catalog, permissions or ledger was added.

- Local baseline: `c017f8108a57d711a646c181a5f9ff3e5fdb660a`.
- GitHub baseline: `73696bb319637ea5ca32a4d65d8f8015e5cbbb56`.
- [Sync PR #5](https://github.com/asisad/sage-vibe-engineering-protocol/pull/5),
  normal merge `3c65765ef9c76115cd17d449d7e469739adf336a`.
- [SAGE Windows/Linux CI](https://github.com/asisad/sage-vibe-engineering-protocol/actions/runs/40119435275)
  and [real Ruflo smoke](https://github.com/asisad/sage-vibe-engineering-protocol/actions/runs/40119435165)
  passed. A Windows 8.3-path fixture assertion was corrected without relaxing policy.
- Initial 1,674 manifest hashes, 750 wheel resources, 12 runtime modules,
  wheel/sdist/rebuilt-wheel payloads and both prior run ledgers were checked.
  Four newer GitHub acceptance files were preserved. No old-success replay.

Historical reports retain their original scope/date. Runtime remains `0.2.0`;
the historical `v0.8.4` tag was not moved and no release was republished.

## Capability comparison / تطبیق قابلیت‌ها

| Capability | Existing SAGE + Ruflo/Codex | SDK evidence | Disposition |
|---|---|---|---|
| Planning, scope, approval, budget, state, evidence | Existing core; real accepted runs | Same core reused | SAGE owns these |
| Structured coding response | Codex returns data; controller applies files | Agent + Conversation produced two accepted products | Feasible, overlapping |
| Independent tests and fresh review | Existing hardened checks and separate Codex session | Same checker and reviewer retained | No added improvement proved |
| Pause/resume, recovery | Durable SAGE checkpoints; real Ruflo resume | SAGE slug pause/resume; charged bootstrap recovery | Existing core reused |
| Native Conversation persistence | SAGE already persists evidence/state | New Conversation object read finished state, same process | No crash/restart proof |
| Usage metrics | Existing Codex receipts | SDK typed token metrics, price-map estimate | Different receipt; billing unknown |
| Native Terminal/FileEditor, iterative coding | Excluded from data-only worker contract | Not installed/activated; tools dependency lacked wheel | Not admitted |
| DockerWorkspace, Agent Server, REST/WebSocket | Local hardened checks; isolated Ruflo MCP | Documentation/source review only | No live proof or demonstrated need |
| MCP, memory, skills, hooks | Existing interfaces/catalog | SDK copies disabled | No duplicate systems |

SDK `finished`, API success or Ruflo queue completion was never product DONE.
SAGE independent verification and review controlled acceptance.

## Versions and isolation / نسخه و ایزوله‌سازی

Release/tag and PyPI metadata were checked before installation. Tag `v1.58.1`
points to `60192ed54db73ac658ac1a07462916126c32d3a0`; Python requires `>=3.12`.
A disposable Python `3.13.15` environment preserved main Python `3.14.8` and
the dependency-free SAGE runtime. Official SDK wheel SHA-256:
`eb8dfecd5edef95a073db29df2194388f3d59d345a54aa4adab6456484e6615e`.

SDK/workspace `1.58.1` installed as wheels: 149 distributions in that environment,
including transitive `openhands-agent-server 1.49.5`, which was **not invoked**.
This was not a verified `1.58.1` server stack. Native tools were not installed:
`func-timeout 4.3.5` lacked a wheel; the wheels-only policy prevented a source build.

Only the approved existing ChatGPT subscription was used. The parent passed
a short-lived access token to the official SDK subscription client through
private process memory/stdin. No refresh token or paid API key was delegated.
Native account storage stayed unchanged; successful SDK receipts confirmed no
token in Conversation persistence. No credentials are in published evidence.
The SDK worker used isolated settings and no mutating tools, hooks, MCP, skills,
critic or auxiliary models. Native OS tools were not delegated to the model.

Generated-code checks used the existing read-only, non-root, network-denied
Python image `sha256:6a0e06f5ba0b373d051aabd3fffb9b873f27f9a2a3a14bcbe37dee6f0e3bbc70`,
with 1 CPU, 256 MiB and 64-PID caps. These are configured check limits, not
measured whole-worker resource peaks. Original Ruflo image/binding stayed intact.

## Real results / نتایج عملی

Sanitized receipts, hashes and usage: [RESULTS.json](OPENHANDS_SDK_v1.58.1_RESULTS.json).

| Scenario | Direct Codex | SAGE + Ruflo + Codex | SAGE + SDK |
|---|---|---|---|
| Unicode slug | Independent PASS, 5 tests; 48.44 s | Historical DONE, 6 tests; no replay | DONE, 9 tests; 357.86 active s including failed bootstraps |
| Division repair | Independent PASS, 7 tests; 39.34 s | Historical DONE, 7 tests; no replay | DONE, 7 tests; 123.10 active s |
| Actual acceptance-tool defect | Independent PASS, 6 tests; 58.73 s | R2 review BLOCKED; 1 planner job | R2 review BLOCKED; 1 planner job; SDK not called |

این جدول رتبه‌بندی سرعت یا برتری موتور نیست. نتایج Ruflo تاریخی‌اند و شناسهٔ
مدل واقعی آن‌ها اثبات نشده؛ مدل درخواستی آزمون‌های جدید `gpt-6.1-sol` بود.
Prompt، پیام سیستمی، تعداد مراحل و Snapshot اولیه یکسان کامل نیستند. Direct
فاقد بازبینی چرخهٔ SAGE است؛ تعداد تست بیشتر هم اثبات کیفیت بالاتر نیست.

Successful SDK implementation-only durations: slug `62.107059 s`, divide
`46.180462 s`. Slug required three charged receipt/bootstrap fixes: these were
harness collection failures, not proof of incorrect generated products.
Division's isolated original source failed the independent oracle. Original
repair snapshots stayed unchanged; current source hashes and SAGE ledgers were
read back. R2 stops were preserved, never bypassed or relabeled as successful coding.

The real repository defect was accepting an all-skipped unittest suite from
exit code zero. Direct's candidate passed fresh read-only Codex review; the
focused fix now checks executed test counts. Five regressions cover unchanged/
failed and successful code, empty, all-skipped and mixed suites. This bounded
calculator helper is **not a sandbox or general security attestation**; the
actual SAGE runtime verifier is separate.

## Budget, tests and limits / بودجه و محدودیت‌ها

- New grant: **15/30 reserved jobs**, including failed slots `6,7,8` and fresh
  verifier review. No refund, hidden fallback or old-budget reset. Reservations
  do not attest internal HTTP request counts. Historical budget remains **6/12**.
- The 900-second ceiling counts cumulative active model/check time, excluding
  external pauses/debugging. SDK subprocess jobs also had bounded timeouts.
- No paid API used. Actual monetary cost is **unknown**, not zero. SDK estimates
  `0.039224` and `0.032442` for successful implementations are public price-map
  estimates, not subscription billing or total evaluation cost.
- Peak CPU/RAM: **NOT_MEASURED**. No controlled benchmark, live remote SDK server,
  native mutating SDK tools, crash recovery or live SDK MCP validation.
- Experimental offline suite: **192 discovered**, zero failures/errors, six
  local skips: five missing optional packaging backend, one Windows symlink.
  Ten dedicated negative tests cover authority mutation, budget-reset rejection,
  cancellation, scope escape, expired/API-only grants, charging failures,
  synthetic receipts and no implicit Codex fallback.
- No new Strix scan or security certification. Final CI belongs to the final
  PR/checks, not the historical acceptance report.

## Disposition and rollback / سرنوشت کد و بازگشت

Experiment source is preserved in commit
[`58ff45b35de4014e0130bbf8c2da7fb3a7a4ed3b`](https://github.com/asisad/sage-vibe-engineering-protocol/commit/58ff45b35de4014e0130bbf8c2da7fb3a7a4ed3b).
Its worker/harness/tests and evaluation-only 30-job extension were removed from
the final production tree. The original 12-job helper and runtime source remain.
No SDK adapter is registered, packaged or selectable; there is no dormant
integration to accidentally activate. The temporary SDK environment is disposable;
private receipts, generated examples and the pinned wheel are retained locally.
Automatic approval review rejected removal of the temporary SDK environment
with `blocked by policy`. It therefore also remains isolated on this host;
it is not a registered engine or a production dependency.
Reverting the fixture-verifier fix cannot change Ruflo binding or runtime0.2.0.

Reconsider only for a concrete unmet task requiring native iterative tools or
a remote Agent Server, under a new scoped experiment. Any eventual adapter
still requires the existing contract, disabled feature flag, negative CI tests,
independent acceptance, receipts and rollback. That future integration is not
part of this completed review.

## Primary sources / منابع اصلی

- [Pinned SDK source](https://github.com/OpenHands/software-agent-sdk/tree/v1.58.1)
- [Release v1.58.1](https://github.com/OpenHands/software-agent-sdk/releases/tag/v1.58.1)
- [PyPI metadata](https://pypi.org/pypi/openhands-sdk/1.58.1/json)
- [SDK docs](https://docs.openhands.dev/sdk)
- [Subscriptions](https://docs.openhands.dev/sdk/guides/llm-subscriptions)
- [Docker workspace](https://docs.openhands.dev/sdk/guides/agent-server/docker-sandbox)
- [Persistence](https://docs.openhands.dev/sdk/guides/convo-persistence)
- [Metrics](https://docs.openhands.dev/sdk/guides/metrics)

Live documentation may differ from the pinned tag. Documented capability is
not scored as observed SAGE evidence. Raw private run state is not published.
