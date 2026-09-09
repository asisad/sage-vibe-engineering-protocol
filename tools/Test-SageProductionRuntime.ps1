[CmdletBinding()]
param([string]$Root)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
if ([string]::IsNullOrWhiteSpace($Root)) {$Root=Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)}
Import-Module (Join-Path $Root 'runtime\production\SageProduction.psm1') -Force
$path=Join-Path $Root 'tmp\production-ledger-test.json'
$engine=New-SageProductionEngine -LedgerPath $path
$engine=Register-SageProductionProvider $engine ([pscustomobject]@{provider_id='provider.fixture';execution_policy='ADAPTER_ONLY'})
$engine=Register-SageProductionTool $engine ([pscustomobject]@{tool_id='tool.fixture';execution_policy='ADAPTER_ONLY'})
$run=Get-Content -Raw (Join-Path $Root 'fixtures\v0.8\r2-feature-data-path.json') | ConvertFrom-Json -Depth 100 -DateKind String
$result=Invoke-SageProductionRun -Engine $engine -RunContract $run
if ($result.final_state -ne 'DONE') {throw "Expected DONE, got $($result.final_state)"}
if ($result.external_execution -ne 'NOT_PERFORMED') {throw 'External execution must remain disabled.'}
$loaded=Get-Content -Raw $path | ConvertFrom-Json -Depth 100 -DateKind String
if ($loaded.status -ne 'SEALED' -or [string]::IsNullOrWhiteSpace($loaded.chain_head)) {throw 'Sealed ledger was not persisted.'}
$bad=$run | ConvertTo-Json -Depth 100 | ConvertFrom-Json -Depth 100 -DateKind String
$bad.gate_plan.gates[0].status='FAIL'
$badResult=Invoke-SageProductionRun -Engine $engine -RunContract $bad
if ($badResult.final_state -ne 'BLOCKED') {throw 'Failed gate must block production run.'}
[pscustomobject]@{status='PASS';done_state=$result.final_state;blocked_state=$badResult.final_state;ledger_sealed=$loaded.status;external_execution=$result.external_execution;providers=$result.providers_registered;tools=$result.tools_registered;history_states=@($result.workflow_history|ForEach-Object state)} | ConvertTo-Json -Depth 10
