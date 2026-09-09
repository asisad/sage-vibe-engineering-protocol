Set-StrictMode -Version Latest
Import-Module (Join-Path $PSScriptRoot 'SageProduction.psm1') -Force
Import-Module (Join-Path (Split-Path $PSScriptRoot -Parent) 'reference\SageDiscovery.psm1') -Force

function Invoke-SageLifecycle {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]$RunContract,
        [Parameter(Mandatory)][string]$RegistryPath,
        [Parameter(Mandatory)][string]$LedgerPath,
        [string[]]$RequiredCapabilities = @('json-schema-validation'),
        [ValidateSet('READ_ONLY','ADAPTER_ONLY')][string]$MaxSideEffect = 'READ_ONLY'
    )
    $engine = New-SageProductionEngine -LedgerPath $LedgerPath
    $ledger = [pscustomobject]@{ ledger_id="lifecycle.$($RunContract.run_id)"; run_id=[string]$RunContract.run_id; entries=@(); chain_head=''; status='OPEN' }
    $stages = [System.Collections.Generic.List[object]]::new()
    function RecordStage([string]$Name,[string]$Status,[string]$Ref) {
        $script:unused = $null
        $entry = Add-SageProductionLedgerEntry -Ledger $ledger -Kind $Name.ToUpperInvariant() -Status $Status -Ref $Ref
        $stages.Add([pscustomobject]@{stage=$Name;status=$Status;ref=$Ref})
        return $entry
    }
    RecordStage 'intake' 'PASS' 'lifecycle://intake' | Out-Null
    if ([string]::IsNullOrWhiteSpace([string]$RunContract.run_id) -or [string]::IsNullOrWhiteSpace([string]$RunContract.task_packet.task_id)) { RecordStage 'intake' 'FAIL' 'contract://missing-identity' | Out-Null; $ledger.status='BLOCKED'; Save-SageProductionLedger $ledger $LedgerPath | Out-Null; return [pscustomobject]@{status='BLOCKED';final_stage='intake';stages=@($stages);ledger_path=$LedgerPath;external_execution='NOT_PERFORMED'} }
    $registry = Import-SageRegistrySet -Path $RegistryPath
    $discovery = Find-SageCapabilities -Registry $registry -RequiredCapabilities $RequiredCapabilities -MaxSideEffect $MaxSideEffect
    RecordStage 'discover' 'PASS' "discovery://$($discovery.match_count)-matches" | Out-Null
    if ($discovery.match_count -eq 0) { RecordStage 'plan' 'FAIL' 'plan://no-safe-capability' | Out-Null; $ledger.status='BLOCKED'; Save-SageProductionLedger $ledger $LedgerPath | Out-Null; return [pscustomobject]@{status='BLOCKED';final_stage='plan';stages=@($stages);discovery=$discovery;ledger_path=$LedgerPath;external_execution='NOT_PERFORMED'} }
    $plan = [pscustomobject]@{plan_type='sage.lifecycle.plan';mode='DRY_RUN';selected_capabilities=@($discovery.matches|ForEach-Object id);required_capabilities=@($RequiredCapabilities);created_at=[DateTime]::UtcNow.ToString('o')}
    RecordStage 'plan' 'PASS' 'plan://dry-run' | Out-Null
    $implementation = [pscustomobject]@{status='PLANNED';executed=$false;mode='DRY_RUN';mutations=0;external_execution='NOT_PERFORMED';receipt='implementation://dry-run'}
    RecordStage 'implement' 'PASS' $implementation.receipt | Out-Null
    $verify = ($implementation.status -eq 'PLANNED' -and $implementation.executed -eq $false -and $ledger.entries.Count -ge 4)
    RecordStage 'verify' $(if($verify){'PASS'}else{'FAIL'}) 'verification://lifecycle-evidence' | Out-Null
    if ($verify) { $ledger.status='SEALED'; $status='DONE' } else { $ledger.status='BLOCKED'; $status='BLOCKED' }
    Save-SageProductionLedger $ledger $LedgerPath | Out-Null
    [pscustomobject]@{status=$status;final_stage='verify';stages=@($stages);plan=$plan;discovery=$discovery;implementation=$implementation;ledger_path=$LedgerPath;ledger_chain_head=$ledger.chain_head;ledger_status=$ledger.status;external_execution='NOT_PERFORMED'}
}

Export-ModuleMember -Function Invoke-SageLifecycle
