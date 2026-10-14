Set-StrictMode -Version Latest
$script:SensSchema=Join-Path $PSScriptRoot 'schemas\sage-sens.schema.json'

function Test-SageSensDocument {
    [CmdletBinding()]
    param([Parameter(Mandatory)][AllowNull()]$Document)
    $issues=[System.Collections.Generic.List[string]]::new()
    try {
        $json=$Document | ConvertTo-Json -Depth 40 -Compress
        if ($null -eq $Document -or -not (Test-Json -Json $json -SchemaFile $script:SensSchema -ErrorAction Stop)) { $issues.Add('SCHEMA_INVALID') }
    } catch { $issues.Add('SCHEMA_INVALID') }
    if ($issues.Count -eq 0) {
        if ($json -match '(?i)sk-or-v1-[A-Za-z0-9_-]{16,}|AIza[A-Za-z0-9_-]{30,}|gh[pousr]_[A-Za-z0-9]{25,}|-----BEGIN.{0,16}PRIVATE KEY-----|Bearer\s+') { $issues.Add('CREDENTIAL_PATTERN_REJECTED') }
        switch ($Document.record_type) {
            'sens_registration' {
                if ($null -ne $Document.source_ref) {
                    $uri=$null
                    if (-not [Uri]::TryCreate([string]$Document.source_ref,[UriKind]::Absolute,[ref]$uri) -or $uri.Scheme -ne 'https' -or $uri.UserInfo -or $uri.Query -or $uri.Fragment) { $issues.Add('SOURCE_REFERENCE_NOT_SAFE') }
                }
            }
            'sens_integration_config' {
                if ($Document.budget.max_batch_events -gt $Document.budget.max_queue_events) { $issues.Add('BATCH_EXCEEDS_QUEUE') }
            }
            'sage_sens_event' {
                $parsed=[DateTimeOffset]::MinValue
                if (-not [DateTimeOffset]::TryParse([string]$Document.timestamp,[ref]$parsed)) { $issues.Add('TIMESTAMP_INVALID') }
            }
            'sens_finding' {
                $parsed=[DateTimeOffset]::MinValue
                if (-not [DateTimeOffset]::TryParse([string]$Document.provenance.observed_at,[ref]$parsed)) { $issues.Add('TIMESTAMP_INVALID') }
            }
        }
    }
    [pscustomobject]@{valid=($issues.Count -eq 0);errors=@($issues);authority_granted=$false;external_execution=$false}
}

function Get-SageSensRegistrationReview {
    [CmdletBinding()]
    param([Parameter(Mandatory)][AllowNull()]$Registration)
    $check=Test-SageSensDocument $Registration
    if (-not $check.valid -or $Registration.record_type -ne 'sens_registration') {
        return [pscustomobject]@{status='BLOCKED';errors=@($check.errors)+@('REGISTRATION_REQUIRED');registered=$false;activation_granted=$false;external_execution=$false}
    }
    [pscustomobject]@{status='PROPOSAL_ONLY';sens_id=$Registration.sens_id;source_connected=$false;registered=$false;activation_granted=$false;authority_granted=$false;external_execution=$false}
}

function New-SageSensPreview {
    [CmdletBinding()]
    param([Parameter(Mandatory)][AllowNull()]$Config,[AllowEmptyCollection()][object[]]$Events=@())
    $accepted=[System.Collections.Generic.List[object]]::new()
    $dropped=[System.Collections.Generic.List[object]]::new()
    $check=Test-SageSensDocument $Config
    if (-not $check.valid -or $Config.record_type -ne 'sens_integration_config') {
        return [pscustomobject]@{status='SKIPPED_CONFIG_INVALID';accepted=@();accepted_count=0;dropped_count=$Events.Count;errors=@($check.errors);authority_granted=$false;external_execution=$false;safety_gates_bypassed=$false}
    }
    if ($Config.mode -eq 'DISABLED') {
        return [pscustomobject]@{status='DISABLED';accepted=@();accepted_count=0;dropped_count=$Events.Count;authority_granted=$false;external_execution=$false;safety_gates_bypassed=$false}
    }
    $seen=[Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    $capacity=[Math]::Min([int]$Config.budget.max_batch_events,[int]$Config.budget.max_queue_events)
    $inspected=[Math]::Min($Events.Count,256)
    for ($index=0;$index -lt $inspected;$index++) {
        $event=$Events[$index]
        $validation=Test-SageSensDocument $event
        $reason=$null
        if (-not $validation.valid -or $event.record_type -ne 'sage_sens_event') { $reason='INVALID_EVENT' }
        elseif (@($Config.project_allowlist) -cnotcontains $event.project_id) { $reason='PROJECT_OUT_OF_SCOPE' }
        elseif ([Text.Encoding]::UTF8.GetByteCount(($event | ConvertTo-Json -Depth 40 -Compress)) -gt $Config.budget.max_event_bytes) { $reason='EVENT_BYTE_LIMIT' }
        elseif (-not $seen.Add([string]$event.event_id)) { $reason='DUPLICATE_EVENT' }
        elseif ($accepted.Count -ge $capacity) { $reason='BATCH_CAPACITY' }
        if ($reason) { $dropped.Add([pscustomobject]@{reason=$reason}); continue }
        # Return plain copied metadata, never a caller's executable PSObject.
        $accepted.Add(($event | ConvertTo-Json -Depth 40 -Compress | ConvertFrom-Json -Depth 40 -DateKind String))
    }
    [pscustomobject]@{status='PREVIEW_ONLY';accepted=@($accepted);accepted_count=$accepted.Count;dropped_count=($Events.Count-$accepted.Count);dropped=@($dropped);inspected_count=$inspected;input_truncated=($Events.Count -gt $inspected);transport_connected=$false;rate_window_enforced=$false;authority_granted=$false;external_execution=$false;safety_gates_bypassed=$false}
}

function Get-SageSensFindingReview {
    [CmdletBinding()]
    param([Parameter(Mandatory)][AllowNull()]$Finding,
          [Parameter(Mandatory)][string]$ExpectedProject,
          [Parameter(Mandatory)][string]$ExpectedTask,
          [Parameter(Mandatory)][string]$ExpectedRevision,
          [Parameter(Mandatory)][string]$ExpectedSensId)
    $check=Test-SageSensDocument $Finding
    $issues=[System.Collections.Generic.List[string]]::new()
    if (-not $check.valid -or $Finding.record_type -ne 'sens_finding') { $issues.Add('FINDING_SCHEMA_INVALID') }
    else {
        if ($Finding.project_id -cne $ExpectedProject) { $issues.Add('PROJECT_MISMATCH') }
        if ($Finding.task_id -cne $ExpectedTask) { $issues.Add('TASK_MISMATCH') }
        if ($Finding.source_revision -cne $ExpectedRevision) { $issues.Add('REVISION_MISMATCH') }
        if ($Finding.sens_id -cne $ExpectedSensId) { $issues.Add('SENS_ID_MISMATCH') }
    }
    [pscustomobject]@{status=$(if($issues.Count){'BLOCKED'}else{'ADVISORY_REVIEW_REQUIRED'});errors=@($issues);evidence_verified=$false;commands_executed=0;authority_granted=$false;external_execution=$false}
}

Export-ModuleMember -Function Test-SageSensDocument,Get-SageSensRegistrationReview,New-SageSensPreview,Get-SageSensFindingReview
