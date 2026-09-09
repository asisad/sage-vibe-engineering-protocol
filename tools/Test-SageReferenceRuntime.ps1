[CmdletBinding()]
param([string]$Root)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($Root)) { $Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path) }
Import-Module (Join-Path $Root 'runtime\reference\SageReference.psm1') -Force
$fixture = Read-SageJson (Join-Path $Root 'fixtures\v0.8\architecture-model.json')
$check = Test-SageArchitectureModel $fixture
if (-not $check.valid) { throw "Fixture semantic check failed: $($check.errors -join '; ')" }
$observed = $fixture | ConvertTo-Json -Depth 100 | ConvertFrom-Json -Depth 100 -DateKind String
$observed.model_version = 'observed.2026.09.09.1'
$observed.relationships = @($observed.relationships) + [pscustomobject]@{ relationship_id='rel.observed.direct-db'; from='system.checkout'; to='database.orders'; kind='reads'; authority='OBSERVED'; provenance=[pscustomobject]@{ source='sens'; observed_at='2026-09-09T10:30:00Z' } }
$comparison = Compare-SageArchitectureModels -Approved $fixture -Observed $observed
if ($comparison.status -ne 'NOT_CONVERGED') { throw 'Expected material unexpected runtime relationship to block convergence.' }
if (@($comparison.findings).Count -ne 1) { throw 'Expected exactly one drift finding.' }
[pscustomobject]@{ status='PASS'; model_valid=$check.valid; planned_observed=$comparison.status; findings=@($comparison.findings).Count } | ConvertTo-Json -Depth 10
