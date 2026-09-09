Set-StrictMode -Version Latest

$script:States = @('INTAKE','CLARIFYING','CLASSIFIED','PLANNED','AUTHORIZED','EXECUTING','VERIFYING','CONVERGING','DONE','BLOCKED','ESCALATED')
$script:Transitions = @{
    INTAKE=@('CLARIFYING','CLASSIFIED'); CLARIFYING=@('CLASSIFIED','BLOCKED'); CLASSIFIED=@('PLANNED','ESCALATED');
    PLANNED=@('AUTHORIZED','BLOCKED','ESCALATED'); AUTHORIZED=@('EXECUTING','BLOCKED','ESCALATED');
    EXECUTING=@('VERIFYING','BLOCKED','ESCALATED'); VERIFYING=@('CONVERGING','BLOCKED','ESCALATED');
    CONVERGING=@('DONE','EXECUTING','BLOCKED','ESCALATED'); DONE=@(); BLOCKED=@('PLANNED','ESCALATED'); ESCALATED=@('PLANNED','BLOCKED')
}

function Get-SageProductionHash([string]$Text) {
    ([Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($Text)))).ToLower()
}

function New-SageProductionEngine {
    param([Parameter(Mandatory)][string]$LedgerPath)
    $parent = Split-Path -Parent $LedgerPath
    if ($parent -and -not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
    [pscustomobject]@{ engine_id='sage.production.reference'; mode='CONTROLLED_NO_EXTERNAL_EXECUTION'; ledger_path=$LedgerPath; providers=@(); tools=@(); runs=@() }
}

function Register-SageProductionProvider {
    param([Parameter(Mandatory)]$Engine,[Parameter(Mandatory)]$Descriptor)
    if ([string]::IsNullOrWhiteSpace([string]$Descriptor.provider_id)) { throw 'Provider descriptor requires provider_id.' }
    if (@($Engine.providers | Where-Object provider_id -eq $Descriptor.provider_id).Count -gt 0) { throw "Duplicate provider: $($Descriptor.provider_id)" }
    if ([string]$Descriptor.execution_policy -ne 'ADAPTER_ONLY') { throw 'Production provider must use ADAPTER_ONLY execution policy.' }
    $Engine.providers = @($Engine.providers) + $Descriptor
    $Engine
}

function Register-SageProductionTool {
    param([Parameter(Mandatory)]$Engine,[Parameter(Mandatory)]$Descriptor)
    if ([string]::IsNullOrWhiteSpace([string]$Descriptor.tool_id)) { throw 'Tool descriptor requires tool_id.' }
    if (@($Engine.tools | Where-Object tool_id -eq $Descriptor.tool_id).Count -gt 0) { throw "Duplicate tool: $($Descriptor.tool_id)" }
    if ([string]$Descriptor.execution_policy -ne 'ADAPTER_ONLY') { throw 'Production tool must use ADAPTER_ONLY execution policy.' }
    $Engine.tools = @($Engine.tools) + $Descriptor
    $Engine
}

function Move-SageProductionState {
    param([Parameter(Mandatory)][string]$Current,[Parameter(Mandatory)][string]$Next)
    if ($script:States -notcontains $Current -or $script:States -notcontains $Next) { throw 'Unknown SAGE state.' }
    if (@($script:Transitions[$Current]) -notcontains $Next) { throw "Illegal transition: $Current -> $Next" }
    [pscustomobject]@{ previous_state=$Current; state=$Next; transition="$Current->$Next"; at=[DateTime]::UtcNow.ToString('o') }
}

function Add-SageProductionLedgerEntry {
    param([Parameter(Mandatory)]$Ledger,[Parameter(Mandatory)][string]$Kind,[Parameter(Mandatory)][string]$Status,[Parameter(Mandatory)][string]$Ref)
    $entry = [ordered]@{ entry_id="led.$($Ledger.entries.Count + 1).$([Guid]::NewGuid().ToString('N').Substring(0,8))"; kind=$Kind; status=$Status; ref=$Ref; recorded_at=[DateTime]::UtcNow.ToString('o') }
    $entry.content_sha256 = Get-SageProductionHash (($entry | ConvertTo-Json -Compress -Depth 20))
    $Ledger.entries = @($Ledger.entries) + [pscustomobject]$entry
    $Ledger.chain_head = Get-SageProductionHash (($Ledger.entries | ConvertTo-Json -Compress -Depth 30))
    $Ledger
}

function Save-SageProductionLedger {
    param([Parameter(Mandatory)]$Ledger,[Parameter(Mandatory)][string]$Path)
    $tmp = "$Path.$([Guid]::NewGuid().ToString('N')).tmp"
    $Ledger | ConvertTo-Json -Depth 40 | Set-Content -LiteralPath $tmp -Encoding utf8
    Move-Item -LiteralPath $tmp -Destination $Path -Force
    $Path
}

function Invoke-SageProductionRun {
    param([Parameter(Mandatory)]$Engine,[Parameter(Mandatory)]$RunContract)
    $runId = [string]$RunContract.run_id
    $ledger = [pscustomobject]@{ ledger_id="production.$runId"; run_id=$runId; entries=@(); chain_head=''; status='OPEN' }
    $history = [System.Collections.Generic.List[object]]::new()
    $state = 'INTAKE'; $history.Add([pscustomobject]@{state=$state;at=[DateTime]::UtcNow.ToString('o')})
    $record = Add-SageProductionLedgerEntry $ledger 'STATE' 'PASS' 'state://INTAKE'
    $identity = [string]$RunContract.task_packet.task_id -eq [string]$RunContract.risk_assessment.task_id -and [string]$RunContract.task_packet.task_id -eq [string]$RunContract.gate_plan.task_id
    if (-not $identity) { $state='BLOCKED'; $record=Add-SageProductionLedgerEntry $ledger 'IDENTITY' 'FAIL' 'contract://task-identity'; $history.Add([pscustomobject]@{state=$state;at=[DateTime]::UtcNow.ToString('o')}) }
    else {
        foreach ($next in @('CLASSIFIED','PLANNED','AUTHORIZED','EXECUTING','VERIFYING','CONVERGING')) { $state=(Move-SageProductionState $state $next).state; $history.Add([pscustomobject]@{state=$state;at=[DateTime]::UtcNow.ToString('o')}); $record=Add-SageProductionLedgerEntry $ledger 'STATE' 'PASS' "state://$state" }
        $gates=@($RunContract.gate_plan.gates | Where-Object {$_.state -eq 'ACTIVE' -and $_.blocking -eq $true})
        $failed=@($gates | Where-Object {[string]$_.status -ne 'PASS'})
        if ($failed.Count -gt 0) { $state=(Move-SageProductionState $state 'BLOCKED').state; $record=Add-SageProductionLedgerEntry $ledger 'GATE' 'FAIL' 'gate://blocking'; $history.Add([pscustomobject]@{state=$state;at=[DateTime]::UtcNow.ToString('o')}) }
        elseif ([string]$RunContract.task_packet.authority.status -ne 'GRANTED' -or @($RunContract.task_packet.authority.scope).Count -eq 0) { $state=(Move-SageProductionState $state 'ESCALATED').state; $record=Add-SageProductionLedgerEntry $ledger 'AUTHORITY' 'FAIL' 'authority://missing-or-empty'; $history.Add([pscustomobject]@{state=$state;at=[DateTime]::UtcNow.ToString('o')}) }
        else { $state=(Move-SageProductionState $state 'DONE').state; $record=Add-SageProductionLedgerEntry $ledger 'COMPLETION' 'PASS' 'completion://gates-and-authority'; $history.Add([pscustomobject]@{state=$state;at=[DateTime]::UtcNow.ToString('o')}); $ledger.status='SEALED' }
    }
    Save-SageProductionLedger $ledger $Engine.ledger_path | Out-Null
    $result=[pscustomobject]@{run_id=$runId;final_state=$state;decision=if($state -eq 'DONE'){'DONE'}elseif($state -eq 'ESCALATED'){'ESCALATE'}else{'BLOCKED'};workflow_history=@($history);ledger_id=$ledger.ledger_id;ledger_chain_head=$ledger.chain_head;external_execution='NOT_PERFORMED';providers_registered=@($Engine.providers).Count;tools_registered=@($Engine.tools).Count}
    $Engine.runs=@($Engine.runs)+$result; $result
}

Export-ModuleMember -Function New-SageProductionEngine,Register-SageProductionProvider,Register-SageProductionTool,Move-SageProductionState,Add-SageProductionLedgerEntry,Save-SageProductionLedger,Invoke-SageProductionRun
