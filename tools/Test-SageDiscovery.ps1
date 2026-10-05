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
    $safeTool=Get-Content -Raw -LiteralPath (Join-Path $Root 'fixtures\v0.8\registries\tool-descriptor.json') | ConvertFrom-Json -Depth 100
    $safeTool.tool_id="tool.test.$($sideEffect.ToLowerInvariant())"
    $safeTool.capabilities=@('unsafe-test-capability')
    $safeTool.side_effect_class=$sideEffect
    [pscustomobject]@{
        source = "memory://$sideEffect"
        record_type = 'tool_descriptor'
        record = $safeTool
    }
}
$unsafeRegistry = [pscustomobject]@{ registry_path='memory'; records=@($unsafeRecords); count=@($unsafeRecords).Count }
$unsafeReadMatches = Find-SageCapabilities -Registry $unsafeRegistry -RequiredCapabilities @('unsafe-test-capability') -MaxSideEffect READ_ONLY
if ($unsafeReadMatches.match_count -ne 0) { throw 'READ_ONLY discovery must reject mutating, security-active and unknown side-effect classes.' }
$reversibleMutation = Find-SageCapabilities -Registry $unsafeRegistry -RequiredCapabilities @('unsafe-test-capability') -MaxSideEffect MUTATING
if ($reversibleMutation.match_count -ne 1 -or $reversibleMutation.matches[0].side_effect_class -ne 'LOCAL_REVERSIBLE') { throw 'MUTATING discovery must admit only the bounded local-reversible test tool.' }
$interfaces=Import-SageRegistrySet -Path (Join-Path $Root 'fixtures\v0.8\interfaces')
$interfaceFound=Find-SageCapabilities -Registry $interfaces -RequiredCapabilities @('json-schema-validation')
if ($interfaceFound.match_count -ne 2 -or $interfaceFound.interface_selection.status -ne 'RECOMMENDED' -or $interfaceFound.authority_granted -or $interfaceFound.external_execution) { throw 'Interface discovery must return safe advisory candidates.' }
$malformedInterface=[pscustomobject]@{record_type='agent_native_interface'}
$mixedInterfaces=[pscustomobject]@{records=@([pscustomobject]@{source='memory://malformed-interface';record=$malformedInterface})+@($interfaces.records)}
$mixedInterfaceResult=Find-SageCapabilities -Registry $mixedInterfaces -RequiredCapabilities @('json-schema-validation')
if ($mixedInterfaceResult.match_count -ne 2 -or $mixedInterfaceResult.interface_selection.rejected.Count -ne 1) { throw 'Malformed interface peer must be rejected without crashing valid candidate source resolution.' }
$badInterface=$interfaces.records[0].record | ConvertTo-Json -Depth 100 | ConvertFrom-Json -Depth 100
$badInterface.schema_version='sage-agent-interface/999'
$futureRegistry=[pscustomobject]@{records=@([pscustomobject]@{ source='memory://future'; record=$badInterface; record_type='agent_native_interface' })}
if ((Find-SageCapabilities -Registry $futureRegistry -RequiredCapabilities @('json-schema-validation')).match_count -ne 0) { throw 'Unvalidated future interface must never route through generic discovery.' }
$badInterface.PSObject.Properties.Remove('schema_version')
if ((Find-SageCapabilities -Registry $futureRegistry -RequiredCapabilities @('json-schema-validation')).match_count -ne 0) { throw 'Unversioned interface must never route through generic discovery.' }
$malformedProvider=[pscustomobject]@{record_type='provider_adapter';adapter_id='adapter.bad';scope_preservation=$true;capabilities=@('json-schema-validation')}
$malformedTool=[pscustomobject]@{record_type='tool_descriptor';tool_id='tool.bad';operations=@('json-schema-validation');side_effect_class='READ_ONLY'}
$malformedAgent=$registry.records | Where-Object { $_.record_type -eq 'agent_capability' } | ForEach-Object { $_.record | ConvertTo-Json -Depth 100 | ConvertFrom-Json -Depth 100 }
$malformedAgent.PSObject.Properties.Remove('schema_version')
$mixedRecords=@($malformedProvider,$malformedTool,$malformedAgent,$null) | ForEach-Object { [pscustomobject]@{source='memory://invalid';record=$_} }
$malformedResult=Find-SageCapabilities -Registry ([pscustomobject]@{records=@($mixedRecords)}) -RequiredCapabilities @('json-schema-validation')
if ($malformedResult.match_count -ne 0 -or $malformedResult.rejected.Count -ne 4) { throw 'Malformed legacy descriptors must be rejected individually without crashing or routing.' }
$mixedRegistry=[pscustomobject]@{records=@($mixedRecords)+@($registry.records)}
if ((Find-SageCapabilities -Registry $mixedRegistry -RequiredCapabilities @('json-schema-validation')).match_count -ne $found.match_count) { throw 'Malformed peers must not prevent valid legacy descriptor discovery.' }
[pscustomobject]@{status='PASS'; registry_records=$registry.count; read_matches=$found.match_count; unknown_matches=$none.match_count; unsafe_read_matches=$unsafeReadMatches.match_count; bounded_mutating_matches=$reversibleMutation.match_count; interface_matches=$interfaceFound.match_count; authority_granted=$false;external_execution=$false} | ConvertTo-Json -Depth 10
