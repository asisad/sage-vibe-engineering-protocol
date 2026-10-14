[CmdletBinding()]
param([string]$Root)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
if(-not $Root){$Root=Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)}
$sensRoot=Join-Path $Root 'integrations\sens'
Import-Module (Join-Path $sensRoot 'SageSens.psm1') -Force
$checks=[Collections.Generic.List[string]]::new()
function Assert([bool]$Condition,[string]$Name){if(-not $Condition){throw "SENS integration test failed: $Name"};$checks.Add($Name)}
function ReadJson([string]$Path){Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json -Depth 40 -DateKind String}
function Clone($Value){$Value | ConvertTo-Json -Depth 40 | ConvertFrom-Json -Depth 40 -DateKind String}
$config=ReadJson (Join-Path $sensRoot 'config.example.json')
$registration=ReadJson (Join-Path $sensRoot 'registration.example.json')
$event=ReadJson (Join-Path $sensRoot 'examples\event.json')
$finding=ReadJson (Join-Path $sensRoot 'examples\finding.json')
foreach($record in @($config,$registration,$event,$finding)){
    $validation=Test-SageSensDocument $record
    Assert $validation.valid "$($record.record_type) schema"
    Assert (-not $validation.authority_granted -and -not $validation.external_execution) "$($record.record_type) no authority"
}
foreach($malformed in @($null,42,'untrusted',@{record_type='unknown'})){
    Assert (-not (Test-SageSensDocument $malformed).valid) 'malformed record fails closed'
}
$review=Get-SageSensRegistrationReview $registration
Assert ($review.status -eq 'PROPOSAL_ONLY' -and -not $review.registered -and -not $review.activation_granted) 'self introduction never activates'
foreach($mutation in @(
    @{name='self activation';edit={param($x)$x.auto_activate=$true}},
    @{name='self approval';edit={param($x)$x.approval_state='APPROVED'}},
    @{name='execution authority';edit={param($x)$x.authority='GRANTED'}},
    @{name='incompatible protocol';edit={param($x)$x.protocol_versions=@('sage-sens/9.0')}},
    @{name='credential in source URL';edit={param($x)$x.source_ref='https://name:password@example.invalid/sens'}},
    @{name='query in source URL';edit={param($x)$x.source_ref='https://example.invalid/sens?credential=private'}},
    @{name='unknown command field';edit={param($x)$x | Add-Member NoteProperty command 'DO_NOT_EXECUTE'}}
)){$bad=Clone $registration;& $mutation.edit $bad;Assert ((Get-SageSensRegistrationReview $bad).status -eq 'BLOCKED') $mutation.name}
$disabled=New-SageSensPreview -Config $config -Events @($event)
Assert ($disabled.status -eq 'DISABLED' -and $disabled.accepted_count -eq 0 -and -not $disabled.safety_gates_bypassed) 'disabled default does not publish or bypass gates'
$previewConfig=Clone $config;$previewConfig.mode='PREVIEW_ONLY'
$preview=New-SageSensPreview -Config $previewConfig -Events @($event)
Assert ($preview.status -eq 'PREVIEW_ONLY' -and $preview.accepted_count -eq 1) 'offline preview accepts valid metadata'
Assert (-not $preview.external_execution -and -not $preview.transport_connected -and -not $preview.rate_window_enforced) 'no hidden network or rate worker'
Assert ($preview.accepted[0].status -eq 'NOT_RUN') 'NOT RUN is not promoted'
$eventCopy=Clone $event;$duplicate=New-SageSensPreview -Config $previewConfig -Events @($event,$eventCopy)
Assert ($duplicate.accepted_count -eq 1 -and $duplicate.dropped_count -eq 1 -and $duplicate.dropped[0].reason -eq 'DUPLICATE_EVENT') 'duplicate event is dropped'
$outOfScope=Clone $event;$outOfScope.project_id='another.project'
Assert ((New-SageSensPreview -Config $previewConfig -Events @($outOfScope)).accepted_count -eq 0) 'project allowlist enforced'
$caseScope=Clone $event;$caseScope.project_id='SAGE.REFERENCE'
Assert ((New-SageSensPreview -Config $previewConfig -Events @($caseScope)).accepted_count -eq 0) 'scope identity is case exact'
$small=Clone $previewConfig;$small.budget.max_event_bytes=256
Assert ((New-SageSensPreview -Config $small -Events @($event)).dropped[0].reason -eq 'EVENT_BYTE_LIMIT') 'UTF8 event bytes bounded'
$many=@(1..300 | ForEach-Object {$copy=Clone $event;$copy.event_id="event.reference.$_";$copy})
$bounded=New-SageSensPreview -Config $previewConfig -Events $many
Assert ($bounded.accepted_count -eq 16 -and $bounded.dropped_count -eq 284) 'batch and queue limits'
Assert ($bounded.input_truncated -and $bounded.inspected_count -eq 256 -and $bounded.dropped.Count -le 256) 'preview inspection and rejection memory bounded'
foreach($mutation in @(
    @{name='raw payload rejected';edit={param($x)$x | Add-Member NoteProperty payload 'private source'}},
    @{name='credential field rejected';edit={param($x)$x | Add-Member NoteProperty token 'placeholder'}},
    @{name='restricted telemetry rejected';edit={param($x)$x.privacy_class='RESTRICTED'}},
    @{name='raw content mode rejected';edit={param($x)$x.content_mode='FULL_SOURCE'}},
    @{name='bad time rejected';edit={param($x)$x.timestamp='invalid-time'}},
    @{name='old event version rejected';edit={param($x)$x.schema_version='sage-sens/9.0'}},
    @{name='credential-shaped ID rejected';edit={param($x)$x.actor_id='sk-or-v1-'+('0'*32)}}
)){$bad=Clone $event;& $mutation.edit $bad;$result=New-SageSensPreview -Config $previewConfig -Events @($bad);Assert ($result.accepted_count -eq 0 -and $result.dropped_count -eq 1) $mutation.name}
$badConfig=Clone $previewConfig;$badConfig.mode='LIVE'
Assert ((New-SageSensPreview -Config $badConfig -Events @($event)).status -eq 'SKIPPED_CONFIG_INVALID') 'live mode cannot be enabled here'
$badConfig=Clone $previewConfig;$badConfig.endpoint_ref='https://example.invalid/send'
Assert (-not (Test-SageSensDocument $badConfig).valid) 'endpoint reference only, no raw URL'
$badConfig=Clone $previewConfig;$badConfig.credential_ref='placeholder-secret'
Assert (-not (Test-SageSensDocument $badConfig).valid) 'credential reference only'
$badConfig=Clone $previewConfig;$badConfig.budget.max_batch_events=100;$badConfig.budget.max_queue_events=2
Assert (-not (Test-SageSensDocument $badConfig).valid) 'batch cannot exceed queue'
Assert ((New-SageSensPreview -Config $null -Events @($event)).status -eq 'SKIPPED_CONFIG_INVALID') 'invalid optional telemetry does not throw into workflow'
$context=@{ExpectedProject=$finding.project_id;ExpectedTask=$finding.task_id;ExpectedRevision=$finding.source_revision;ExpectedSensId=$finding.sens_id}
$advice=Get-SageSensFindingReview -Finding $finding @context
Assert ($advice.status -eq 'ADVISORY_REVIEW_REQUIRED' -and -not $advice.evidence_verified -and -not $advice.authority_granted -and $advice.commands_executed -eq 0) 'findings are unverified advice, never execution'
foreach($field in @('project_id','task_id','source_revision','sens_id')){
    $bad=Clone $finding;$bad.$field=if($field -eq 'source_revision'){'0'*40}else{'other.context'}
    Assert ((Get-SageSensFindingReview -Finding $bad @context).status -eq 'BLOCKED') "finding context mismatch: $field"
}
foreach($field in @('auto_execute','authority')){
    $bad=Clone $finding;$bad.$field=if($field -eq 'auto_execute'){$true}else{'APPROVED'}
    Assert ((Get-SageSensFindingReview -Finding $bad @context).status -eq 'BLOCKED') "finding cannot grant $field"
}
$registry=ReadJson (Join-Path $sensRoot 'registry.json');$manifest=ReadJson (Join-Path $sensRoot 'manifest.json')
Assert (Test-SageSensDocument $registry).valid 'proposal registry schema'
$forgedRegistry=Clone $registry;$forgedRegistry.active_instances=@('sens.forged')
Assert (-not (Test-SageSensDocument $forgedRegistry).valid) 'proposal registry cannot claim a live instance'
Assert ($registry.entries.Count -eq 0 -and $registry.active_instances.Count -eq 0 -and -not $registry.self_activation_allowed) 'no fictitious registered SENS'
Assert (-not $manifest.transport_implemented -and -not $manifest.deployment_performed -and -not $manifest.auto_install) 'manifest exposes implementation limits'
$pwsh=(Get-Command pwsh).Source
$cli=& $pwsh -NoProfile -File (Join-Path $Root 'sage.ps1') sens
Assert ($LASTEXITCODE -eq 0 -and ($cli | ConvertFrom-Json).active_instances -eq 0) 'CLI status is offline'
$cli=& $pwsh -NoProfile -File (Join-Path $Root 'sage.ps1') sens -InputPath (Join-Path $sensRoot 'registration.example.json')
Assert ($LASTEXITCODE -eq 0 -and ($cli | ConvertFrom-Json).status -eq 'PROPOSAL_ONLY') 'CLI registration review is not activation'
$cli=& $pwsh -NoProfile -File (Join-Path $Root 'sage.ps1') sens -InputPath (Join-Path $sensRoot 'examples\event.json') -Preview
Assert ($LASTEXITCODE -eq 0 -and ($cli | ConvertFrom-Json).accepted_count -eq 1) 'CLI local preview'
[pscustomobject]@{status='PASS';checks=$checks.Count;scope='CONTRACT_AND_OFFLINE_PREVIEW_ONLY';registered_instances=0;external_execution=$false;deployment_performed=$false} | ConvertTo-Json
