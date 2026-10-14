Set-StrictMode -Version Latest
$script:TechnologyRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$script:TechnologySchema = Join-Path $script:TechnologyRoot 'schemas\extensions\sage-technology-engineering.schema.json'

function Test-SageTechnologyRecord {
    [CmdletBinding()]
    param([Parameter(Mandatory)][AllowNull()]$Document)
    try {
        if ($null -eq $Document) { return $false }
        return [bool](Test-Json -Json ($Document | ConvertTo-Json -Depth 100 -Compress) -SchemaFile $script:TechnologySchema -ErrorAction SilentlyContinue)
    } catch { return $false }
}

function Test-SageTechnologyArtifact {
    param($Evidence,[string]$Root)
    if (-not $Evidence.PSObject.Properties['artifact_ref'] -or -not $Evidence.PSObject.Properties['sha256'] -or -not $Evidence.PSObject.Properties['environment']) { return $false }
    $relative=[string]$Evidence.artifact_ref
    if ([IO.Path]::IsPathRooted($relative) -or $relative -match '(^|[\\/])\.\.([\\/]|$)|:') { return $false }
    try {
        $rootPath=[IO.Path]::TrimEndingDirectorySeparator([IO.Path]::GetFullPath($Root))
        $path=[IO.Path]::GetFullPath((Join-Path $rootPath $relative))
        if (-not $path.StartsWith($rootPath+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) { return $false }
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { return $false }
        $item=Get-Item -LiteralPath $path
        while ($null -ne $item) {
            if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { return $false }
            if ($item.FullName -eq $rootPath) { break }
            $item=if ($item -is [IO.FileInfo]) { $item.Directory } else { $item.Parent }
        }
        return ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -ceq [string]$Evidence.sha256)
    } catch { return $false }
}

