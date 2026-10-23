[CmdletBinding()]
param([Parameter(Position=0)][ValidateSet('validate','demo','discover','interfaces','specialists','technology','sens','operations','lifecycle','catalog','ci')][string]$Command='validate',[string]$Capability,[string]$RunPath,[string]$RegistryPath,[string]$LedgerPath,[string]$DecisionPath,[ValidateSet('PLAN','VERIFY')][string]$Phase='PLAN',[switch]$RequireTechnologyDecision,[string]$ArchitecturePath,[switch]$View,[string]$InputPath,[string]$ConfigPath,[switch]$Preview,[ValidateSet('list','search','show','plan')][string]$CatalogAction='list',[string]$Query,[string]$EntryId)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$root=$PSScriptRoot
$pwsh=(Get-Command pwsh -ErrorAction Stop).Source
switch ($Command) {
  'catalog' {
    $python=(Get-Command python -ErrorAction Stop).Source
    $catalogArgs=@((Join-Path $root 'extensions\ecc\sage_ecc.py'),$CatalogAction)
    switch ($CatalogAction) {
      'search' { if ([string]::IsNullOrWhiteSpace($Query)) { $Query=$Capability }; if ([string]::IsNullOrWhiteSpace($Query)) { throw 'catalog search requires -Query or -Capability' }; $catalogArgs+=@($Query) }
      'show' { if ([string]::IsNullOrWhiteSpace($EntryId)) { throw 'catalog show requires -EntryId' }; $catalogArgs+=@($EntryId) }
      'plan' { if ([string]::IsNullOrWhiteSpace($Query)) { throw 'catalog plan requires -Query' }; $catalogArgs+=@('--task',$Query) }
    }
    $catalogArgs+=@('--json')
    & $python @catalogArgs
  }
  'validate' { & $pwsh -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root 'tools\Test-SageContracts.ps1') }
  'demo' { & $pwsh -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root 'tools\Test-SageDemonstrator.ps1') }
  'discover' { if ([string]::IsNullOrWhiteSpace($Capability)) { throw 'discover requires -Capability' }; & $pwsh -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root 'tools\Test-SageDiscovery.ps1') -Capability $Capability }
  'operations' { & $pwsh -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root 'tools\Test-SageDeploymentRuntime.ps1') }
  'sens' {
    $sensRoot=Join-Path $root 'integrations\sens'
    Import-Module (Join-Path $sensRoot 'SageSens.psm1') -Force
    if (-not $InputPath) {
      $sensManifest=Get-Content -LiteralPath (Join-Path $sensRoot 'manifest.json') -Raw | ConvertFrom-Json
      $sensRegistry=Get-Content -LiteralPath (Join-Path $sensRoot 'registry.json') -Raw | ConvertFrom-Json
      $registryCheck=Test-SageSensDocument $sensRegistry
      if (-not $registryCheck.valid) { $registryCheck | ConvertTo-Json; exit 2 }
      [pscustomobject]@{status=$sensManifest.status;protocol=$sensManifest.protocol;integration_path='integrations/sens/';registration_proposals=@($sensRegistry.entries).Count;registered_instances=0;active_instances=0;transport_connected=$false;deployment_performed=$false;authority_granted=$false;external_execution=$false} | ConvertTo-Json -Depth 10
      break
    }
    $sensDocument=Get-Content -LiteralPath $InputPath -Raw | ConvertFrom-Json -Depth 40 -DateKind String
    $validation=Test-SageSensDocument $sensDocument
    if (-not $validation.valid) { $validation | ConvertTo-Json -Depth 10; exit 2 }
    switch ($sensDocument.record_type) {
      'sens_registration' { Get-SageSensRegistrationReview $sensDocument | ConvertTo-Json -Depth 10 }
      'sage_sens_event' {
        if (-not $ConfigPath) { $ConfigPath=Join-Path $sensRoot 'config.example.json' }
        $sensConfig=Get-Content -LiteralPath $ConfigPath -Raw | ConvertFrom-Json -Depth 40 -DateKind String
        if ($Preview) { $sensConfig.mode='PREVIEW_ONLY' }
        New-SageSensPreview -Config $sensConfig -Events @($sensDocument) | ConvertTo-Json -Depth 40
      }
      'sens_finding' { [pscustomobject]@{status='UNBOUND_OBSERVATION';context_checked=$false;evidence_verified=$false;authority_granted=$false;external_execution=$false} | ConvertTo-Json }
      default { $validation | ConvertTo-Json -Depth 10 }
    }
  }
  'specialists' {
    if ([string]::IsNullOrWhiteSpace($Capability)) { throw 'specialists requires -Capability' }
    Import-Module (Join-Path $root 'runtime\reference\SageDiscovery.psm1') -Force
    Find-SageEngineeringCapabilities -RequiredCapabilities @($Capability) | ConvertTo-Json -Depth 100
  }
  'technology' {
    if ([string]::IsNullOrWhiteSpace($DecisionPath)) { throw 'technology requires -DecisionPath' }
    Import-Module (Join-Path $root 'runtime\reference\SageTechnologyEngineering.psm1') -Force
    $decision=Get-Content -LiteralPath $DecisionPath -Raw | ConvertFrom-Json -Depth 100 -DateKind String
    $reviewArgs=@{Decision=$decision;Phase=$Phase}
    if ($ArchitecturePath) { $reviewArgs.ArchitectureModel=Get-Content -LiteralPath $ArchitecturePath -Raw | ConvertFrom-Json -Depth 100 -DateKind String }
    $review=Get-SageTechnologyDecisionReview @reviewArgs
    if ($View -and $review.status -ne 'BLOCKED') { $review | Add-Member NoteProperty view (New-SageTechnologyDecisionView $decision) }
    $review | ConvertTo-Json -Depth 100
    if ($review.status -eq 'BLOCKED') { exit 2 }
  }
  'interfaces' {
    if ([string]::IsNullOrWhiteSpace($Capability)) { $Capability = 'json-schema-validation' }
    if ([string]::IsNullOrWhiteSpace($RegistryPath)) { $RegistryPath = Join-Path $root 'fixtures\v0.8\interfaces' }
    Import-Module (Join-Path $root 'runtime\reference\SageDiscovery.psm1') -Force
    $registry = Import-SageRegistrySet -Path $RegistryPath
    Find-SageCapabilities -Registry $registry -RequiredCapabilities @($Capability) -MaxSideEffect READ_ONLY | ConvertTo-Json -Depth 100
  }
  'lifecycle' {
    if ([string]::IsNullOrWhiteSpace($RunPath)) { $RunPath=Join-Path $root 'fixtures\v0.8\r2-feature-data-path.json' }
    if ([string]::IsNullOrWhiteSpace($RegistryPath)) { $RegistryPath=Join-Path $root 'fixtures\v0.8\registries' }
    if ([string]::IsNullOrWhiteSpace($LedgerPath)) { $LedgerPath=Join-Path $root 'tmp\sage-lifecycle-ledger.json' }
    Import-Module (Join-Path $root 'runtime\production\SageLifecycle.psm1') -Force
    $contract=Get-Content -Raw -LiteralPath $RunPath | ConvertFrom-Json -Depth 100 -DateKind String
    $lifecycleArgs=@{RunContract=$contract;RegistryPath=$RegistryPath;LedgerPath=$LedgerPath;RequiredCapabilities=@('json-schema-validation');RequireTechnologyDecision=$RequireTechnologyDecision}
    if ($DecisionPath) { $lifecycleArgs.TechnologyDecision=Get-Content -LiteralPath $DecisionPath -Raw | ConvertFrom-Json -Depth 100 -DateKind String }
    Invoke-SageLifecycle @lifecycleArgs | ConvertTo-Json -Depth 30
  }
  'ci' { & $pwsh -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root 'tools\Invoke-SageReferenceCI.ps1') }
}
if (Test-Path variable:LASTEXITCODE) { if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } }
