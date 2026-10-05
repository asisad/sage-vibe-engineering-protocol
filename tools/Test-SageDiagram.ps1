[CmdletBinding()]
param([string]$Root)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($Root)) { $Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path) }
$diagram = Join-Path $Root 'docs\diagrams\sage-architecture.mmd'
$readme = Join-Path $Root 'docs\diagrams\README.md'
$passes = [System.Collections.Generic.List[string]]::new()
$failures = [System.Collections.Generic.List[string]]::new()
function Assert([bool]$Condition, [string]$Message) { if ($Condition) { $passes.Add($Message) } else { $failures.Add($Message) } }
Assert (Test-Path -LiteralPath $diagram) 'Architecture Mermaid source exists.'
Assert (Test-Path -LiteralPath $readme) 'Diagram README exists.'
$source = Get-Content -Raw -LiteralPath $diagram
foreach ($stage in @('INTAKE','DISCOVER','PLAN','IMPLEMENT','VERIFY','Evidence Ledger','Authority & Scope Gates','Provider / Tool / Skill Registry','Strix Security Adapter')) {
    Assert ($source.Contains($stage)) "Diagram includes $stage."
}
Assert ($source.Contains('Context & Memory')) 'Diagram includes scoped Context & Memory boundary.'
Assert ($source.Contains('minimum sufficient context')) 'Diagram documents minimum-sufficient context loading.'
foreach ($edge in @('intake --> discover','discover --> plan','plan --> implement','implement --> verify','verify --> outcome')) {
    Assert ($source.Contains($edge)) "Diagram includes lifecycle edge: $edge."
}
Assert ($source.Contains('opt-in boundary')) 'Diagram marks external adapters as opt-in.'
foreach ($edge in @('interfaces -. constrains .-> registry','callable -. optional transport .-> bridge','callable -. direct native binding .-> api')) {
    Assert ($source.Contains($edge)) "Diagram includes Agent-Native relationship: $edge."
}
Assert ($source.Contains('target-specific conformance')) 'Diagram discloses target-specific transport coverage.'
if ($failures.Count -gt 0) { $failures | ForEach-Object { Write-Error $_ }; exit 1 }
[pscustomobject]@{ status='PASS'; checks=@($passes) } | ConvertTo-Json -Depth 10