function Get-SageTechnologyDecisionReview {
    [CmdletBinding()]
    param([Parameter(Mandatory)][AllowNull()]$Decision,
          [ValidateSet('PLAN','VERIFY')][string]$Phase='PLAN',
          [string]$TaskId, $ArchitectureModel,
          [string]$EvidenceRoot=$script:TechnologyRoot)
    $errors=[System.Collections.Generic.List[string]]::new()
    $pending=[System.Collections.Generic.List[string]]::new()
    $schemaValid=Test-SageTechnologyRecord $Decision
    if (-not $schemaValid -or $Decision.record_type -ne 'sage_technology_decision') {
        return [pscustomobject]@{status='BLOCKED';schema_valid=$false;errors=@('DECISION_SCHEMA_INVALID');pending_checks=@();authority_granted=$false;external_execution=$false}
    }
    foreach ($set in @(@{name='candidate_id';items=@($Decision.candidates)},@{name='constraint_id';items=@($Decision.constraints)},@{name='evidence_id';items=@($Decision.evidence)},@{name='check_id';items=@($Decision.validation_plan)})) {
        $ids=@($set.items | ForEach-Object { [string]$_.$($set.name) })
        if (@($ids | Sort-Object -Unique).Count -ne $ids.Count) { $errors.Add("DUPLICATE_$($set.name.ToUpperInvariant())") }
    }
    if ($TaskId -and $Decision.task_id -cne $TaskId) { $errors.Add('TASK_ID_MISMATCH') }
    $architectureLink='NOT_CHECKED'
    if ($null -ne $ArchitectureModel) {
        try {
            $validModel=Test-Json -Json ($ArchitectureModel | ConvertTo-Json -Depth 100 -Compress) -SchemaFile (Join-Path $script:TechnologyRoot 'schemas\v0.8\sage-architecture.schema.json') -ErrorAction SilentlyContinue
            if (-not $validModel -or $ArchitectureModel.record_type -ne 'architecture_model' -or $ArchitectureModel.model_version -cne $Decision.architecture_model_version -or @($ArchitectureModel.elements | Where-Object architecture_id -CEQ $Decision.component_id).Count -ne 1) { $errors.Add('ARCHITECTURE_LINK_INVALID') }
            else { $architectureLink='MATCHED_REFERENCE_ONLY' }
        } catch { $errors.Add('ARCHITECTURE_LINK_INVALID') }
    }
    if ($Decision.candidates.Count -eq 1 -and (-not $Decision.PSObject.Properties['single_option_rationale'] -or [string]::IsNullOrWhiteSpace($Decision.single_option_rationale))) { $errors.Add('SINGLE_OPTION_RATIONALE_REQUIRED') }
    $evidence=@{}; foreach ($entry in @($Decision.evidence)) { $evidence[[string]$entry.evidence_id]=$entry }
    foreach ($entry in @($Decision.evidence)) {
        if (@($Decision.candidates | Where-Object candidate_id -CEQ $entry.subject_candidate_id).Count -ne 1) { $errors.Add('EVIDENCE_CANDIDATE_UNKNOWN') }
        if ($entry.subject_revision -cne $Decision.project_revision) { $errors.Add('EVIDENCE_REVISION_MISMATCH') }
        if ($entry.version.Trim() -match '^(latest|current|unknown|unversioned)$') { $errors.Add('UNPINNED_EVIDENCE_VERSION') }
        $parsedDate=[DateTimeOffset]::MinValue
        if (-not [DateTimeOffset]::TryParse([string]$entry.observed_at,[ref]$parsedDate)) { $errors.Add('INVALID_EVIDENCE_DATE') }
    }
    foreach ($candidate in @($Decision.candidates)) {
        $results=@($candidate.constraint_results)
        if (@($results | ForEach-Object constraint_id | Sort-Object -Unique).Count -ne $results.Count) { $errors.Add('DUPLICATE_CONSTRAINT_RESULT') }
        foreach ($reference in @($candidate.documentation_refs)) {
            if (-not $evidence.ContainsKey($reference) -or $evidence[$reference].kind -ne 'DOCUMENTATION' -or $evidence[$reference].subject_candidate_id -cne $candidate.candidate_id -or $evidence[$reference].source_ref -notmatch '^https://') { $errors.Add('DOCUMENTATION_REFERENCE_INVALID') }
        }
        foreach ($result in $results) {
            if (@($Decision.constraints | Where-Object constraint_id -CEQ $result.constraint_id).Count -ne 1) { $errors.Add('UNKNOWN_CONSTRAINT_RESULT') }
            foreach ($reference in @($result.evidence_refs)) {
                if (-not $evidence.ContainsKey($reference) -or $evidence[$reference].subject_candidate_id -cne $candidate.candidate_id) { $errors.Add('CONSTRAINT_EVIDENCE_REFERENCE_INVALID') }
            }
        }
    }
    $selected=@($Decision.candidates | Where-Object candidate_id -CEQ $Decision.selection.candidate_id)
    if ($selected.Count -ne 1) { $errors.Add('SELECTED_CANDIDATE_INVALID') }
    else {
        $selected=$selected[0]
        foreach ($reference in @($selected.documentation_refs)) {
            if ($evidence.ContainsKey($reference) -and $evidence[$reference].status -ne 'PASS') { $errors.Add('SELECTED_DOCUMENTATION_NOT_CHECKED') }
        }
        foreach ($constraint in @($Decision.constraints | Where-Object mandatory -EQ $true)) {
            $result=@($selected.constraint_results | Where-Object constraint_id -CEQ $constraint.constraint_id)
            if ($result.Count -ne 1 -or $result[0].status -ne 'SATISFIED' -or $result[0].evidence_refs.Count -eq 0) { $errors.Add('MANDATORY_CONSTRAINT_UNRESOLVED'); continue }
            foreach ($reference in @($result[0].evidence_refs)) {
                if (-not $evidence.ContainsKey($reference) -or $evidence[$reference].status -ne 'PASS') { $errors.Add('MANDATORY_CONSTRAINT_EVIDENCE_MISSING') }
                elseif ($constraint.kind -eq 'PERFORMANCE' -and ($evidence[$reference].kind -ne 'BENCHMARK' -or -not (Test-SageTechnologyArtifact $evidence[$reference] $EvidenceRoot))) { $errors.Add('PERFORMANCE_REQUIRES_MEASURED_RECEIPT') }
            }
        }
        $added=@($selected.languages | Where-Object { @($Decision.project_languages) -notcontains $_ })
        if ($Decision.project_languages.Count -gt 0 -and $added.Count -gt 0) {
            if (-not $Decision.selection.PSObject.Properties['added_language_cost_rationale'] -or [string]::IsNullOrWhiteSpace($Decision.selection.added_language_cost_rationale)) { $errors.Add('ADDED_LANGUAGE_COST_RATIONALE_REQUIRED') }
            if (@($Decision.validation_plan | Where-Object { $_.kind -eq 'COMPATIBILITY' -and $_.required }).Count -eq 0) { $errors.Add('CROSS_LANGUAGE_CHECK_REQUIRED') }
        }
    }
    foreach ($kind in @('BUILD','TEST')) {
        if (@($Decision.validation_plan | Where-Object { $_.kind -eq $kind -and $_.required }).Count -eq 0) { $errors.Add("${kind}_PLAN_REQUIRED") }
    }
    if ($Decision.selection.performance_claim -eq 'MEASURED') {
        $benchmarks=@($Decision.evidence | Where-Object { $_.kind -eq 'BENCHMARK' -and $_.status -eq 'PASS' -and $_.subject_candidate_id -ceq $Decision.selection.candidate_id })
        if ($benchmarks.Count -eq 0 -or @($benchmarks | Where-Object { -not (Test-SageTechnologyArtifact $_ $EvidenceRoot) }).Count -gt 0) { $errors.Add('PERFORMANCE_CLAIM_UNPROVEN') }
    }
    foreach ($check in @($Decision.validation_plan)) {
        foreach ($reference in @($check.evidence_refs)) {
            if (-not $evidence.ContainsKey($reference) -or $evidence[$reference].kind -cne $check.kind -or $evidence[$reference].subject_candidate_id -cne $Decision.selection.candidate_id -or $evidence[$reference].status -cne $check.status) { $errors.Add('CHECK_EVIDENCE_REFERENCE_INVALID') }
        }
        if ($check.required -and $check.status -eq 'FAIL') { $errors.Add('REQUIRED_CHECK_FAILED') }
        if ($check.required -and $check.status -eq 'NOT_RUN') { $pending.Add([string]$check.check_id) }
        if ($check.status -eq 'PASS') {
            if ($check.evidence_refs.Count -eq 0) { $errors.Add('CHECK_PASS_WITHOUT_EVIDENCE') }
            foreach ($reference in @($check.evidence_refs)) {
                if ($evidence.ContainsKey($reference) -and -not (Test-SageTechnologyArtifact $evidence[$reference] $EvidenceRoot)) { $errors.Add('CHECK_ARTIFACT_INTEGRITY_INVALID') }
            }
        }
    }
    if ($Phase -eq 'VERIFY' -and $pending.Count -gt 0) { $errors.Add('REQUIRED_CHECKS_NOT_RUN') }
    if ($Phase -eq 'VERIFY' -and $Decision.record_context -eq 'REFERENCE_FIXTURE') { $errors.Add('SYNTHETIC_FIXTURE_IS_NOT_PROJECT_PROOF') }
    [pscustomobject]@{
        status=$(if($errors.Count){'BLOCKED'}else{'READY_FOR_REVIEW'}); schema_valid=$true
        decision_id=$Decision.decision_id; component_id=$Decision.component_id; phase=$Phase
        selected_candidate=$Decision.selection.candidate_id; required_specialist_capabilities=@($Decision.required_specialist_capabilities)
        pending_checks=@($pending); errors=@($errors | Sort-Object -Unique); architecture_link=$architectureLink
        record_context=$Decision.record_context; evidence_trust='DECLARATIONS_AND_LOCAL_HASHES_ONLY_NOT_ATTESTED_EXECUTION'
        authority_granted=$false; external_execution=$false
    }
}

