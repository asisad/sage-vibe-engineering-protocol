[CmdletBinding()]
param([string]$Root)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($Root)) { $Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path) }
$schema = Get-Content -Raw -LiteralPath (Join-Path $Root 'schemas\v0.8.2\sage-operations.schema.json') | ConvertFrom-Json -Depth 100
$policy = Get-Content -Raw -LiteralPath (Join-Path $Root 'policies\v0.8.2\production-operations-policy.json') | ConvertFrom-Json -Depth 100
$passes = [System.Collections.Generic.List[string]]::new(); $failures = [System.Collections.Generic.List[string]]::new()
function Assert([bool]$Condition, [string]$Message) { if ($Condition) { $passes.Add($Message) } else { $failures.Add($Message) } }
Assert ($schema.'$schema' -eq 'https://json-schema.org/draft/2020-12/schema') 'Operations schema declares JSON Schema 2020-12.'
Assert ($policy.deployment.immutable_artifact_required -eq $true) 'Deployments require immutable artifacts.'
Assert ($policy.deployment.production_approval -eq 'HUMAN_REQUIRED') 'Production requires human approval.'
Assert ($policy.secrets.log_or_evidence -eq $false) 'Secrets are excluded from logs and evidence.'
Assert (@($policy.gates.required).Count -ge 5) 'Production gate set covers health, migration, backup, observability and rollback.'
$files = Get-ChildItem -LiteralPath (Join-Path $Root 'fixtures\v0.8.2') -Filter '*.json' -File
Assert ($files.Count -eq 4) 'Four operations fixtures are present.'
foreach ($file in $files) { try { Get-Content -Raw -LiteralPath $file.FullName | ConvertFrom-Json -Depth 100 | Out-Null; Assert $true "$($file.Name) parses as JSON." } catch { Assert $false "$($file.Name) parses as JSON." } }
if ($failures.Count -gt 0) { $failures | ForEach-Object { Write-Error $_ }; exit 1 }
[pscustomobject]@{ status='PASS'; checks=@($passes); fixture_count=$files.Count } | ConvertTo-Json -Depth 10
