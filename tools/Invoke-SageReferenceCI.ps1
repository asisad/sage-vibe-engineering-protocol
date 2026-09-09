[CmdletBinding()]
param([string]$Root)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($Root)) { $Root = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent }
$pwsh = (Get-Command pwsh -ErrorAction Stop).Source
$scripts = @('Test-SageContracts.ps1','Test-SageReferenceRuntime.ps1','Test-SageOrchestrator.ps1','Test-SageProductionRuntime.ps1','Test-SageProductionAdapters.ps1','Test-SageDescriptorRegistry.ps1','Test-SageLocalLiveAdapter.ps1','Test-SageDemonstrator.ps1','Test-SageDiscovery.ps1','Test-SageEnhancements.ps1','Test-SageOperations.ps1','Test-SageDeploymentRuntime.ps1','Test-SageLifecycle.ps1','Test-SageRelease.ps1')
$results = [System.Collections.Generic.List[object]]::new()
foreach ($script in $scripts) {
    & $pwsh -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Root "tools\$script") | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "CI check failed: $script" }
    $results.Add([pscustomobject]@{ script=$script; status='PASS' })
}
[pscustomobject]@{ status='PASS'; checks=@($results); completed_at=[DateTime]::UtcNow.ToString('o') } | ConvertTo-Json -Depth 10
