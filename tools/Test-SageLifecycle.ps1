[CmdletBinding()]
param([string]$Root)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
if ([string]::IsNullOrWhiteSpace($Root)) {$Root=Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)}
Import-Module (Join-Path $Root 'runtime\production\SageLifecycle.psm1') -Force
$run=Get-Content -Raw (Join-Path $Root 'fixtures\v0.8\r2-feature-data-path.json') | ConvertFrom-Json -Depth 100 -DateKind String
$ledger=Join-Path $Root 'tmp\v0.8.3-lifecycle-ledger.json'
$registry=Join-Path $Root 'fixtures\v0.8\registries'
$result=Invoke-SageLifecycle -RunContract $run -RegistryPath $registry -LedgerPath $ledger -RequiredCapabilities @('json-schema-validation')
if ($result.status -ne 'DONE') {throw "Lifecycle expected DONE, got $($result.status)"}
if ($result.ledger_status -ne 'SEALED') {throw 'Lifecycle ledger was not sealed.'}
if ($result.external_execution -ne 'NOT_PERFORMED' -or $result.implementation.executed) {throw 'Lifecycle must remain dry-run.'}
if (@($result.stages|Where-Object status -ne 'PASS').Count -ne 0) {throw 'All lifecycle stages must pass.'}
$loaded=Get-Content -Raw $ledger | ConvertFrom-Json -Depth 100 -DateKind String
if ($loaded.chain_head -ne $result.ledger_chain_head) {throw 'Persisted ledger chain head mismatch.'}
$cliLedger=Join-Path $Root 'tmp\v0.8.3-cli-lifecycle-ledger.json'
$cliJson=& (Get-Command pwsh).Source -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Root 'sage.ps1') lifecycle -LedgerPath $cliLedger
$cliResult=$cliJson | ConvertFrom-Json -Depth 100
if ($cliResult.status -ne 'DONE' -or $cliResult.ledger_status -ne 'SEALED') {throw 'CLI lifecycle did not complete a sealed dry-run.'}
[pscustomobject]@{status='PASS';release='0.8.3';lifecycle='INTAKE>DISCOVER>PLAN>IMPLEMENT>VERIFY';stage_count=@($result.stages).Count;ledger_status=$result.ledger_status;ledger_entries=@($loaded.entries).Count;external_execution=$result.external_execution;selected_capabilities=@($result.plan.selected_capabilities)} | ConvertTo-Json -Depth 10
