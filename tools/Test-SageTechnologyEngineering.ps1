[CmdletBinding()]
param([string]$Root)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
if (-not $Root) { $Root=Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path) }
Import-Module (Join-Path $Root 'runtime\reference\SageTechnologyEngineering.psm1') -Force
Import-Module (Join-Path $Root 'runtime\production\SageLifecycle.psm1') -Force
$fixtureRoot=Join-Path $Root 'fixtures\extensions\technology-engineering'
$extensionRoot=Join-Path $Root 'extensions\technology-engineering'
$passed=[System.Collections.Generic.List[string]]::new()
function Assert([bool]$Condition,[string]$Name) { if(-not $Condition){throw "Technology engineering test failed: $Name"}; $passed.Add($Name) }
function Clone($Value) { $Value | ConvertTo-Json -Depth 100 | ConvertFrom-Json -Depth 100 -DateKind String }
function ReadJson([string]$Path) { Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json -Depth 100 -DateKind String }
$base=ReadJson (Join-Path $fixtureRoot 'keep-current-stack.json')
$browser=ReadJson (Join-Path $fixtureRoot 'browser-polyglot.json')
$engine=ReadJson (Join-Path $fixtureRoot 'engine-constrained.json')
$model=ReadJson (Join-Path $fixtureRoot 'architecture-model.json')
$catalog=ReadJson (Join-Path $extensionRoot 'specialists.json')
$manifest=ReadJson (Join-Path $extensionRoot 'manifest.json')
foreach($fixture in @($base,$browser,$engine)) {
    Assert (Test-SageTechnologyRecord $fixture) "$($fixture.decision_id) schema"
    $review=Get-SageTechnologyDecisionReview $fixture -ArchitectureModel $model
    Assert ($review.status -eq 'READY_FOR_REVIEW') "$($fixture.decision_id) plan review"
    Assert ($review.pending_checks.Count -ge 2) "$($fixture.decision_id) NOT RUN stays pending"
    Assert (-not $review.authority_granted -and -not $review.external_execution) "$($fixture.decision_id) no authority"
    Assert ((Get-SageTechnologyDecisionReview $fixture -Phase VERIFY).status -eq 'BLOCKED') "$($fixture.decision_id) not project proof"
}
Assert ((Get-SageTechnologyDecisionReview $base).selected_candidate -eq 'candidate.powershell') 'no forced Rust migration'
Assert ((Get-SageTechnologyDecisionReview $engine).selected_candidate -eq 'candidate.csharp') 'single constrained platform option allowed'
$view=New-SageTechnologyDecisionView $base
Assert ($view.status -eq 'GENERATED_SOURCE_ONLY' -and -not $view.rendered -and -not $view.authority_granted) 'decision view is not approval or rendered output'
Assert ($view.mermaid.Contains('component.validation-cli') -and $view.mermaid.Contains('PowerShell') -and $view.mermaid.Contains('c0 -->|proposed selection| gate')) 'view derived from selected candidate and stable ID'
$labelProbe=Clone $base; $labelProbe.candidates[0].runtime="unsafe `"<script>`nlabel"
$labelView=New-SageTechnologyDecisionView $labelProbe
Assert (-not $labelView.mermaid.Contains('<script>') -and -not $labelView.mermaid.Contains("`nlabel")) 'diagram labels encode markup and control characters'
Assert ((New-SageTechnologyDecisionView $null).status -eq 'BLOCKED') 'invalid decision has no view'
Assert ((Get-SageTechnologyDecisionReview $null).status -eq 'BLOCKED') 'null fails closed'
Assert ((Get-SageTechnologyDecisionReview 42).status -eq 'BLOCKED') 'scalar fails closed'
Assert ((Get-SageTechnologyDecisionReview $base -TaskId 'another.task').status -eq 'BLOCKED') 'task mismatch'
$badModel=Clone $model; $badModel.model_version='another.version'
Assert ((Get-SageTechnologyDecisionReview $base -ArchitectureModel $badModel).status -eq 'BLOCKED') 'model version mismatch'
$badModel=Clone $model; $badModel.elements=@($badModel.elements | Where-Object architecture_id -NE $base.component_id)
Assert ((Get-SageTechnologyDecisionReview $base -ArchitectureModel $badModel).status -eq 'BLOCKED') 'unresolved component ID'

