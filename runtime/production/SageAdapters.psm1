Set-StrictMode -Version Latest

# Provider-neutral production boundary. The default execution mode is DRY_RUN;
# adapters may describe an invocation but cannot perform external side effects.

function Import-SageAdapterRegistry {
    param([Parameter(Mandatory)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Adapter registry not found: $Path" }
    $data = Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json -Depth 100
    if ($data.record_type -ne 'provider_adapter') { throw 'Registry record_type must be provider_adapter.' }
    if (-not $data.adapter_id -or -not $data.provider) { throw 'Adapter registry requires adapter_id and provider.' }
    if ($data.scope_preservation -ne $true -or $data.permission_preservation -ne $true -or $data.authority_preservation -ne $true -or $data.evidence_preservation -ne $true) { throw 'Adapter registry must preserve scope, permission, authority, and evidence.' }
    return $data
}

function Register-SageToolAdapter {
    param([Parameter(Mandatory)][hashtable]$Registry, [Parameter(Mandatory)][hashtable]$Tool)
    if (-not $Registry.ContainsKey('adapters')) { $Registry.adapters = @{} }
    if (-not $Tool.tool_id) { throw 'Tool requires tool_id.' }
    if ($Registry.adapters.ContainsKey([string]$Tool.tool_id)) { throw "Duplicate tool adapter: $($Tool.tool_id)" }
    if (-not $Tool.side_effect_class) { throw 'Tool requires side_effect_class.' }
    $Registry.adapters[[string]$Tool.tool_id] = [pscustomobject]$Tool
    return $Registry
}

function Register-SageDescriptor {
    param([Parameter(Mandatory)][hashtable]$Registry, [Parameter(Mandatory)]$Descriptor)
    $kind = [string]$Descriptor.record_type
    $allowedKinds = @('agent_capability','tool_descriptor','provider_adapter')
    if ($allowedKinds -notcontains $kind) { throw "Unsupported SAGE descriptor type: $kind" }
    $id = if ($Descriptor.PSObject.Properties['agent_id']) { [string]$Descriptor.agent_id } elseif ($Descriptor.PSObject.Properties['tool_id']) { [string]$Descriptor.tool_id } elseif ($Descriptor.PSObject.Properties['adapter_id']) { [string]$Descriptor.adapter_id } else { '' }
    if ([string]::IsNullOrWhiteSpace($id)) { throw 'Descriptor must contain a stable agent_id, tool_id or adapter_id.' }
    if (-not $Registry.ContainsKey('descriptors')) { $Registry.descriptors = @{} }
    if ($Registry.descriptors.ContainsKey($id)) { throw "Duplicate SAGE descriptor: $id" }
    if ($kind -eq 'provider_adapter') {
        foreach ($field in @('scope_preservation','permission_preservation','authority_preservation','evidence_preservation')) { if ($Descriptor.$field -ne $true) { throw "Provider descriptor must preserve $($field -replace '_preservation','')." } }
    }
    $Registry.descriptors[$id] = [pscustomobject]@{ descriptor_id=$id; record_type=$kind; descriptor=$Descriptor; registered_mode='OFFLINE' }
    return $Registry
}

function Test-SageAdapterScope {
    param([Parameter(Mandatory)]$Adapter, [Parameter(Mandatory)]$Request)
    $reasons = [System.Collections.Generic.List[string]]::new()
    if (-not $Adapter.scope_preservation) { $reasons.Add('adapter does not preserve scope') }
    if (-not $Adapter.permission_preservation) { $reasons.Add('adapter does not preserve permission') }
    if (-not $Adapter.authority_preservation) { $reasons.Add('adapter does not preserve authority') }
    if (-not $Adapter.evidence_preservation) { $reasons.Add('adapter does not preserve evidence') }
    if (-not $Request.PSObject.Properties['authority']) { $reasons.Add('request authority is missing') }
    elseif ($Request.authority.status -ne 'GRANTED') { $reasons.Add('request authority is not GRANTED') }
    elseif (@($Request.authority.scope).Count -eq 0) { $reasons.Add('granted request authority has empty scope') }
    [pscustomobject]@{ allowed=($reasons.Count -eq 0); reasons=@($reasons) }
}

function New-SageInvocationPlan {
    param([Parameter(Mandatory)]$Adapter, [Parameter(Mandatory)]$Tool, [Parameter(Mandatory)]$Request, [ValidateSet('DRY_RUN','LIVE')][string]$Mode='DRY_RUN')
    if ($Mode -ne 'DRY_RUN') { throw 'LIVE adapter execution is not enabled by the reference production boundary.' }
    $scope = Test-SageAdapterScope -Adapter $Adapter -Request $Request
    $plan = [pscustomobject]@{
        plan_type='sage_invocation_plan'; plan_id="plan.$([guid]::NewGuid().ToString('N'))"; mode=$Mode
        adapter_id=[string]$Adapter.adapter_id; provider=[string]$Adapter.provider; tool_id=[string]$Tool.tool_id
        allowed=$scope.allowed; reasons=@($scope.reasons); side_effect_class=[string]$Tool.side_effect_class
        network_mode=if ($Tool.network_behavior) { [string]$Tool.network_behavior.mode } else { 'UNKNOWN' }
        request_digest=([Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes(($Request | ConvertTo-Json -Depth 50 -Compress)))).ToLower())
        created_at=[DateTime]::UtcNow.ToString('o')
    }
    if (-not $scope.allowed) { $plan.allowed=$false }
    return $plan
}

function Invoke-SageAdapter {
    param([Parameter(Mandatory)]$Plan)
    if ($Plan.mode -ne 'DRY_RUN') { throw 'Only DRY_RUN is supported.' }
    [pscustomobject]@{ status='PLANNED'; executed=$false; plan_id=$Plan.plan_id; adapter_id=$Plan.adapter_id; tool_id=$Plan.tool_id; allowed=$Plan.allowed; reasons=@($Plan.reasons); evidence_kind='adapter-dry-run'; recorded_at=[DateTime]::UtcNow.ToString('o') }
}

function Test-SageAdapterRegistry {
    param([Parameter(Mandatory)]$Adapter, [Parameter(Mandatory)]$Tool)
    $issues = @()
    foreach ($field in @('adapter_id','provider','interfaces')) { if (-not $Adapter.PSObject.Properties[$field]) { $issues += "missing adapter field: $field" } }
    foreach ($field in @('tool_id','side_effect_class')) { if (-not $Tool.PSObject.Properties[$field]) { $issues += "missing tool field: $field" } }
    if ($Tool.network_behavior.mode -ne 'NONE' -and $Tool.side_effect_class -eq 'READ_ONLY') { $issues += 'read-only tool must declare NONE network behavior' }
    [pscustomobject]@{ valid=($issues.Count -eq 0); issues=@($issues) }
}

function Invoke-SageLocalReferenceAdapter {
    param([Parameter(Mandatory)][string]$Root, [Parameter(Mandatory)][string]$RelativePath)
    $rootFull = [IO.Path]::GetFullPath($Root)
    $target = [IO.Path]::GetFullPath((Join-Path $rootFull $RelativePath))
    if (-not $target.StartsWith($rootFull.TrimEnd('\') + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Local adapter target escaped the approved root.' }
    if (-not (Test-Path -LiteralPath $target -PathType Leaf)) { throw "Local adapter target not found: $RelativePath" }
    $content = Get-Content -Raw -LiteralPath $target
    $digest = ([Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($content)))).ToLower()
    [pscustomobject]@{ status='COMPLETED'; executed=$true; adapter_id='adapter.local-reference'; operation='READ_AND_DIGEST'; target=$RelativePath; bytes=[Text.Encoding]::UTF8.GetByteCount($content); sha256=$digest; network='NONE'; mutation='NONE'; evidence_kind='local-read-proof'; recorded_at=[DateTime]::UtcNow.ToString('o') }
}

Export-ModuleMember -Function Import-SageAdapterRegistry,Register-SageToolAdapter,Register-SageDescriptor,Test-SageAdapterScope,New-SageInvocationPlan,Invoke-SageAdapter,Test-SageAdapterRegistry,Invoke-SageLocalReferenceAdapter
