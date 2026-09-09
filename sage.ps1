[CmdletBinding()]
param([Parameter(Position=0)][ValidateSet('validate','demo','discover','operations','ci')][string]$Command='validate',[string]$Capability)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$root=$PSScriptRoot
$pwsh=(Get-Command pwsh -ErrorAction Stop).Source
switch ($Command) {
  'validate' { & $pwsh -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root 'tools\Test-SageContracts.ps1') }
  'demo' { & $pwsh -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root 'tools\Test-SageDemonstrator.ps1') }
  'discover' { if ([string]::IsNullOrWhiteSpace($Capability)) { throw 'discover requires -Capability' }; & $pwsh -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root 'tools\Test-SageDiscovery.ps1') }
  'operations' { & $pwsh -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root 'tools\Test-SageDeploymentRuntime.ps1') }
  'ci' { & $pwsh -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root 'tools\Invoke-SageReferenceCI.ps1') }
}
