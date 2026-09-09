Set-StrictMode -Version Latest

$script:SageStates = @('INTAKE','CLARIFYING','CLASSIFIED','PLANNED','AUTHORIZED','EXECUTING','VERIFYING','CONVERGING','DONE','BLOCKED','ESCALATED')
$script:SageTransitions = @{
    INTAKE=@('CLARIFYING','CLASSIFIED'); CLARIFYING=@('CLASSIFIED','BLOCKED'); CLASSIFIED=@('PLANNED','ESCALATED'); PLANNED=@('AUTHORIZED','BLOCKED','ESCALATED'); AUTHORIZED=@('EXECUTING','BLOCKED','ESCALATED'); EXECUTING=@('VERIFYING','BLOCKED','ESCALATED'); VERIFYING=@('CONVERGING','BLOCKED','ESCALATED'); CONVERGING=@('DONE','EXECUTING','BLOCKED','ESCALATED'); DONE=@(); BLOCKED=@('PLANNED','ESCALATED'); ESCALATED=@('PLANNED','BLOCKED')
}

function New-SageEvidenceLedger {
    param([Parameter(Mandatory)][string]$RunId)
    [pscustomobject]@{ ledger_id="ledger.$RunId"; run_id=$RunId; entries=@(); status='OPEN'; chain_head='' }
}

function Add-SageEvidence {
    param([Parameter(Mandatory)]$Ledger, [Parameter(Mandatory)][string]$EvidenceId, [Parameter(Mandatory)][string]$Kind, [Parameter(Mandatory)][string]$Status, [Parameter(Mandatory)][string]$Ref)
    if (@($Ledger.entries | Where-Object { $_.evidence_id -eq $EvidenceId }).Count -gt 0) { throw "Duplicate evidence_id: $EvidenceId" }
    $entry = [pscustomobject]@{ evidence_id=$EvidenceId; kind=$Kind; status=$Status; ref=$Ref; recorded_at=[DateTime]::UtcNow.ToString('o') }
    $payload = $entry | ConvertTo-Json -Depth 20 -Compress
    $entry | Add-Member -NotePropertyName content_sha256 -NotePropertyValue ([Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($payload))).ToLower())
    $Ledger.entries = @($Ledger.entries) + $entry
    $headPayload = ($Ledger.entries | ConvertTo-Json -Depth 30 -Compress)
    $Ledger.chain_head = ([Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($headPayload))).ToLower())
    return $Ledger
}

function Save-SageEvidenceLedger {
    param([Parameter(Mandatory)]$Ledger, [Parameter(Mandatory)][string]$Path)
    $parent = Split-Path -Parent $Path
    if ($parent -and -not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
    $Ledger | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $Path -Encoding utf8
    return $Path
}

function Read-SageEvidenceLedger {
    param([Parameter(Mandatory)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Evidence ledger not found: $Path" }
    Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json -Depth 100 -DateKind String
}

function Invoke-SageWorkflow {
    param([Parameter(Mandatory)]$RunContract, [Parameter(Mandatory)]$Ledger)
    $state = 'INTAKE'; $history = [System.Collections.Generic.List[object]]::new()
    $history.Add([pscustomobject]@{ state=$state; at=[DateTime]::UtcNow.ToString('o') })
    $next = if ($RunContract.task_packet.request_type -eq 'QUESTION') { 'CLARIFYING' } else { 'CLASSIFIED' }
    $transition = Move-SageRunState -CurrentState $state -NextState $next
    $state = $transition.state; $history.Add([pscustomobject]@{ state=$state; at=[DateTime]::UtcNow.ToString('o') })
    $evaluation = Invoke-SageRunEvaluation $RunContract
    $final = if ($evaluation.decision -eq 'DONE') { 'DONE' } elseif ($evaluation.decision -eq 'ESCALATE') { 'ESCALATED' } else { 'BLOCKED' }
    $history.Add([pscustomobject]@{ state=$final; at=[DateTime]::UtcNow.ToString('o') })
    [pscustomobject]@{ run_id=$evaluation.run_id; workflow_history=@($history); decision=$evaluation.decision; final_state=$final; evaluation=$evaluation; ledger_id=$Ledger.ledger_id }
}

function Test-SageEvidenceCoverage {
    param([Parameter(Mandatory)]$Ledger, [Parameter(Mandatory)][string[]]$RequiredEvidenceIds)
    $ids=@($Ledger.entries | ForEach-Object { [string]$_.evidence_id }); $missing=@($RequiredEvidenceIds | Where-Object { $ids -notcontains $_ }); $failed=@($Ledger.entries | Where-Object { $_.status -notin @('PASS','ACCEPTED') })
    [pscustomobject]@{ complete=($missing.Count -eq 0 -and $failed.Count -eq 0); missing=@($missing); failed=@($failed | ForEach-Object { $_.evidence_id }) }
}

function Move-SageRunState {
    param([Parameter(Mandatory)][string]$CurrentState, [Parameter(Mandatory)][string]$NextState)
    if ($script:SageStates -notcontains $CurrentState -or $script:SageStates -notcontains $NextState) { throw 'Unknown SAGE workflow state.' }
    if (@($script:SageTransitions[$CurrentState]) -notcontains $NextState) { throw "Illegal workflow transition: $CurrentState -> $NextState" }
    [pscustomobject]@{ previous_state=$CurrentState; state=$NextState; transition="${CurrentState}->${NextState}" }
}

function Invoke-SageRunEvaluation {
    param([Parameter(Mandatory)]$RunContract)
    $reasons = [System.Collections.Generic.List[string]]::new()
    if ($RunContract.record_type -ne 'sage_run_contract') { $reasons.Add('invalid run contract record_type') }
    if ($RunContract.task_packet.task_id -ne $RunContract.risk_assessment.task_id -or $RunContract.task_packet.task_id -ne $RunContract.gate_plan.task_id) { $reasons.Add('task identity mismatch') }
    $activeBlocking = @($RunContract.gate_plan.gates | Where-Object { $_.state -eq 'ACTIVE' -and $_.blocking -eq $true })
    foreach ($gate in $activeBlocking) {
        if ([string]$gate.status -ne 'PASS') { $reasons.Add("blocking gate not passed: $($gate.gate_id)") }
        if (@($gate.evidence_required).Count -eq 0) { $reasons.Add("blocking gate lacks evidence requirement: $($gate.gate_id)") }
    }
    if ($RunContract.task_packet.authority.status -eq 'GRANTED' -and @($RunContract.task_packet.authority.scope).Count -eq 0) { $reasons.Add('granted authority has empty scope') }
    $decision = if ($reasons.Count -eq 0) { 'DONE' } elseif ($RunContract.risk_assessment.risk_level -in @('R3','R4')) { 'ESCALATE' } else { 'BLOCKED' }
    [pscustomobject]@{ run_id=[string]$RunContract.run_id; task_id=[string]$RunContract.task_packet.task_id; risk_level=[string]$RunContract.risk_assessment.risk_level; decision=$decision; blocking_gate_count=$activeBlocking.Count; reasons=@($reasons) }
}

Export-ModuleMember -Function Invoke-SageRunEvaluation
Export-ModuleMember -Function New-SageEvidenceLedger, Add-SageEvidence, Test-SageEvidenceCoverage, Move-SageRunState, Save-SageEvidenceLedger, Read-SageEvidenceLedger, Invoke-SageWorkflow
