[CmdletBinding()]
param([string]$Root, [string]$EvidencePath)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($Root)) { $Root = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent }
$pwsh = (Get-Command pwsh -ErrorAction Stop).Source
$scripts = @('Test-SageContracts.ps1','Test-SageReferenceRuntime.ps1','Test-SageOrchestrator.ps1','Test-SageProductionRuntime.ps1','Test-SageProductionAdapters.ps1','Test-SageDescriptorRegistry.ps1','Test-SageLocalLiveAdapter.ps1','Test-SageDemonstrator.ps1','Test-SageDiscovery.ps1','Test-SageEnhancements.ps1','Test-SageOperations.ps1','Test-SageDeploymentRuntime.ps1','Test-SageLifecycle.ps1','Test-SageDiagram.ps1','Test-SageSdk.ps1','Test-SageAgentInterfaces.ps1','Test-SageRelease.ps1')
$results = [System.Collections.Generic.List[object]]::new()
foreach ($script in $scripts) {
    $output = & $pwsh -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Root "tools\$script") | Out-String
    if ($LASTEXITCODE -ne 0) { throw "CI check failed: $script`n$output" }
    $results.Add([pscustomobject]@{ script=$script; status='PASS' })
}
$result = [pscustomobject]@{ status='PASS'; checks=@($results); completed_at=[DateTime]::UtcNow.ToString('o') }
$json = $result | ConvertTo-Json -Depth 10
if ($EvidencePath) {
    $directory = Split-Path -Parent ([IO.Path]::GetFullPath($EvidencePath))
    if (-not (Test-Path -LiteralPath $directory)) { New-Item -ItemType Directory -Path $directory -Force | Out-Null }
    [IO.File]::WriteAllText([IO.Path]::GetFullPath($EvidencePath), $json, [Text.UTF8Encoding]::new($false))
}
$json
