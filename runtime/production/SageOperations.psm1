Set-StrictMode -Version Latest

function Test-SageDeploymentContract {
    param([Parameter(Mandatory)]$Contract)
    $required = @('deployment_id','artifact_ref','provider','environment','trigger','gates','rollback_ref')
    $missing = @($required | Where-Object { -not $Contract.PSObject.Properties[$_] -or [string]::IsNullOrWhiteSpace([string]$Contract.$_) })
    $issues = [System.Collections.Generic.List[string]]::new()
    foreach ($field in $missing) { $issues.Add("missing deployment field: $field") }
    if (@($Contract.gates).Count -lt 1) { $issues.Add('deployment requires operations gates') }
    if ($Contract.environment -in @('STAGING','PRODUCTION') -and [string]::IsNullOrWhiteSpace([string]$Contract.image_digest)) { $issues.Add('staging/production requires image_digest') }
    [pscustomobject]@{ valid=($issues.Count -eq 0); issues=@($issues); deployment_id=[string]$Contract.deployment_id }
}

function New-SageDeploymentPlan {
    param([Parameter(Mandatory)]$Contract,[ValidateSet('DRY_RUN','LIVE')][string]$Mode='DRY_RUN')
    if ($Mode -ne 'DRY_RUN') { throw 'Live deployment is disabled by the reference production boundary.' }
    $check = Test-SageDeploymentContract $Contract
    [pscustomobject]@{ plan_type='sage-deployment-plan'; plan_id="deploy-plan.$([guid]::NewGuid().ToString('N'))"; mode=$Mode; valid=$check.valid; issues=@($check.issues); provider=[string]$Contract.provider; environment=[string]$Contract.environment; artifact_ref=[string]$Contract.artifact_ref; rollback_ref=[string]$Contract.rollback_ref; gates=@($Contract.gates); external_execution=$false; created_at=[DateTime]::UtcNow.ToString('o') }
}

function Invoke-SageDeployment {
    param([Parameter(Mandatory)]$Plan)
    if ($Plan.mode -ne 'DRY_RUN') { throw 'Only DRY_RUN is supported.' }
    [pscustomobject]@{ status=if ($Plan.valid) { 'PLANNED' } else { 'BLOCKED' }; executed=$false; plan_id=$Plan.plan_id; provider=$Plan.provider; environment=$Plan.environment; gates=@($Plan.gates); issues=@($Plan.issues); evidence_kind='deployment-dry-run'; recorded_at=[DateTime]::UtcNow.ToString('o') }
}

Export-ModuleMember -Function Test-SageDeploymentContract,New-SageDeploymentPlan,Invoke-SageDeployment
