Set-StrictMode -Version Latest

function Test-SageLocalSchemaReference {
    param([Parameter(Mandatory)][string]$Reference, [Parameter(Mandatory)][string]$Root)
    try {
        $parts=$Reference.Split('#')
        if ($parts.Count -gt 2 -or [string]::IsNullOrWhiteSpace($parts[0]) -or [System.IO.Path]::IsPathRooted($parts[0]) -or $parts[0].Contains(':') -or @($parts[0] -split '[\\/]' | Where-Object { $_ -eq '..' }).Count -gt 0) { return $false }
        $rootPath=[System.IO.Path]::GetFullPath($Root).TrimEnd([System.IO.Path]::DirectorySeparatorChar,[System.IO.Path]::AltDirectorySeparatorChar)
        $path=[System.IO.Path]::GetFullPath((Join-Path $rootPath $parts[0]))
        if (-not $path.StartsWith($rootPath+[System.IO.Path]::DirectorySeparatorChar,[System.StringComparison]::OrdinalIgnoreCase)) { return $false }
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { return $false }
        # A junction or symlink must not turn a local reference into an out-of-scope read.
        $cursor=$path
        while ($cursor.Length -gt $rootPath.Length) {
            if (((Get-Item -LiteralPath $cursor).Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) { return $false }
            $cursor=Split-Path -Parent $cursor
        }
        $node=Get-Content -Raw -LiteralPath $path | ConvertFrom-Json -AsHashtable -Depth 100
        if ($node -isnot [System.Collections.IDictionary]) { return $false }
        if ($parts.Count -eq 1 -or [string]::IsNullOrEmpty($parts[1])) { return $true }
        $pointer=[System.Uri]::UnescapeDataString($parts[1])
        if (-not $pointer.StartsWith('/')) { return $false }
        foreach ($segment in $pointer.Substring(1).Split('/')) {
            if ($segment -match '~(?![01])') { return $false }
            $key=$segment.Replace('~1','/').Replace('~0','~')
            if ($node -is [System.Collections.IDictionary]) {
                if (-not $node.Contains($key)) { return $false }
                $node=$node[$key]
            } elseif ($node -is [System.Collections.IList]) {
                $index=0
                if ($key -notmatch '^(0|[1-9][0-9]*)$' -or -not [int]::TryParse($key,[ref]$index) -or $index -ge $node.Count) { return $false }
                $node=$node[$index]
            } else { return $false }
        }
        return ($node -is [System.Collections.IDictionary] -or $node -is [bool])
    } catch { return $false }
}

function Test-SageAgentInterface {
    [CmdletBinding()]
    param([Parameter(Mandatory)][AllowNull()]$Descriptor, [string]$SchemaPath = (Join-Path $PSScriptRoot '..\..\schemas\v0.8\sage-agent-interface.schema.json'), [string]$Root=(Join-Path $PSScriptRoot '..\..'))
    $errors = [System.Collections.Generic.List[string]]::new()
    if ($null -eq $Descriptor) { return [pscustomobject]@{valid=$false;errors=@('INVALID_DESCRIPTOR_INPUT');authority_granted=$false;external_execution=$false} }
    try {
        $json = $Descriptor | ConvertTo-Json -Depth 100 -Compress
        $valid = Test-Json -Json $json -SchemaFile $SchemaPath -ErrorAction SilentlyContinue
        if (-not $valid) { $errors.Add('DESCRIPTOR_SCHEMA_INVALID') }
        else {
            foreach ($schemaField in @('input_schema_ref','output_schema_ref')) {
                if (-not (Test-SageLocalSchemaReference -Reference $Descriptor.contract.$schemaField -Root $Root)) { $errors.Add("SCHEMA_REFERENCE_INVALID:$schemaField") }
            }
            if ($Descriptor.contract.timeout_seconds -gt $Descriptor.contract.maximum_timeout_seconds) { $errors.Add('INVALID_TIMEOUT_BOUNDS') }
            $network = $Descriptor.contract.transport -in @('LOCALHOST','REMOTE')
            if ($network -and $Descriptor.security.network_authentication -eq 'NOT_APPLICABLE') { $errors.Add('NETWORK_AUTHENTICATION_REQUIRED') }
            if (-not $network -and $Descriptor.security.network_authentication -ne 'NOT_APPLICABLE') { $errors.Add('TRANSPORT_AUTHENTICATION_MISMATCH') }
            if ($Descriptor.security.side_effect_class -notin @('READ_ONLY','ADAPTER_ONLY') -and -not $Descriptor.contract.dry_run) { $errors.Add('MUTATION_DRY_RUN_REQUIRED') }
            if ($Descriptor.layers.callable_surface -eq 'NATIVE_API' -and $Descriptor.contract.transport -ne 'IN_PROCESS') { $errors.Add('NATIVE_API_TRANSPORT_MISMATCH') }
            if ($Descriptor.layers.callable_surface -eq 'CLI' -and $Descriptor.contract.transport -ne 'STDIO') { $errors.Add('CLI_TRANSPORT_MISMATCH') }
            foreach ($requiredCode in @('INVALID_INPUT','TIMEOUT','CANCELLED','VERSION_MISMATCH','UNAUTHORIZED')) {
                if ($Descriptor.contract.error_codes -notcontains $requiredCode) { $errors.Add("MISSING_ERROR_CODE:$requiredCode") }
            }
        }
    } catch { $errors.Add('DESCRIPTOR_VALIDATION_FAILED') }
    [pscustomobject]@{ valid=($errors.Count -eq 0); errors=@($errors); authority_granted=$false; external_execution=$false }
}

function Select-SageAgentInterface {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][AllowNull()][AllowEmptyCollection()][object[]]$Descriptors,
        [Parameter(Mandatory)][ValidateNotNullOrEmpty()][string[]]$RequiredCapabilities,
        [ValidateSet('READ_ONLY','ADAPTER_ONLY','MUTATING')][string]$MaxSideEffect='READ_ONLY',
        [ValidateSet('ANY','NATIVE_API','CLI','MCP','CLI_AND_MCP')][string]$Surface='ANY',
        [string]$SchemaPath=(Join-Path $PSScriptRoot '..\..\schemas\v0.8\sage-agent-interface.schema.json'),
        [string]$Root=(Join-Path $PSScriptRoot '..\..')
    )
    $rank=@{ READ_ONLY=0; ADAPTER_ONLY=1; LOCAL_REVERSIBLE=2; LOCAL_DESTRUCTIVE=3; EXTERNAL_MUTATION=3; SECURITY_ACTIVE=3 }
    $maximum=@{ READ_ONLY=0; ADAPTER_ONLY=1; MUTATING=2 }
    $decisions=@{ ADOPT=0; ADAPT=1; BUILD=2 }
    $surfaces=@{ NATIVE_API=0; CLI=1; MCP=2; CLI_AND_MCP=3 }
    $eligible=[System.Collections.Generic.List[object]]::new()
    $rejected=[System.Collections.Generic.List[object]]::new()
    foreach ($descriptor in $Descriptors) {
        $validation=Test-SageAgentInterface -Descriptor $descriptor -SchemaPath $SchemaPath -Root $Root
        $id=if ($null -ne $descriptor -and $descriptor.PSObject.Properties['interface_id']) { [string]$descriptor.interface_id } else { '<invalid>' }
        if (-not $validation.valid) { $rejected.Add([pscustomobject]@{ id=$id; reasons=$validation.errors }); continue }
        $reason=$null
        if (@($RequiredCapabilities | Where-Object { $descriptor.capabilities -notcontains $_ }).Count -gt 0) { $reason='CAPABILITY_MISMATCH' }
        elseif ($rank[[string]$descriptor.security.side_effect_class] -gt $maximum[$MaxSideEffect]) { $reason='SIDE_EFFECT_EXCEEDS_LIMIT' }
        elseif ($Surface -ne 'ANY' -and $descriptor.layers.callable_surface -ne $Surface -and -not ($descriptor.layers.callable_surface -eq 'CLI_AND_MCP' -and $Surface -in @('CLI','MCP'))) { $reason='SURFACE_MISMATCH' }
        if ($reason) { $rejected.Add([pscustomobject]@{ id=$id; reasons=@($reason) }); continue }
        $eligible.Add($descriptor)
    }
    # Identity conflicts stay ambiguous even when one record fails validation or filtering.
    $duplicates=@($Descriptors | Where-Object { $null -ne $_ -and $_.PSObject.Properties['interface_id'] } | Group-Object interface_id | Where-Object Count -gt 1 | ForEach-Object Name)
    $candidates=@($eligible | Where-Object { $duplicates -notcontains $_.interface_id } | Sort-Object @{Expression={$rank[[string]$_.security.side_effect_class]}}, @{Expression={$decisions[[string]$_.decision]}}, @{Expression={$surfaces[[string]$_.layers.callable_surface]}}, interface_id)
    foreach ($id in $duplicates) { $rejected.Add([pscustomobject]@{ id=$id; reasons=@('DUPLICATE_INTERFACE_ID') }) }
    [pscustomobject]@{
        status=if ($candidates.Count) { 'RECOMMENDED' } else { 'NO_MATCH' }
        selected=if ($candidates.Count) { $candidates[0] } else { $null }
        candidates=$candidates; rejected=@($rejected)
        authority_granted=$false; external_execution=$false
    }
}

Export-ModuleMember -Function Test-SageAgentInterface, Select-SageAgentInterface
