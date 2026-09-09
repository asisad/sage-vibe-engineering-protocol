[CmdletBinding()]
param([string]$Root,[string]$Capability='json-schema-validation')
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
if ([string]::IsNullOrWhiteSpace($Root)) {$Root=Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)}
Import-Module (Join-Path $Root 'runtime\reference\SageDiscovery.psm1') -Force
$registry=Import-SageRegistrySet -Path (Join-Path $Root 'fixtures\v0.8\registries')
$found=Find-SageCapabilities -Registry $registry -RequiredCapabilities @($Capability) -MaxSideEffect READ_ONLY
if ($registry.count -ne 3 -or $found.match_count -lt 1) { throw 'Capability discovery failed.' }
$none=Find-SageCapabilities -Registry $registry -RequiredCapabilities @('capability-that-does-not-exist')
if ($none.match_count -ne 0) { throw 'Unknown capability must return no matches.' }
$unsafeRecords = foreach ($sideEffect in @('LOCAL_REVERSIBLE','LOCAL_DESTRUCTIVE','EXTERNAL_MUTATION','SECURITY_ACTIVE','UNKNOWN')) {
    [pscustomobject]@{
        source = "memory://$sideEffect"
        record_type = 'tool_descriptor'
        record = [pscustomobject]@{
            record_type = 'tool_descriptor'
            tool_id = "tool.test.$($sideEffect.ToLowerInvariant())"
            capabilities = @('unsafe-test-capability')
            side_effect_class = $sideEffect
        }
    }
}
$unsafeRegistry = [pscustomobject]@{ registry_path='memory'; records=@($unsafeRecords); count=@($unsafeRecords).Count }
$unsafeReadMatches = Find-SageCapabilities -Registry $unsafeRegistry -RequiredCapabilities @('unsafe-test-capability') -MaxSideEffect READ_ONLY
if ($unsafeReadMatches.match_count -ne 0) { throw 'READ_ONLY discovery must reject mutating, security-active and unknown side-effect classes.' }
$reversibleMutation = Find-SageCapabilities -Registry $unsafeRegistry -RequiredCapabilities @('unsafe-test-capability') -MaxSideEffect MUTATING
if ($reversibleMutation.match_count -ne 1 -or $reversibleMutation.matches[0].side_effect_class -ne 'LOCAL_REVERSIBLE') { throw 'MUTATING discovery must admit only the bounded local-reversible test tool.' }
[pscustomobject]@{status='PASS'; registry_records=$registry.count; read_matches=$found.match_count; unknown_matches=$none.match_count; unsafe_read_matches=$unsafeReadMatches.match_count; bounded_mutating_matches=$reversibleMutation.match_count} | ConvertTo-Json -Depth 10
