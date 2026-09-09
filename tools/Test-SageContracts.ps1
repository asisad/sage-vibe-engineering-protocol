[CmdletBinding()]
param(
    [string]$Root
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
}

$schemaPath = Join-Path $Root 'schemas\v0.8\sage-contracts.schema.json'
$policySchemaPath = Join-Path $Root 'schemas\v0.8\sage-policies.schema.json'
$architectureSchemaPath = Join-Path $Root 'schemas\v0.8\sage-architecture.schema.json'
$manifestPath = Join-Path $Root 'SOURCE_MANIFEST.json'
$fixturePath = Join-Path $Root 'fixtures\v0.8'
$registryFixturePath = Join-Path $fixturePath 'registries'
$policyPath = Join-Path $Root 'policies\v0.8'
$failures = [System.Collections.Generic.List[string]]::new()
$passes = [System.Collections.Generic.List[string]]::new()

function Add-Pass([string]$Message) {
    $script:passes.Add($Message)
}

function Add-Failure([string]$Message) {
    $script:failures.Add($Message)
}

function Assert-Condition([bool]$Condition, [string]$Message) {
    if ($Condition) {
        Add-Pass $Message
    }
    else {
        Add-Failure $Message
    }
}

function Test-BriefPreservesContract($Document) {
    $task = $Document.task_packet
    $brief = $Document.brief
    if ($brief.risk_level -ne $Document.risk_assessment.risk_level) { return $false }
    if (($brief.authority | ConvertTo-Json -Depth 20 -Compress) -ne ($task.authority | ConvertTo-Json -Depth 20 -Compress)) { return $false }
    if (($brief.goal | ConvertTo-Json -Depth 30 -Compress) -ne ($task.goal | ConvertTo-Json -Depth 30 -Compress)) { return $false }
    foreach ($field in @('forbidden_paths','forbidden_side_effects','restricted_paths')) {
        foreach ($restriction in $task.change_scope.$field) {
            if (@($brief.change_scope.$field) -notcontains $restriction) { return $false }
        }
    }
    foreach ($field in @('allowed_paths','allowed_change_types')) {
        foreach ($grant in $brief.change_scope.$field) {
            if (@($task.change_scope.$field) -notcontains $grant) { return $false }
        }
    }
    foreach ($field in @('generated_artifact_policy','dependency_boundary','migration_boundary','deviation_protocol')) {
        if ([string]$brief.change_scope.$field -ne [string]$task.change_scope.$field) { return $false }
    }
    return $true
}

function ConvertTo-ComparableSet([object[]]$Values) {
    return @($Values | ForEach-Object { ([string]$_).Trim().ToLowerInvariant() } | Sort-Object -Unique)
}

function Test-SetOverlap([object[]]$Left, [object[]]$Right) {
    $rightSet = ConvertTo-ComparableSet $Right
    return @((ConvertTo-ComparableSet $Left) | Where-Object { $rightSet -contains $_ }).Count -gt 0
}