function Find-SageSpecialistProfiles {
    [CmdletBinding()]
    param([Parameter(Mandatory)][AllowNull()]$Catalog,[Parameter(Mandatory)][string[]]$RequiredCapabilities,
          [string]$ExtensionRoot=(Join-Path $script:TechnologyRoot 'extensions\technology-engineering'))
    $profileMatches=[System.Collections.Generic.List[object]]::new()
    $errors=[System.Collections.Generic.List[string]]::new()
    if (-not (Test-SageTechnologyRecord $Catalog) -or $Catalog.record_type -ne 'sage_specialist_catalog') { $errors.Add('CATALOG_SCHEMA_INVALID') }
    else {
        $ids=@($Catalog.profiles.profile_id)
        if (@($ids | Sort-Object -Unique).Count -ne $ids.Count) { $errors.Add('DUPLICATE_PROFILE_ID') }
        foreach ($profile in @($Catalog.profiles)) {
            $ref=[string]$profile.skill_ref
            if ($ref -notmatch '^skills/[a-z0-9-]+/SKILL\.md$' -or -not (Test-Path -LiteralPath (Join-Path $ExtensionRoot $ref) -PathType Leaf)) { $errors.Add('PROFILE_SKILL_REFERENCE_INVALID'); continue }
            $skillItem=Get-Item -LiteralPath (Join-Path $ExtensionRoot $ref)
            $extensionPath=[IO.Path]::GetFullPath($ExtensionRoot)
            $unsafeLink=$false
            while ($null -ne $skillItem) {
                if ($skillItem.Attributes -band [IO.FileAttributes]::ReparsePoint) { $unsafeLink=$true; break }
                if ($skillItem.FullName -eq $extensionPath) { break }
                $skillItem=if ($skillItem -is [IO.FileInfo]) { $skillItem.Directory } else { $skillItem.Parent }
            }
            if ($unsafeLink) { $errors.Add('PROFILE_SKILL_REFERENCE_UNSAFE_LINK'); continue }
            if (@($profile.capabilities | Sort-Object -Unique).Count -ne $profile.capabilities.Count) { $errors.Add('DUPLICATE_PROFILE_CAPABILITY') }
            if (@($RequiredCapabilities | Where-Object { $profile.capabilities -contains $_ }).Count -gt 0) { $profileMatches.Add($profile) }
        }
    }
    if ($errors.Count -gt 0) { $profileMatches.Clear() }
    # Deterministic greedy coverage: avoid activating every overlapping profile.
    # This is an advisory bounded heuristic, not a globally optimal staffing proof.
    $candidateCount=$profileMatches.Count
    $uncovered=@($RequiredCapabilities | Sort-Object -Unique)
    $chosen=[System.Collections.Generic.List[object]]::new()
    while ($uncovered.Count -gt 0 -and $profileMatches.Count -gt 0) {
        $ordered=@($profileMatches | Sort-Object -Property @{Expression={@($_.capabilities | Where-Object { $uncovered -contains $_ }).Count};Descending=$true},profile_id)
        $best=$ordered[0]
        $coverage=@($best.capabilities | Where-Object { $uncovered -contains $_ })
        if ($coverage.Count -eq 0) { break }
        $chosen.Add($best)
        $uncovered=@($uncovered | Where-Object { $coverage -notcontains $_ })
        $profileMatches.Remove($best) | Out-Null
    }
    $profileMatches=$chosen
    $missing=@($RequiredCapabilities | Where-Object { @($profileMatches | ForEach-Object capabilities) -notcontains $_ })
    [pscustomobject]@{status=$(if($errors.Count){'BLOCKED'}elseif($missing.Count){'NO_MATCH'}else{'MATCHES'});matches=@($profileMatches | Sort-Object profile_id);match_count=$profileMatches.Count;candidate_count=$candidateCount;selection_method='DETERMINISTIC_GREEDY_COVERAGE_NOT_GLOBAL_OPTIMUM';unmatched_capabilities=$missing;errors=@($errors | Sort-Object -Unique);readiness='DECLARED_PROFILES_NOT_RUNNING_AGENTS';authority_granted=$false;external_execution=$false}
}

