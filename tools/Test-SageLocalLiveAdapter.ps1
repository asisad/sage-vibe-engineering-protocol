[CmdletBinding()]
param([string]$Root)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
if ([string]::IsNullOrWhiteSpace($Root)) {$Root=Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)}
Import-Module (Join-Path $Root 'runtime\production\SageAdapters.psm1') -Force
$result = Invoke-SageLocalReferenceAdapter -Root $Root -RelativePath 'fixtures\v0.8\architecture-model.json'
if ($result.status -ne 'COMPLETED' -or $result.executed -ne $true -or $result.network -ne 'NONE' -or $result.mutation -ne 'NONE') { throw 'Local live adapter proof failed.' }
$escaped=$false
try { Invoke-SageLocalReferenceAdapter -Root $Root -RelativePath '..\SAGE_v0.7_MASTER_BASELINE.md' | Out-Null } catch { $escaped=$true }
if (-not $escaped) { throw 'Root escape must be rejected.' }
[pscustomobject]@{status='PASS'; live_execution=$result.executed; target=$result.target; sha256=$result.sha256; network=$result.network; mutation=$result.mutation; escape_rejected=$escaped} | ConvertTo-Json -Depth 10