function Test-IsoDateTime([string]$Value) {
    try {
        [DateTimeOffset]::Parse(
            $Value,
            [System.Globalization.CultureInfo]::InvariantCulture,
            [System.Globalization.DateTimeStyles]::RoundtripKind
        ) | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

function Test-SecurityScopeReady($Scope) {
    if ($null -eq $Scope) { return $false }
    if ($Scope.authorization.status -ne 'GRANTED') { return $false }
    if ([string]::IsNullOrWhiteSpace([string]$Scope.authorization.approval_id)) { return $false }
    if (@($Scope.authorization.scope).Count -eq 0 -or @($Scope.target_allowlist).Count -eq 0) { return $false }
    if (@($Scope.allowed_techniques).Count -eq 0 -or @($Scope.prohibited_techniques).Count -eq 0) { return $false }
    if (Test-SetOverlap $Scope.target_allowlist $Scope.target_denylist) { return $false }
    if (Test-SetOverlap $Scope.allowed_techniques $Scope.prohibited_techniques) { return $false }
    foreach ($target in @($Scope.target_allowlist)) {
        if (@($Scope.authorization.scope) -notcontains $target) { return $false }
    }
    foreach ($value in @($Scope.evaluation_time, $Scope.time_window.starts_at, $Scope.time_window.ends_at, $Scope.authorization.expires_at)) {
        if (-not (Test-IsoDateTime ([string]$value))) { return $false }
    }
    $evaluation = [DateTimeOffset]::Parse([string]$Scope.evaluation_time)
    $starts = [DateTimeOffset]::Parse([string]$Scope.time_window.starts_at)
    $ends = [DateTimeOffset]::Parse([string]$Scope.time_window.ends_at)
    $expires = [DateTimeOffset]::Parse([string]$Scope.authorization.expires_at)
    if ($starts -ge $ends) { return $false }
    if ($evaluation -lt $starts -or $evaluation -gt $ends) { return $false }
    if ($evaluation -ge $expires) { return $false }
    return $true
}

if (-not (Test-Path -LiteralPath $schemaPath -PathType Leaf)) {
    throw "Schema not found: $schemaPath"
}
if (-not (Test-Path -LiteralPath $policySchemaPath -PathType Leaf)) {
    throw "Policy schema not found: $policySchemaPath"
}
if (-not (Test-Path -LiteralPath $architectureSchemaPath -PathType Leaf)) {
    throw "Architecture schema not found: $architectureSchemaPath"
}
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    throw "Source manifest not found: $manifestPath"
}

try {
    Get-Content -Raw -LiteralPath $schemaPath | ConvertFrom-Json -Depth 100 -DateKind String | Out-Null
    Add-Pass 'Schema JSON parses.'
}
catch {
    Add-Failure "Schema JSON parse failed: $($_.Exception.Message)"
}

try {
    Get-Content -Raw -LiteralPath $policySchemaPath | ConvertFrom-Json -Depth 100 -DateKind String | Out-Null
    Add-Pass 'Policy schema JSON parses.'
}
catch {
    Add-Failure "Policy schema JSON parse failed: $($_.Exception.Message)"
}

try {
    Get-Content -Raw -LiteralPath $architectureSchemaPath | ConvertFrom-Json -Depth 100 -DateKind String | Out-Null
    Add-Pass 'Architecture schema JSON parses.'
}
catch {
    Add-Failure "Architecture schema JSON parse failed: $($_.Exception.Message)"
}

$corePolicy = Get-Content -Raw -LiteralPath (Join-Path $policyPath 'core-policy.json') |
    ConvertFrom-Json -Depth 100 -DateKind String

$manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json -Depth 100 -DateKind String
Assert-Condition (@($manifest.entries).Count -ge 30) 'Source manifest contains all baseline, supplied and pinned upstream snapshots.'
Assert-Condition ($manifest.upstream_pins.'github/spec-kit'.commit -match '^[a-f0-9]{40}$') 'Spec Kit upstream pin is a full commit hash.'
Assert-Condition ($manifest.upstream_pins.'usestrix/strix'.commit -match '^[a-f0-9]{40}$') 'Strix upstream pin is a full commit hash.'

$fixtureFiles = @(Get-ChildItem -LiteralPath $fixturePath -Filter '*.json' -File | Where-Object { $_.Name -notin @('architecture-model.json','demonstrator-gps-map-request.json') } | Sort-Object Name)
Assert-Condition ($fixtureFiles.Count -eq 3) 'Exactly three R0/R2/R4 reference fixtures exist.'

foreach ($file in $fixtureFiles) {
    $raw = Get-Content -Raw -LiteralPath $file.FullName
    try {
        $schemaErrors = $null
        $valid = Test-Json -Json $raw -SchemaFile $schemaPath -ErrorVariable schemaErrors
        if ($valid) {
            Add-Pass "$($file.Name) passes JSON Schema 2020-12."
        }
        else {
            Add-Failure "$($file.Name) failed schema validation: $schemaErrors"
            continue
        }
    }
    catch {
        Add-Failure "$($file.Name) schema validation threw: $($_.Exception.Message)"
        continue
    }

    $doc = $raw | ConvertFrom-Json -Depth 100 -DateKind String
    $taskId = [string]$doc.task_packet.task_id
    Assert-Condition (Test-BriefPreservesContract $doc) "$($file.Name) brief preserves goal, risk, authority and scope contract."
    $evidenceIds = @($doc.evidence | ForEach-Object { $_.evidence_id })
    foreach ($criterion in $doc.task_packet.goal.acceptance_criteria) {
        foreach ($id in @($criterion.evidence_ids)) {
            Assert-Condition ($evidenceIds -contains $id) "$($file.Name) evidence reference $id resolves."
        }
    }
    Assert-Condition ([string]$doc.risk_assessment.task_id -eq $taskId) "$($file.Name) risk task_id matches."
    Assert-Condition ([string]$doc.gate_plan.task_id -eq $taskId) "$($file.Name) gate-plan task_id matches."
    Assert-Condition ([string]$doc.brief.task_id -eq $taskId) "$($file.Name) brief task_id matches."

    $allowed = @($doc.task_packet.change_scope.allowed_paths)
    $forbidden = @($doc.task_packet.change_scope.forbidden_paths)
    $overlap = @($allowed | Where-Object { $forbidden -contains $_ })
    Assert-Condition ($overlap.Count -eq 0) "$($file.Name) allowed and forbidden paths do not overlap."

    $invalidBlockingGate = @(
        $doc.gate_plan.gates |
            Where-Object {
                $_.state -eq 'ACTIVE' -and
                $_.blocking -eq $true -and
                @($_.evidence_required).Count -eq 0
            }
    )
    Assert-Condition ($invalidBlockingGate.Count -eq 0) "$($file.Name) active blocking gates require evidence."
    $gateIds = @($doc.gate_plan.gates | ForEach-Object { [string]$_.gate_id })
    Assert-Condition (($gateIds | Sort-Object -Unique).Count -eq $gateIds.Count) "$($file.Name) gate IDs are unique."
    $riskName = [string]$doc.risk_assessment.risk_level
    $requiredGates = @($corePolicy.risk_profiles.$riskName.required_gates)
    foreach ($requiredGate in $requiredGates) {
        Assert-Condition ($gateIds -contains "gate.$requiredGate") "$($file.Name) includes policy-required gate $requiredGate."
    }

    if ($doc.task_packet.authority.status -eq 'GRANTED') {
        Assert-Condition (@($doc.task_packet.authority.scope).Count -gt 0) "$($file.Name) granted task authority has non-empty scope."
        Assert-Condition (-not [string]::IsNullOrWhiteSpace([string]$doc.task_packet.authority.approval_id)) "$($file.Name) granted task authority has approval_id."
    }

    if ($doc.risk_assessment.risk_level -eq 'R0') {
        Assert-Condition ($doc.task_packet.budget.max_attempts -le 1) "$($file.Name) keeps the R0 attempt budget minimal."
        $heavyReview = @($doc.gate_plan.gates | Where-Object { $_.independent_review -eq $true })
        Assert-Condition ($heavyReview.Count -eq 0) "$($file.Name) does not inflate R0 with independent review."
    }

    if ($doc.risk_assessment.risk_level -eq 'R4') {
        Assert-Condition ($doc.task_packet.authority.status -eq 'GRANTED') "$($file.Name) has explicit granted authority."
        $humanGate = @(
            $doc.gate_plan.gates |
                Where-Object { $_.state -eq 'ACTIVE' -and $_.human_approval -eq $true }
        )
        Assert-Condition ($humanGate.Count -gt 0) "$($file.Name) contains an active human-approval gate."
        $independent = @($doc.gate_plan.gates | Where-Object { $_.state -eq 'ACTIVE' -and $_.independent_review -eq $true })
        Assert-Condition ($independent.Count -gt 0) "$($file.Name) retains independent review."
    }

    if (@($doc.task_packet.affected_domains) -contains 'security') {
        Assert-Condition ($null -ne $doc.security_scope) "$($file.Name) includes Security Scope."
        Assert-Condition ($doc.security_scope.authorization.status -eq 'GRANTED') "$($file.Name) security authorization is granted."
        Assert-Condition (@($doc.security_scope.target_allowlist).Count -gt 0) "$($file.Name) security target allowlist is non-empty."
        Assert-Condition (@($doc.security_scope.prohibited_techniques).Count -gt 0) "$($file.Name) security prohibited-techniques list is non-empty."
        Assert-Condition (Test-SecurityScopeReady $doc.security_scope) "$($file.Name) security scope is invocation-ready at evaluation_time."
    }
}

$registryFixtureFiles = @(Get-ChildItem -LiteralPath $registryFixturePath -Filter '*.json' -File | Sort-Object Name)
Assert-Condition ($registryFixtureFiles.Count -eq 3) 'Three full registry descriptor fixtures exist.'
foreach ($file in $registryFixtureFiles) {
    $raw = Get-Content -Raw -LiteralPath $file.FullName
    try {
        $valid = Test-Json -Json $raw -SchemaFile $schemaPath -ErrorAction SilentlyContinue
        Assert-Condition $valid "$($file.Name) passes the full registry contract."
    }
    catch {
        Add-Failure "$($file.Name) registry validation threw: $($_.Exception.Message)"
    }
}

$architectureFixturePath = Join-Path $fixturePath 'architecture-model.json'
$architectureRaw = Get-Content -Raw -LiteralPath $architectureFixturePath
try {
    $architectureValid = Test-Json -Json $architectureRaw -SchemaFile $architectureSchemaPath -ErrorAction SilentlyContinue
    Assert-Condition $architectureValid 'Architecture model fixture passes the architecture schema.'
}
catch {
    Add-Failure "Architecture fixture validation threw: $($_.Exception.Message)"
}
$architectureDoc = $architectureRaw | ConvertFrom-Json -Depth 100 -DateKind String
Assert-Condition ($architectureDoc.source_of_truth -eq $true -and $architectureDoc.authority -eq 'APPROVED') 'Approved architecture fixture remains the source of truth.'
Assert-Condition ((@($architectureDoc.elements | ForEach-Object { $_.architecture_id }) | Sort-Object -Unique).Count -eq @($architectureDoc.elements).Count) 'Architecture element IDs are unique.'
Assert-Condition ((@($architectureDoc.relationships | ForEach-Object { $_.from, $_.to } | Where-Object { @($architectureDoc.elements | ForEach-Object { $_.architecture_id }) -notcontains $_ }).Count -eq 0)) 'Architecture relationship endpoints resolve to stable element IDs.'

# Negative tests mutate in-memory copies only; no fixture or target is changed.
$negative = Get-Content -Raw -LiteralPath (Join-Path $fixturePath 'r0-documentation-typo.json') | ConvertFrom-Json -Depth 100 -DateKind String
$negative.brief.change_scope.forbidden_side_effects = @()
Assert-Condition (-not (Test-BriefPreservesContract $negative)) 'Reject a brief that drops forbidden side effects.'
$negative = Get-Content -Raw -LiteralPath (Join-Path $fixturePath 'r2-feature-data-path.json') | ConvertFrom-Json -Depth 100 -DateKind String
$negative.brief.risk_level = 'R0'
Assert-Condition (-not (Test-BriefPreservesContract $negative)) 'Reject a brief that downgrades risk.'
$negative.brief.risk_level = 'R2'
$negative.brief.authority.scope = @('entire-repository')
Assert-Condition (-not (Test-BriefPreservesContract $negative)) 'Reject a brief that expands authority.'
$negativeJson = '{"record_type":"provider_adapter","schema_version":"sage-contracts/0.8","adapter_id":"adapter.bad","version":"1","provider":"fixture","input_mapping":{},"output_mapping":{},"scope_preservation":false,"permission_preservation":true}'
$negativeValid = Test-Json -Json $negativeJson -SchemaFile $schemaPath -ErrorAction SilentlyContinue
Assert-Condition (-not $negativeValid) 'Schema rejects an adapter that does not preserve scope.'
$negative = Get-Content -Raw -LiteralPath (Join-Path $fixturePath 'r0-documentation-typo.json') | ConvertFrom-Json -Depth 100 -DateKind String
$negative.task_packet.authority.scope = @()
$negative.task_packet.authority.PSObject.Properties.Remove('approval_id')
$negativeValid = Test-Json -Json ($negative | ConvertTo-Json -Depth 100 -Compress) -SchemaFile $schemaPath -ErrorAction SilentlyContinue
Assert-Condition (-not $negativeValid) 'Schema rejects GRANTED task authority without approval_id and non-empty scope.'

$negative = Get-Content -Raw -LiteralPath (Join-Path $fixturePath 'r2-feature-data-path.json') | ConvertFrom-Json -Depth 100 -DateKind String
$negative.brief.goal.non_goals = @('Replace the database')
Assert-Condition (-not (Test-BriefPreservesContract $negative)) 'Reject a brief that drops a Goal Contract non-goal.'
$negative = Get-Content -Raw -LiteralPath (Join-Path $fixturePath 'r2-feature-data-path.json') | ConvertFrom-Json -Depth 100 -DateKind String
$negative.brief.goal.acceptance_criteria = @($negative.brief.goal.acceptance_criteria | Select-Object -First 1)
Assert-Condition (-not (Test-BriefPreservesContract $negative)) 'Reject a brief that drops an acceptance criterion.'

$negative = Get-Content -Raw -LiteralPath (Join-Path $fixturePath 'r4-authorized-security-validation.json') | ConvertFrom-Json -Depth 100 -DateKind String
$negative.security_scope.authorization.status = 'DENIED'
Assert-Condition (-not (Test-SecurityScopeReady $negative.security_scope)) 'Reject a denied security scope.'
$negative = Get-Content -Raw -LiteralPath (Join-Path $fixturePath 'r4-authorized-security-validation.json') | ConvertFrom-Json -Depth 100 -DateKind String
$negative.security_scope.time_window.ends_at = '2026-09-06T15:00:00Z'
Assert-Condition (-not (Test-SecurityScopeReady $negative.security_scope)) 'Reject a reversed security time window.'
$negative = Get-Content -Raw -LiteralPath (Join-Path $fixturePath 'r4-authorized-security-validation.json') | ConvertFrom-Json -Depth 100 -DateKind String
$negative.security_scope.target_denylist = @($negative.security_scope.target_allowlist)
Assert-Condition (-not (Test-SecurityScopeReady $negative.security_scope)) 'Reject overlapping security allowlist and denylist.'
$negative = Get-Content -Raw -LiteralPath (Join-Path $fixturePath 'r4-authorized-security-validation.json') | ConvertFrom-Json -Depth 100 -DateKind String
$negative.security_scope.evaluation_time = 'not-a-date'
Assert-Condition (-not (Test-SecurityScopeReady $negative.security_scope)) 'Reject an invalid security evaluation timestamp.'
$negative = Get-Content -Raw -LiteralPath (Join-Path $fixturePath 'r0-documentation-typo.json') | ConvertFrom-Json -Depth 100 -DateKind String
$negative.gate_plan.gates = @($negative.gate_plan.gates | Where-Object { $_.gate_id -ne 'gate.targeted-verification' })
$negativeGateIds = @($negative.gate_plan.gates | ForEach-Object { [string]$_.gate_id })
$missingRequired = @($corePolicy.risk_profiles.R0.required_gates | Where-Object { $negativeGateIds -notcontains "gate.$_" })
Assert-Condition ($missingRequired.Count -gt 0) 'Detect a fixture that drops a policy-required gate.'

$policyFiles = @(Get-ChildItem -LiteralPath $policyPath -Filter '*.json' -File | Sort-Object Name)
Assert-Condition ($policyFiles.Count -eq 3) 'Three reference policy files exist.'
foreach ($file in $policyFiles) {
    try {
        $raw = Get-Content -Raw -LiteralPath $file.FullName
        $raw | ConvertFrom-Json -Depth 100 -DateKind String | Out-Null
        $valid = Test-Json -Json $raw -SchemaFile $policySchemaPath -ErrorAction SilentlyContinue
        Assert-Condition $valid "$($file.Name) passes the policy schema."
    }
    catch {
        Add-Failure "$($file.Name) policy validation failed: $($_.Exception.Message)"
    }
}

$securityPolicy = Get-Content -Raw -LiteralPath (Join-Path $policyPath 'security-adapter-policy.json') |
    ConvertFrom-Json -Depth 100 -DateKind String
Assert-Condition ($securityPolicy.adapter_policy.core_dependency -eq $false) 'Security adapter is not a SAGE core dependency.'
Assert-Condition ($securityPolicy.adapter_policy.authorization_required -eq $true) 'Security adapter requires authorization.'
Assert-Condition ($securityPolicy.strix_binding.installation_managed_separately -eq $true) 'Strix installation is separated from architecture validation.'
Assert-Condition ([string]$securityPolicy.strix_binding.documented_exit_codes.'2' -eq 'vulnerabilities_found') 'Strix exit code 2 is not misclassified as a fatal tool error.'
Assert-Condition ($corePolicy.risk_profiles.R3.independent_review -eq $true) 'R3 policy requires independent review.'
Assert-Condition ($corePolicy.risk_profiles.R4.independent_review -eq $true) 'R4 policy requires independent review.'
Assert-Condition ($corePolicy.risk_profiles.R4.human_approval -eq $true) 'R4 policy requires human approval.'

$expectedHashes = @{
    'sources\supplied-originals\15-Claude-Code-Vibe-Coding-Prompts.pdf' = 'bfd903ce692662eb2cad491fe42baaef45d48f7fe48fe241728be35f86c0828b'
    'sources\supplied-originals\learn4.html' = 'ba42d412f3962aa4c55d08df1aa270801ca1e2ea4be25b1d754d081bae4ba579'
    'sources\integration-deltas\SAGE_v0.8_SPEC_KIT_INTEGRATION_DELTA.md' = '53bceb1a59d508cc000583bdec062b136cb83869d0d6bd6027a2b83404fa83ac'
    'sources\integration-deltas\SAGE_v0.8_CLAUDE_PROMPT_PACK_INTEGRATION_DELTA.md' = 'dcb1e468d8067811dcabaa870a66b7e966a641cf10d6bef02aea8f17aea856b5'
    'sources\integration-deltas\SAGE_v0.8_VIBE_MASTER_PROMPT_INTEGRATION_DELTA.md' = '3f779a7387fb459f1c63caa8ebc924ea5c95c78f1ea18c00e02063c7f083c8e5'
    'sources\integration-deltas\SAGE_v0.8_STRIX_SECURITY_INTEGRATION_DELTA.md' = '7a048ceb92d35d84b7e16ee4570f0665d3023f5d0eab5b9aee3e07cb258fcf52'
    'history\SAGE_v0.8_EXECUTION_PROTOCOL_AND_SKILL_CONTRACT_v0.8.0-draft.2.md' = '6cab3bf5006b57a01a2ab41e04e06b01dbdd46d4b1161882a9341fc8594876ac'
}

foreach ($relativePath in $expectedHashes.Keys) {
    $fullPath = Join-Path $Root $relativePath
    if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
        Add-Failure "Archived source missing: $relativePath"
        continue
    }
    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $fullPath).Hash.ToLowerInvariant()
    Assert-Condition ($actual -eq $expectedHashes[$relativePath]) "$relativePath hash matches the registry."
}

foreach ($entry in @($manifest.entries)) {
    $relativePath = ([string]$entry.path).Replace('/', '\')
    $fullPath = Join-Path $Root $relativePath
    if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
        Add-Failure "Manifest source missing: $($entry.path)"
        continue
    }
    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $fullPath).Hash.ToLowerInvariant()
    Assert-Condition ($actual -eq [string]$entry.sha256) "Manifest hash matches: $($entry.path)"
}

$result = [pscustomobject]@{
    schema = $schemaPath
    fixtures = $fixtureFiles.Count
    policies = $policyFiles.Count
    passed_checks = $passes.Count
    failed_checks = $failures.Count
    status = if ($failures.Count -eq 0) { 'PASS' } else { 'FAIL' }
    failures = @($failures)
}

$result | ConvertTo-Json -Depth 10

if ($failures.Count -gt 0) {
    exit 1
}

