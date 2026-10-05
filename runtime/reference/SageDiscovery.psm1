Set-StrictMode -Version Latest
Import-Module (Join-Path $PSScriptRoot 'SageAgentInterfaces.psm1') -Force

function Import-SageRegistrySet {
    param([Parameter(Mandatory)][string]$Path)
    $records = [System.Collections.Generic.List[object]]::new()
    foreach ($file in Get-ChildItem -LiteralPath $Path -Filter '*.json' -File) {
        $record = Get-Content -Raw -LiteralPath $file.FullName | ConvertFrom-Json -Depth 100 -DateKind String
        $type=if ($null -ne $record -and $record.PSObject.Properties['record_type']) { [string]$record.record_type } else { '<invalid>' }
        $records.Add([pscustomobject]@{ source=$file.FullName; record=$record; record_type=$type })
    }
    [pscustomobject]@{ registry_path=$Path; records=@($records); count=$records.Count }
}

function Get-SageSideEffectRank {
    param([Parameter(Mandatory)]$Record)
    if ($Record.record_type -eq 'agent_capability') { return 0 }
    if ($Record.record_type -eq 'provider_adapter') { return 1 }
    if ($Record.record_type -ne 'tool_descriptor' -or -not $Record.PSObject.Properties['side_effect_class']) { return $null }
    $rank = @{
        READ_ONLY = 0
        LOCAL_REVERSIBLE = 2
        LOCAL_DESTRUCTIVE = 3
        EXTERNAL_MUTATION = 3
        SECURITY_ACTIVE = 3
    }
    $sideEffect = [string]$Record.side_effect_class
    if (-not $rank.ContainsKey($sideEffect)) { return $null }
    return $rank[$sideEffect]
}

function Find-SageCapabilities {
    param([Parameter(Mandatory)]$Registry, [Parameter(Mandatory)][string[]]$RequiredCapabilities, [ValidateSet('READ_ONLY','ADAPTER_ONLY','MUTATING')][string]$MaxSideEffect='READ_ONLY')
    $maximumRank=@{ READ_ONLY=0; ADAPTER_ONLY=1; MUTATING=2 }; $matches=[System.Collections.Generic.List[object]]::new()
    $rejected=[System.Collections.Generic.List[object]]::new()
    $contractSchema=Join-Path $PSScriptRoot '..\..\schemas\v0.8\sage-contracts.schema.json'
    foreach ($item in @($Registry.records)) {
        $record=$item.record
        if ($null -eq $record -or -not $record.PSObject.Properties['record_type']) { $rejected.Add([pscustomobject]@{source=$item.source;reason='INVALID_DESCRIPTOR_INPUT'}); continue }
        if ($record.record_type -eq 'agent_native_interface') { continue }
        if ($record.record_type -notin @('agent_capability','provider_adapter','tool_descriptor')) { $rejected.Add([pscustomobject]@{source=$item.source;reason='UNSUPPORTED_RECORD_TYPE'}); continue }
        try { $valid=Test-Json -Json ($record | ConvertTo-Json -Depth 100 -Compress) -SchemaFile $contractSchema -ErrorAction SilentlyContinue } catch { $valid=$false }
        if (-not $valid) { $rejected.Add([pscustomobject]@{source=$item.source;reason='DESCRIPTOR_SCHEMA_INVALID'}); continue }
        $caps=@(); if ($record.PSObject.Properties['capabilities']) { $caps=@($record.capabilities) }; if ($record.record_type -eq 'tool_descriptor' -and $record.PSObject.Properties['operations']) { $caps=@($caps + $record.operations) }
        $missing=@($RequiredCapabilities | Where-Object { $caps -notcontains $_ })
        $side=[string]$(if ($record.PSObject.Properties['side_effect_class']) { $record.side_effect_class } elseif ($record.record_type -eq 'provider_adapter') { 'ADAPTER_ONLY' } else { 'READ_ONLY' })
        $sideEffectRank = Get-SageSideEffectRank $record
        $preserves=($record.PSObject.Properties['scope_preservation'] -and $record.scope_preservation -eq $true -and $record.permission_preservation -eq $true -and $record.authority_preservation -eq $true -and $record.evidence_preservation -eq $true)
        $resolvedId = if ($record.PSObject.Properties['adapter_id']) { $record.adapter_id } elseif ($record.PSObject.Properties['tool_id']) { $record.tool_id } else { $record.agent_id }
        if ($missing.Count -eq 0 -and $null -ne $sideEffectRank -and $sideEffectRank -le $maximumRank[$MaxSideEffect] -and ($record.record_type -ne 'provider_adapter' -or $preserves)) { $matches.Add([pscustomobject]@{ id=[string]$resolvedId; record_type=$record.record_type; capabilities=$caps; side_effect_class=$side; source=$item.source }) }
    }
    $interfaceItems=@($Registry.records | Where-Object { $null -ne $_.record -and $_.record.PSObject.Properties['record_type'] -and $_.record.record_type -eq 'agent_native_interface' })
    $interfaceSelection=Select-SageAgentInterface -Descriptors @($interfaceItems | ForEach-Object { $_.record }) -RequiredCapabilities $RequiredCapabilities -MaxSideEffect $MaxSideEffect
    foreach ($interface in @($interfaceSelection.candidates)) {
        $source=@($interfaceItems | Where-Object { $_.record.PSObject.Properties['interface_id'] -and $_.record.interface_id -eq $interface.interface_id })[0].source
        $matches.Add([pscustomobject]@{
            id=[string]$interface.interface_id; record_type='agent_native_interface'; capabilities=@($interface.capabilities)
            side_effect_class=[string]$interface.security.side_effect_class; source=$source
            callable_surface=[string]$interface.layers.callable_surface; decision=[string]$interface.decision
            authority_granted=$false; external_execution=$false
        })
    }
    [pscustomobject]@{ required_capabilities=@($RequiredCapabilities); matches=@($matches); match_count=$matches.Count; rejected=@($rejected); interface_selection=$interfaceSelection; authority_granted=$false; external_execution=$false }
}

Export-ModuleMember -Function Import-SageRegistrySet, Find-SageCapabilities
