Set-StrictMode -Version Latest

function Import-SageRegistrySet {
    param([Parameter(Mandatory)][string]$Path)
    $records = [System.Collections.Generic.List[object]]::new()
    foreach ($file in Get-ChildItem -LiteralPath $Path -Filter '*.json' -File) {
        $record = Get-Content -Raw -LiteralPath $file.FullName | ConvertFrom-Json -Depth 100 -DateKind String
        $records.Add([pscustomobject]@{ source=$file.FullName; record=$record; record_type=[string]$record.record_type })
    }
    [pscustomobject]@{ registry_path=$Path; records=@($records); count=$records.Count }
}

function Find-SageCapabilities {
    param([Parameter(Mandatory)]$Registry, [Parameter(Mandatory)][string[]]$RequiredCapabilities, [ValidateSet('READ_ONLY','ADAPTER_ONLY','MUTATING')][string]$MaxSideEffect='READ_ONLY')
    $rank=@{ READ_ONLY=0; ADAPTER_ONLY=1; MUTATING=2 }; $matches=[System.Collections.Generic.List[object]]::new()
    foreach ($item in @($Registry.records)) {
        $record=$item.record; $caps=@(); if ($record.PSObject.Properties['capabilities']) { $caps=@($record.capabilities) }; if ($record.record_type -eq 'tool_descriptor' -and $record.PSObject.Properties['operations']) { $caps=@($caps + $record.operations) }
        $missing=@($RequiredCapabilities | Where-Object { $caps -notcontains $_ })
        $side=[string]$(if ($record.PSObject.Properties['side_effect_class']) { $record.side_effect_class } else { 'READ_ONLY' })
        $preserves=($record.PSObject.Properties['scope_preservation'] -and $record.scope_preservation -eq $true -and $record.permission_preservation -eq $true -and $record.authority_preservation -eq $true -and $record.evidence_preservation -eq $true)
        $resolvedId = if ($record.PSObject.Properties['adapter_id']) { $record.adapter_id } elseif ($record.PSObject.Properties['tool_id']) { $record.tool_id } else { $record.agent_id }
        if ($missing.Count -eq 0 -and $rank[$side] -le $rank[$MaxSideEffect] -and ($record.record_type -ne 'provider_adapter' -or $preserves)) { $matches.Add([pscustomobject]@{ id=[string]$resolvedId; record_type=$record.record_type; capabilities=$caps; side_effect_class=$side; source=$item.source }) }
    }
    [pscustomobject]@{ required_capabilities=@($RequiredCapabilities); matches=@($matches); match_count=$matches.Count }
}

Export-ModuleMember -Function Import-SageRegistrySet, Find-SageCapabilities
