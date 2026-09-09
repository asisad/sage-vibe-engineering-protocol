[CmdletBinding()]
param([string]$Root)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
if ([string]::IsNullOrWhiteSpace($Root)) {$Root=Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)}
Import-Module (Join-Path $Root 'runtime\reference\SageDemonstrator.psm1') -Force
$request=Get-Content -Raw -LiteralPath (Join-Path $Root 'fixtures\v0.8\demonstrator-gps-map-request.json') | ConvertFrom-Json -Depth 100 -DateKind String
$result=Invoke-SageDemonstrator $request
if ($result.status -ne 'CLARIFY_REQUIRED' -or $result.risk_level -ne 'R2') { throw 'Demonstrator must stop for clarification at R2.' }
if (@($result.clarification.questions).Count -ne 4) { throw 'All declared unknowns must become clarification questions.' }
if ($result.architecture.source_of_truth -ne 'approved_model') { throw 'Architecture source of truth was not preserved.' }
if ($result.routing.external_execution -ne 'NOT_AUTHORIZED') { throw 'External execution must remain unauthorized.' }
[pscustomobject]@{status='PASS'; request=$result.request_id; state=$result.status; risk=$result.risk_level; questions=@($result.clarification.questions).Count; stages=@($result.plan.stages).Count; agents=@($result.routing.agents).Count; tools=@($result.routing.tools).Count; external_execution=$result.routing.external_execution} | ConvertTo-Json -Depth 10
