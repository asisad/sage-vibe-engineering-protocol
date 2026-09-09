Set-StrictMode -Version Latest
$root = Split-Path -Parent $PSScriptRoot
Import-Module (Join-Path $root 'runtime\production\SageAdapters.psm1') -Force

$providerPath = Join-Path $root 'fixtures\v0.8\registries\provider-adapter.json'
$toolPath = Join-Path $root 'fixtures\v0.8\registries\tool-descriptor.json'
$provider = Import-SageAdapterRegistry -Path $providerPath
$tool = Get-Content -Raw -LiteralPath $toolPath | ConvertFrom-Json -Depth 100
$checks = 0; $failures = 0
function Assert-Sage([bool]$Condition,[string]$Name) { $script:checks++; if (-not $Condition) { $script:failures++; throw "FAIL: $Name" } }
Assert-Sage ((Test-SageAdapterRegistry -Adapter $provider -Tool $tool).valid) 'registry contract'
$req = [pscustomobject]@{ authority=[pscustomobject]@{ status='GRANTED'; scope=@('read:schemas','read:fixtures') }; task_id='task.adapter.mock' }
$plan = New-SageInvocationPlan -Adapter $provider -Tool $tool -Request $req
Assert-Sage ($plan.mode -eq 'DRY_RUN') 'default dry run'
Assert-Sage ($plan.allowed -eq $true) 'granted scope accepted'
$receipt = Invoke-SageAdapter -Plan $plan
Assert-Sage ($receipt.executed -eq $false -and $receipt.status -eq 'PLANNED') 'no side effect'
$denied = $req | Select-Object *
$denied.authority = [pscustomobject]@{ status='DENIED'; scope=@() }
$deniedPlan = New-SageInvocationPlan -Adapter $provider -Tool $tool -Request $denied
Assert-Sage ($deniedPlan.allowed -eq $false) 'denied authority rejected'
Assert-Sage ($deniedPlan.reasons -contains 'request authority is not GRANTED') 'denial reason preserved'
Write-Output ([pscustomobject]@{ status=if ($failures -eq 0) { 'PASS' } else { 'FAIL' }; checks=$checks; failures=$failures; live_execution=$false; external_target_contacted=$false } | ConvertTo-Json -Compress)
