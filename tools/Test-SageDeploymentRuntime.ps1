[CmdletBinding()]
param([string]$Root)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
if ([string]::IsNullOrWhiteSpace($Root)) { $Root=Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path) }
Import-Module (Join-Path $Root 'runtime\production\SageOperations.psm1') -Force
$contract=Get-Content -Raw -LiteralPath (Join-Path $Root 'fixtures\v0.8.2\deployment-contract.json') | ConvertFrom-Json -Depth 50
$plan=New-SageDeploymentPlan -Contract $contract
$receipt=Invoke-SageDeployment -Plan $plan
if (-not $plan.valid -or $receipt.status -ne 'PLANNED' -or $receipt.executed) { throw 'Deployment dry-run assertion failed.' }
$bad=$contract | ConvertTo-Json -Depth 50 | ConvertFrom-Json -Depth 50
$bad.rollback_ref=''
$badCheck=Test-SageDeploymentContract $bad
if ($badCheck.valid) { throw 'Invalid deployment contract was accepted.' }
[pscustomobject]@{ status='PASS'; plan_mode=$plan.mode; receipt_status=$receipt.status; external_execution=$receipt.executed; negative_case='BLOCKED' } | ConvertTo-Json -Depth 10
