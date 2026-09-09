[CmdletBinding()]
param([string]$Root)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($Root)) { $Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path) }
Import-Module (Join-Path $Root 'runtime\reference\SageOrchestrator.psm1') -Force
$run = Get-Content -Raw -LiteralPath (Join-Path $Root 'fixtures\v0.8\r2-feature-data-path.json') | ConvertFrom-Json -Depth 100 -DateKind String
$done = Invoke-SageRunEvaluation $run
if ($done.decision -ne 'DONE') { throw "Expected DONE for passing R2 fixture, got $($done.decision)" }
$blockedRun = $run | ConvertTo-Json -Depth 100 | ConvertFrom-Json -Depth 100 -DateKind String
$blockedRun.gate_plan.gates[0].status = 'FAIL'
$blocked = Invoke-SageRunEvaluation $blockedRun
if ($blocked.decision -ne 'BLOCKED' -or @($blocked.reasons).Count -eq 0) { throw 'Expected BLOCKED with a reason for failed blocking gate.' }
$ledger = New-SageEvidenceLedger -RunId $run.run_id
$ledger = Add-SageEvidence -Ledger $ledger -EvidenceId 'ev.build' -Kind 'build' -Status 'PASS' -Ref 'test://build'
$ledger = Add-SageEvidence -Ledger $ledger -EvidenceId 'ev.acceptance' -Kind 'acceptance' -Status 'PASS' -Ref 'test://acceptance'
$coverage = Test-SageEvidenceCoverage -Ledger $ledger -RequiredEvidenceIds @('ev.build','ev.acceptance')
if (-not $coverage.complete) { throw 'Expected complete evidence ledger.' }
$transition = Move-SageRunState -CurrentState 'VERIFYING' -NextState 'CONVERGING'
if ($transition.state -ne 'CONVERGING') { throw 'Expected legal VERIFYING -> CONVERGING transition.' }
$illegalCaught = $false
try { Move-SageRunState -CurrentState 'INTAKE' -NextState 'DONE' | Out-Null } catch { $illegalCaught = $true }
if (-not $illegalCaught) { throw 'Expected illegal workflow transition to be rejected.' }
$ledgerPath = Join-Path $Root 'tmp\reference-ledger-test.json'
Save-SageEvidenceLedger -Ledger $ledger -Path $ledgerPath | Out-Null
$loadedLedger = Read-SageEvidenceLedger -Path $ledgerPath
if ($loadedLedger.chain_head -ne $ledger.chain_head) { throw 'Evidence ledger chain head did not persist.' }
$workflow = Invoke-SageWorkflow -RunContract $run -Ledger $ledger
if ($workflow.final_state -ne 'DONE') { throw 'Expected workflow to finish in DONE for passing fixture.' }
[pscustomobject]@{ status='PASS'; passing_decision=$done.decision; failed_gate_decision=$blocked.decision; reasons=@($blocked.reasons).Count; evidence_complete=$coverage.complete; legal_transition=$transition.transition; illegal_transition_rejected=$illegalCaught; ledger_persisted=($loadedLedger.chain_head -eq $ledger.chain_head); workflow_final_state=$workflow.final_state } | ConvertTo-Json -Depth 10