function New-SageTechnologyDecisionView {
    [CmdletBinding()]
    param([Parameter(Mandatory)][AllowNull()]$Decision)
    $review=Get-SageTechnologyDecisionReview $Decision
    if ($review.status -ne 'READY_FOR_REVIEW') { return [pscustomobject]@{status='BLOCKED';errors=$review.errors;authority_granted=$false;external_execution=$false} }
    function Label([string]$Text) { [Net.WebUtility]::HtmlEncode(($Text -replace '[\r\n\x00-\x1f]',' ')) }
    $lines=[System.Collections.Generic.List[string]]::new()
    $lines.Add('%% Generated advisory view; not an approval or source of truth.')
    $lines.Add('flowchart LR')
    $lines.Add('    task["'+(Label $Decision.task_id)+'"] --> component["'+(Label $Decision.component_id)+'"]')
    $lines.Add('    gate["Independent review and approval still required"]')
    for($index=0;$index -lt $Decision.candidates.Count;$index++) {
        $candidate=$Decision.candidates[$index]
        $lines.Add('    component --> c'+$index+'["'+(Label (($candidate.languages -join ' / ')+' | '+$candidate.runtime))+'"]')
        if ($candidate.candidate_id -ceq $Decision.selection.candidate_id) { $lines.Add('    c'+$index+' -->|proposed selection| gate') }
    }
    [pscustomobject]@{status='GENERATED_SOURCE_ONLY';decision_id=$Decision.decision_id;model_version=$Decision.architecture_model_version;mermaid=($lines -join "`n");rendered=$false;authority_granted=$false;external_execution=$false}
}

Export-ModuleMember -Function Test-SageTechnologyRecord,Get-SageTechnologyDecisionReview,Find-SageSpecialistProfiles,New-SageTechnologyDecisionView