$mutations=@(
    @{name='missing selection';change={param($x) $x.PSObject.Properties.Remove('selection')}},
    @{name='unknown selected candidate';change={param($x) $x.selection.candidate_id='candidate.absent'}},
    @{name='duplicate candidate';change={param($x) $x.candidates+=Clone $x.candidates[0]}},
    @{name='case ambiguous candidate';change={param($x) $c=Clone $x.candidates[0];$c.candidate_id=$c.candidate_id.ToUpperInvariant();$x.candidates+=$c}},
    @{name='duplicate evidence';change={param($x) $x.evidence+=Clone $x.evidence[0]}},
    @{name='duplicate constraint';change={param($x) $x.constraints+=Clone $x.constraints[0]}},
    @{name='duplicate check';change={param($x) $x.validation_plan+=Clone $x.validation_plan[0]}},
    @{name='duplicate constraint result';change={param($x) $x.candidates[0].constraint_results+=Clone $x.candidates[0].constraint_results[0]}},
    @{name='unknown constraint result';change={param($x) $x.candidates[0].constraint_results[0].constraint_id='absent.constraint'}},
    @{name='unknown mandatory result';change={param($x) $x.candidates[0].constraint_results[0].status='UNKNOWN'}},
    @{name='unsatisfied mandatory result';change={param($x) $x.candidates[0].constraint_results[0].status='UNSATISFIED'}},
    @{name='missing mandatory result';change={param($x) $x.candidates[0].constraint_results=@()}},
    @{name='unsupported constraint assertion';change={param($x) $x.candidates[0].constraint_results[0].evidence_refs=@()}},
    @{name='missing document reference';change={param($x) $x.candidates[0].documentation_refs=@('doc.absent')}},
    @{name='cross candidate document';change={param($x) $x.candidates[0].documentation_refs=@('doc.rust')}},
    @{name='document NOT RUN';change={param($x) $x.evidence[0].status='NOT_RUN'}},
    @{name='non https document';change={param($x) $x.evidence[0].source_ref='file:///private/local'}},
    @{name='wrong evidence subject';change={param($x) $x.evidence[0].subject_candidate_id='candidate.absent'}},
    @{name='stale revision';change={param($x) $x.evidence[0].subject_revision='old.revision'}},
    @{name='unversioned source';change={param($x) $x.evidence[0].version='latest'}},
    @{name='invalid observation date';change={param($x) $x.evidence[0].observed_at='not-a-date'}},
    @{name='unmeasured performance claim';change={param($x) $x.selection.performance_claim='MEASURED'}},
    @{name='performance constraint backed only by docs';change={param($x) $x.constraints[0].kind='PERFORMANCE'}},
    @{name='missing build plan';change={param($x) $x.validation_plan=@($x.validation_plan | Where-Object kind -NE 'BUILD')}},
    @{name='optional build is not required build';change={param($x) $x.validation_plan[0].required=$false}},
    @{name='required check FAIL';change={param($x) $x.validation_plan[0].status='FAIL'}},
    @{name='check PASS without evidence';change={param($x) $x.validation_plan[0].status='PASS'}},
    @{name='document masquerading as build';change={param($x) $x.validation_plan[0].status='PASS';$x.validation_plan[0].evidence_refs=@('doc.powershell')}},
    @{name='extra authority field';change={param($x) $x | Add-Member NoteProperty authority_granted $true}}
)
foreach($mutation in $mutations) {
    $bad=Clone $base; & $mutation.change $bad
    try { $review=Get-SageTechnologyDecisionReview $bad } catch { throw "Unexpected error in mutation '$($mutation.name)': $_" }
    Assert ($review.status -eq 'BLOCKED') $mutation.name
}
$bad=Clone $browser; $bad.selection.PSObject.Properties.Remove('added_language_cost_rationale')
Assert ((Get-SageTechnologyDecisionReview $bad).status -eq 'BLOCKED') 'extra language needs cost rationale'
$bad=Clone $browser; $bad.validation_plan=@($bad.validation_plan | Where-Object kind -NE 'COMPATIBILITY')
Assert ((Get-SageTechnologyDecisionReview $bad).status -eq 'BLOCKED') 'extra language needs compatibility check'
$bad=Clone $engine; $bad.PSObject.Properties.Remove('single_option_rationale')
Assert ((Get-SageTechnologyDecisionReview $bad).status -eq 'BLOCKED') 'single option needs explicit reason'

