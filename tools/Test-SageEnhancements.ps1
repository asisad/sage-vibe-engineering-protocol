[CmdletBinding()]
param([string]$Root)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($Root)) { $Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path) }
$schema = Get-Content -Raw -LiteralPath (Join-Path $Root 'schemas\v0.8.1\sage-enhancements.schema.json') | ConvertFrom-Json -Depth 100
$policy = Get-Content -Raw -LiteralPath (Join-Path $Root 'policies\v0.8.1\agentic-engineering-policy.json') | ConvertFrom-Json -Depth 100
$passes = [System.Collections.Generic.List[string]]::new()
$failures = [System.Collections.Generic.List[string]]::new()
function Assert([bool]$Condition, [string]$Message) { if ($Condition) { $passes.Add($Message) } else { $failures.Add($Message) } }
Assert ($schema.'$schema' -eq 'https://json-schema.org/draft/2020-12/schema') 'Enhancement schema declares JSON Schema 2020-12.'
Assert ($policy.context.minimum_relevant_only -eq $true) 'Context policy requires minimum relevant context.'
Assert ($policy.workflow.sage_gates_wrap_adapter -eq $true) 'Workflow adapters remain wrapped by SAGE gates.'
Assert ($policy.sensors.authority_from_sensor -eq $false) 'Sensors cannot grant authority.'
Assert ($policy.evaluation.trajectory_required -eq $true) 'Agent trajectory evidence is required.'
Assert ($policy.ai_ssdf.secret_redaction -eq $true) 'AI-SSDF policy requires secret redaction.'
$fixtureRoot = Join-Path $Root 'fixtures\v0.8.1'
$files = Get-ChildItem -LiteralPath $fixtureRoot -Filter '*.json' -File
Assert ($files.Count -eq 5) 'Five enhancement fixtures are present.'
foreach ($file in $files) {
    try { $doc = Get-Content -Raw -LiteralPath $file.FullName | ConvertFrom-Json -Depth 100; Assert ($null -ne $doc) "$($file.Name) parses as JSON." }
    catch { $failures.Add("$($file.Name) JSON parse failed: $($_.Exception.Message)") }
}
if ($failures.Count -gt 0) { $failures | ForEach-Object { Write-Error $_ }; exit 1 }
[pscustomobject]@{ status='PASS'; checks=@($passes); fixture_count=$files.Count } | ConvertTo-Json -Depth 10
