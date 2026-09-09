[CmdletBinding()]
param([string]$Root)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
if ([string]::IsNullOrWhiteSpace($Root)) {$Root=Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)}
Import-Module (Join-Path $Root 'runtime\reference\SageDiscovery.psm1') -Force
$registry=Import-SageRegistrySet -Path (Join-Path $Root 'fixtures\v0.8\registries')
$found=Find-SageCapabilities -Registry $registry -RequiredCapabilities @('json-schema-validation') -MaxSideEffect READ_ONLY
if ($registry.count -ne 3 -or $found.match_count -lt 1) { throw 'Capability discovery failed.' }
$none=Find-SageCapabilities -Registry $registry -RequiredCapabilities @('capability-that-does-not-exist')
if ($none.match_count -ne 0) { throw 'Unknown capability must return no matches.' }
[pscustomobject]@{status='PASS'; registry_records=$registry.count; read_matches=$found.match_count; unknown_matches=$none.match_count} | ConvertTo-Json -Depth 10