# Test-only synthetic receipts exercise local integrity, NOT actual compiler output.
$receiptRoot=Join-Path $Root ('tmp\technology-tests-'+[Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $receiptRoot | Out-Null
$receiptPath=Join-Path $receiptRoot 'synthetic-receipt.txt'
'Synthetic unit-test artifact; not build/test execution evidence.' | Set-Content -LiteralPath $receiptPath -Encoding utf8
$receiptHash=(Get-FileHash -LiteralPath $receiptPath -Algorithm SHA256).Hash.ToLowerInvariant()
$project=Clone $base; $project.record_context='PROJECT'
foreach($kind in @('BUILD','TEST')) {
    $id='receipt.'+$kind.ToLowerInvariant()
    $project.evidence+=[pscustomobject]@{evidence_id=$id;kind=$kind;status='PASS';source_ref='test-harness://synthetic';version='test-harness/1';observed_at='2026-10-14T00:00:00Z';subject_candidate_id=$project.selection.candidate_id;subject_revision=$project.project_revision;artifact_ref='synthetic-receipt.txt';sha256=$receiptHash;environment='SYNTHETIC_UNIT_TEST_NOT_A_COMPILER'}
    $check=@($project.validation_plan | Where-Object kind -EQ $kind)[0]; $check.status='PASS';$check.evidence_refs=@($id)
}
$review=Get-SageTechnologyDecisionReview $project -Phase VERIFY -EvidenceRoot $receiptRoot
Assert ($review.status -eq 'READY_FOR_REVIEW' -and $review.evidence_trust -like '*NOT_ATTESTED_EXECUTION') 'integrity does not attest execution'
Assert (-not $review.authority_granted) 'receipt integrity never grants approval'
$bad=Clone $project; $bad.evidence[-1].sha256=('0'*64)
Assert ((Get-SageTechnologyDecisionReview $bad -Phase VERIFY -EvidenceRoot $receiptRoot).status -eq 'BLOCKED') 'tampered receipt'
foreach($unsafePath in @('../synthetic-receipt.txt','C:\Windows\win.ini','https://example.test/receipt','missing.txt')) {
    $bad=Clone $project;$bad.evidence[-1].artifact_ref=$unsafePath
    Assert ((Get-SageTechnologyDecisionReview $bad -Phase VERIFY -EvidenceRoot $receiptRoot).status -eq 'BLOCKED') "reject outside/missing receipt: $unsafePath"
}
$bad=Clone $project; $bad.record_context='REFERENCE_FIXTURE'
Assert ((Get-SageTechnologyDecisionReview $bad -Phase VERIFY -EvidenceRoot $receiptRoot).status -eq 'BLOCKED') 'fixture cannot become project proof'
if ([OperatingSystem]::IsWindows()) {
    $otherRoot=Join-Path $Root ('tmp\technology-link-target-'+[Guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $otherRoot | Out-Null
    Copy-Item -LiteralPath $receiptPath -Destination (Join-Path $otherRoot 'synthetic-receipt.txt')
    New-Item -ItemType Junction -Path (Join-Path $receiptRoot 'linked') -Target $otherRoot | Out-Null
    $bad=Clone $project;$bad.evidence[-1].artifact_ref='linked/synthetic-receipt.txt'
    Assert ((Get-SageTechnologyDecisionReview $bad -Phase VERIFY -EvidenceRoot $receiptRoot).status -eq 'BLOCKED') 'matching hash through junction still rejected'
}

Assert (Test-SageTechnologyRecord $catalog) 'catalog schema'
Assert (Test-SageTechnologyRecord (ReadJson (Join-Path $extensionRoot 'policy.json'))) 'policy schema'
Assert ($catalog.profiles.Count -eq 17 -and $manifest.skills.Count -eq 18) '17 profiles and 18 optional skills'
Assert ($manifest.compatible_core -eq 'sage/0.8.4' -and -not $manifest.installed_into_host -and -not $manifest.external_execution) 'local extension is not host installation'
$coreRegistry=ReadJson (Join-Path $Root 'skills\registry.json')
$coreBundle=ReadJson (Join-Path $Root 'bundles\v0.8\core-engineering\bundle.json')
Assert ($coreRegistry.skills.Count -eq 8 -and $coreBundle.skills.Count -eq 8) 'preserve eight core skills'
Assert ($coreRegistry.optional_extensions -contains 'extensions/technology-engineering/manifest.json' -and $coreBundle.optional_extensions -contains 'extensions/technology-engineering/manifest.json') 'extension registered in discovery metadata'
foreach($skill in $manifest.skills) {
    $skillPath=Join-Path $extensionRoot "skills\$skill\SKILL.md"
    Assert (Test-Path -LiteralPath $skillPath -PathType Leaf) "skill exists: $skill"
    $body=Get-Content -LiteralPath $skillPath -Raw
    Assert ($body -match ('(?s)\A---\r?\nname: '+[regex]::Escape($skill)+'\r?\ndescription: [^\r\n]+\r?\n---')) "skill metadata: $skill"
}
$routes=Find-SageSpecialistProfiles $catalog -RequiredCapabilities @('language.powershell','engineering.review')
Assert ($routes.status -eq 'MATCHES' -and $routes.match_count -eq 2) 'route only necessary distinct declared roles'
Assert (-not $routes.authority_granted -and -not $routes.external_execution) 'routing is advisory'
$overlapCatalog=Clone $catalog;$duplicateRole=Clone $overlapCatalog.profiles[0];$duplicateRole.profile_id='alternate-rust';$overlapCatalog.profiles+=$duplicateRole
$overlap=Find-SageSpecialistProfiles $overlapCatalog -RequiredCapabilities @('language.rust','systems.concurrent')
Assert ($overlap.status -eq 'MATCHES' -and $overlap.candidate_count -eq 2 -and $overlap.match_count -eq 1) 'do not select every overlapping specialist'
Assert ((Find-SageSpecialistProfiles $catalog -RequiredCapabilities @('unknown.capability')).status -eq 'NO_MATCH') 'unknown capability not substituted'
Assert ((Find-SageSpecialistProfiles $catalog -RequiredCapabilities @('language.rust','unknown.capability')).status -eq 'NO_MATCH') 'partial capability coverage not success'
$badCatalog=Clone $catalog; $badCatalog.profiles+=Clone $badCatalog.profiles[0]
Assert ((Find-SageSpecialistProfiles $badCatalog -RequiredCapabilities @('language.rust')).status -eq 'BLOCKED') 'duplicate profile fails closed'
$badCatalog=Clone $catalog; $badCatalog.profiles[0].execution_verified=$true
Assert ((Find-SageSpecialistProfiles $badCatalog -RequiredCapabilities @('language.rust')).status -eq 'BLOCKED') 'unproven execution cannot be declared verified'
$badCatalog=Clone $catalog; $badCatalog.profiles[0].skill_ref='../private/SKILL.md'
Assert ((Find-SageSpecialistProfiles $badCatalog -RequiredCapabilities @('language.rust')).status -eq 'BLOCKED') 'outside skill reference'
if ([OperatingSystem]::IsWindows()) {
    $linkedExtension=Join-Path $receiptRoot 'linked-extension'
    New-Item -ItemType Directory -Path $linkedExtension | Out-Null
    New-Item -ItemType Junction -Path (Join-Path $linkedExtension 'skills') -Target (Join-Path $extensionRoot 'skills') | Out-Null
    Assert ((Find-SageSpecialistProfiles $catalog -RequiredCapabilities @('language.rust') -ExtensionRoot $linkedExtension).status -eq 'BLOCKED') 'skill directory junction fails closed'
}

$runText=Get-Content (Join-Path $Root 'fixtures\v0.8\r2-feature-data-path.json') -Raw
$run=$runText.Replace('task.r2.feature.001',$base.task_id) | ConvertFrom-Json -Depth 100 -DateKind String
$registry=Join-Path $Root 'fixtures\v0.8\registries'
$args=@{RunContract=$run;RegistryPath=$registry;LedgerPath=(Join-Path $receiptRoot 'lifecycle.json');RequireTechnologyDecision=$true}
$result=Invoke-SageLifecycle @args
Assert ($result.status -eq 'BLOCKED' -and $result.final_stage -eq 'plan') 'required missing decision stops lifecycle'
$args.TechnologyDecision=$base; $result=Invoke-SageLifecycle @args
Assert ($result.status -eq 'DONE' -and $result.external_execution -eq 'NOT_PERFORMED') 'decision-aware dry-run lifecycle'
Assert ($result.stages.Count -eq 5 -and -not $result.plan.specialists_instantiated) 'preserve five stages; do not spawn agents'
Assert ($result.plan.specialist_profiles.Count -eq 2) 'specialist references included in plan'
$ledger=ReadJson $args.LedgerPath
Assert (@($ledger.entries | Where-Object { $_.kind -eq 'TECHNOLOGY_REVIEW' -and $_.status -eq 'ADVISORY_ONLY' -and $_.ref -match '/sha256/[a-f0-9]{64}$' }).Count -eq 1) 'ledger links decision content hash'
$bad=Clone $base; $bad.task_id='another.task';$args.TechnologyDecision=$bad
Assert ((Invoke-SageLifecycle @args).status -eq 'BLOCKED') 'lifecycle rejects wrong task decision'
$bad=Clone $base;$bad.required_specialist_capabilities=@('unknown.capability');$args.TechnologyDecision=$bad
Assert ((Invoke-SageLifecycle @args).status -eq 'BLOCKED') 'lifecycle rejects unroutable role'
$bad=Clone $base;$bad.required_specialist_capabilities=@('language.python','engineering.review');$args.TechnologyDecision=$bad
Assert ((Invoke-SageLifecycle @args).status -eq 'BLOCKED') 'wrong language specialist cannot implement selected stack'

$pwsh=(Get-Command pwsh).Source
$cliOutput=& $pwsh -NoProfile -File (Join-Path $Root 'sage.ps1') technology -DecisionPath (Join-Path $fixtureRoot 'keep-current-stack.json')
Assert ($LASTEXITCODE -eq 0 -and ($cliOutput | ConvertFrom-Json).status -eq 'READY_FOR_REVIEW') 'CLI planning review'
$cliOutput=& $pwsh -NoProfile -File (Join-Path $Root 'sage.ps1') technology -DecisionPath (Join-Path $fixtureRoot 'keep-current-stack.json') -Phase VERIFY
Assert ($LASTEXITCODE -eq 2 -and ($cliOutput | ConvertFrom-Json).status -eq 'BLOCKED') 'CLI machine-readable verification failure'
$global:LASTEXITCODE=0
foreach($source in @(@{name='AI_Engineering_Agent_Team_Blueprint_FA_2026-10-14_v0.2.md';hash='466d5222f27389fdddd1824141c6c49f3d6e8b4190f2046931c97c99647dab25'},@{name='AI_Engineering_Agent_Team_Starter_v0.2.zip';hash='1542658e50cfdd227ca068a061437caa6b7305dab74c7e74782b66e0055e20fe'})) {
    Assert ((Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $Root ('sources\supplied-originals\'+$source.name))).Hash.ToLowerInvariant() -eq $source.hash) "preserved original: $($source.name)"
}
[pscustomobject]@{status='PASS';checks=$passed.Count;profiles=17;optional_skills=18;fixtures=3;external_execution=$false;proof_scope='REFERENCE_VALIDATION_AND_ROUTING_NOT_ALL_LANGUAGE_TOOLCHAINS'} | ConvertTo-Json -Depth 10
