[CmdletBinding()]
param([Parameter(Position=0)][ValidateSet('validate','demo','discover','interfaces','operations','lifecycle','ci')][string]$Command='validate',[string]$Capability,[string]$RunPath,[string]$RegistryPath,[string]$LedgerPath)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$root=$PSScriptRoot
$pwsh=(Get-Command pwsh -ErrorAction Stop).Source
switch ($Command) {
  'validate' { & $pwsh -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root 'tools\Test-SageContracts.ps1') }
  'demo' { & $pwsh -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root 'tools\Test-SageDemonstrator.ps1') }
  'discover' { if ([string]::IsNullOrWhiteSpace($Capability)) { throw 'discover requires -Capability' }; & $pwsh -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root 'tools\Test-SageDiscovery.ps1') -Capability $Capability }
  'operations' { & $pwsh -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root 'tools\Test-SageDeploymentRuntime.ps1') }
  'interfaces' {
    if ([string]::IsNullOrWhiteSpace($Capability)) { $Capability = 'json-schema-validation' }
    if ([string]::IsNullOrWhiteSpace($RegistryPath)) { $RegistryPath = Join-Path $root 'fixtures\v0.8\interfaces' }
    Import-Module (Join-Path $root 'runtime\reference\SageDiscovery.psm1') -Force
    $registry = Import-SageRegistrySet -Path $RegistryPath
    Find-SageCapabilities -Registry $registry -RequiredCapabilities @($Capability) -MaxSideEffect READ_ONLY | ConvertTo-Json -Depth 100
  }
  'lifecycle' {
    if ([string]::IsNullOrWhiteSpace($RunPath)) { $RunPath=Join-Path $root 'fixtures\v0.8\r2-feature-data-path.json' }
    if ([string]::IsNullOrWhiteSpace($RegistryPath)) { $RegistryPath=Join-Path $root 'fixtures\v0.8\registries' }
    if ([string]::IsNullOrWhiteSpace($LedgerPath)) { $LedgerPath=Join-Path $root 'tmp\sage-lifecycle-ledger.json' }
    Import-Module (Join-Path $root 'runtime\production\SageLifecycle.psm1') -Force
    $contract=Get-Content -Raw -LiteralPath $RunPath | ConvertFrom-Json -Depth 100 -DateKind String
    Invoke-SageLifecycle -RunContract $contract -RegistryPath $RegistryPath -LedgerPath $LedgerPath -RequiredCapabilities @('json-schema-validation') | ConvertTo-Json -Depth 30
  }
  'ci' { & $pwsh -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root 'tools\Invoke-SageReferenceCI.ps1') }
}
if (Test-Path variable:LASTEXITCODE) { if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } }
