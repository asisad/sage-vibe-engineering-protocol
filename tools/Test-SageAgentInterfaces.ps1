[CmdletBinding()]
param([string]$Root)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($Root)) { $Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path) }
$schema = Get-Content -Raw (Join-Path $Root 'schemas\v0.8\sage-agent-interface.schema.json') | ConvertFrom-Json -Depth 20
if ($schema.properties.record_type.const -ne 'agent_native_interface') { throw 'Agent interface schema record type invalid.' }
if (($schema.required -notcontains 'layers') -or ($schema.required -notcontains 'security')) { throw 'Agent interface schema is incomplete.' }
$policy = Get-Content -Raw (Join-Path $Root 'policies\v0.8\agent-interface-policy.json') | ConvertFrom-Json -Depth 20
if (($policy.preferred_path -join '|') -ne 'NATIVE_API|THIN_BRIDGE|TYPED_CLI_OR_MCP|SKILL') { throw 'Interface policy layering invalid.' }
Import-Module (Join-Path $Root 'runtime\reference\SageAgentInterfaces.psm1') -Force
$checks=0
function Assert-Interface([bool]$Condition,[string]$Name) { $script:checks++; if (-not $Condition) { throw "FAIL: $Name" } }
function Copy-Descriptor($Value) { $Value | ConvertTo-Json -Depth 100 | ConvertFrom-Json -Depth 100 }
$descriptors=@(Get-ChildItem -LiteralPath (Join-Path $Root 'fixtures\v0.8\interfaces') -Filter '*.json' | ForEach-Object { Get-Content -Raw -LiteralPath $_.FullName | ConvertFrom-Json -Depth 100 })
Assert-Interface ($descriptors.Count -ge 2) 'CLI and MCP fixtures exist'
foreach ($descriptor in $descriptors) {
    $validation=Test-SageAgentInterface -Descriptor $descriptor
    Assert-Interface $validation.valid "valid descriptor $($descriptor.interface_id)"
    Assert-Interface (-not $validation.authority_granted -and -not $validation.external_execution) 'validation grants no authority'
}
$cli=$descriptors | Where-Object { $_.layers.callable_surface -eq 'CLI' } | Select-Object -First 1
$mcp=$descriptors | Where-Object { $_.layers.callable_surface -eq 'MCP' } | Select-Object -First 1
$selected=Select-SageAgentInterface -Descriptors $descriptors -RequiredCapabilities @('json-schema-validation')
Assert-Interface ($selected.status -eq 'RECOMMENDED' -and $selected.selected.interface_id -eq $cli.interface_id) 'deterministic smallest compatible surface selection'
Assert-Interface (-not $selected.authority_granted -and -not $selected.external_execution) 'recommendation is advisory'
$selectedMcp=Select-SageAgentInterface -Descriptors $descriptors -RequiredCapabilities @('json-schema-validation') -Surface MCP
Assert-Interface ($selectedMcp.selected.interface_id -eq $mcp.interface_id) 'explicit MCP request'
$unknown=Select-SageAgentInterface -Descriptors $descriptors -RequiredCapabilities @('unknown-capability')
Assert-Interface ($unknown.status -eq 'NO_MATCH' -and $null -eq $unknown.selected) 'capability mismatch fails closed'
$empty=Select-SageAgentInterface -Descriptors @() -RequiredCapabilities @('json-schema-validation')
Assert-Interface ($empty.status -eq 'NO_MATCH') 'empty registry fails closed'
Assert-Interface (-not (Test-SageAgentInterface -Descriptor $null).valid) 'null malformed descriptor rejected'
Assert-Interface ((Select-SageAgentInterface -Descriptors @($null) -RequiredCapabilities @('json-schema-validation')).status -eq 'NO_MATCH') 'null registry entry fails closed'
foreach ($missing in @('schema_version','version','capabilities','decision_rationale','contract','verification')) {
    $bad=Copy-Descriptor $cli; $bad.PSObject.Properties.Remove($missing)
    Assert-Interface (-not (Test-SageAgentInterface -Descriptor $bad).valid) "missing $missing rejected"
}
foreach ($preservation in @('scope_preserved','permission_preserved','authority_preserved','evidence_preserved','secrets_redacted')) {
    $bad=Copy-Descriptor $cli; $bad.security.$preservation=$false
    Assert-Interface (-not (Test-SageAgentInterface -Descriptor $bad).valid) "$preservation loss rejected"
}
$bad=Copy-Descriptor $cli; $bad.schema_version='sage-agent-interface/999'
Assert-Interface (-not (Test-SageAgentInterface -Descriptor $bad).valid) 'future incompatible schema rejected'
$bad=Copy-Descriptor $cli; $bad.version='unversioned'
Assert-Interface (-not (Test-SageAgentInterface -Descriptor $bad).valid) 'invalid descriptor version rejected'
$bad=Copy-Descriptor $cli; $bad.security.side_effect_class='UNKNOWN'
Assert-Interface ((Select-SageAgentInterface -Descriptors @($bad) -RequiredCapabilities @('json-schema-validation')).status -eq 'NO_MATCH') 'unknown side effects fail closed'
foreach ($requiredFeature in @('version_handshake','cancellation','json_output','typed_errors')) {
    $bad=Copy-Descriptor $cli; $bad.contract.$requiredFeature=$false
    Assert-Interface (-not (Test-SageAgentInterface -Descriptor $bad).valid) "missing $requiredFeature guarantee rejected"
}
$allCapabilities=Select-SageAgentInterface -Descriptors $descriptors -RequiredCapabilities @('json-schema-validation','missing-capability')
Assert-Interface ($allCapabilities.status -eq 'NO_MATCH') 'all required capabilities must match'
$bad=Copy-Descriptor $cli; $bad.contract.timeout_seconds=121
Assert-Interface ((Test-SageAgentInterface -Descriptor $bad).errors -contains 'INVALID_TIMEOUT_BOUNDS') 'timeout relational bounds checked'
$bad=Copy-Descriptor $mcp; $bad.security.network_authentication='NOT_APPLICABLE'
Assert-Interface ((Test-SageAgentInterface -Descriptor $bad).errors -contains 'NETWORK_AUTHENTICATION_REQUIRED') 'unauthenticated localhost denied'
$bad=Copy-Descriptor $cli; $bad.contract.error_codes=@('INVALID_INPUT')
Assert-Interface (-not (Test-SageAgentInterface -Descriptor $bad).valid) 'incomplete error taxonomy rejected'
$bad=Copy-Descriptor $cli; $bad.verification.evidence_refs=@()
Assert-Interface (-not (Test-SageAgentInterface -Descriptor $bad).valid) 'missing evidence refs rejected'
$direct=Copy-Descriptor $cli; $direct.layers.callable_surface='NATIVE_API'; $direct.contract.transport='IN_PROCESS'; $direct.decision='ADOPT'
Assert-Interface (Test-SageAgentInterface -Descriptor $direct).valid 'direct native binding without bridge accepted'
$direct.layers.PSObject.Properties.Remove('bridge')
Assert-Interface (Test-SageAgentInterface -Descriptor $direct).valid 'omitted optional bridge accepted'
# The test variants must use distinct identifiers to avoid ambiguous registry identity.
$direct.interface_id='interface.reference.direct'
$directSelected=Select-SageAgentInterface -Descriptors @($cli,$direct) -RequiredCapabilities @('json-schema-validation')
Assert-Interface ($directSelected.selected.interface_id -eq $direct.interface_id) 'ADOPT direct native binding preferred'
$duplicate=Select-SageAgentInterface -Descriptors @($cli,(Copy-Descriptor $cli)) -RequiredCapabilities @('json-schema-validation')
Assert-Interface ($duplicate.status -eq 'NO_MATCH' -and $duplicate.rejected[0].reasons -contains 'DUPLICATE_INTERFACE_ID') 'ambiguous identity denied'
$shadow=Copy-Descriptor $cli; $shadow.schema_version='sage-agent-interface/999'
$shadowSelection=Select-SageAgentInterface -Descriptors @($cli,$shadow) -RequiredCapabilities @('json-schema-validation')
Assert-Interface ($shadowSelection.status -eq 'NO_MATCH') 'conflicting invalid shadow descriptor denies ambiguous identity'
$dual=Copy-Descriptor $cli; $dual.layers.callable_surface='CLI_AND_MCP'; $dual.interface_id='interface.reference.dual'
Assert-Interface ((Select-SageAgentInterface -Descriptors @($dual) -RequiredCapabilities @('json-schema-validation') -Surface MCP).status -eq 'RECOMMENDED') 'dual surface satisfies requested MCP capability'
$bad=Copy-Descriptor $cli; $bad.contract.transport='LOCALHOST'; $bad.security.network_authentication='TOKEN'
Assert-Interface ((Test-SageAgentInterface -Descriptor $bad).errors -contains 'CLI_TRANSPORT_MISMATCH') 'inconsistent transport declaration rejected'
Assert-Interface (-not (Test-SageAgentInterface -Descriptor $cli -SchemaPath (Join-Path $Root 'missing-interface-schema.json')).valid) 'missing validation schema fails closed'
$bad=Copy-Descriptor $cli; $bad.decision_rationale='   '
Assert-Interface (-not (Test-SageAgentInterface -Descriptor $bad).valid) 'blank adoption rationale rejected'
foreach ($invalidReference in @('schemas/v0.8/does-not-exist.json','schemas/v0.8/sage-contracts.schema.json#/$defs/NotDefined','schemas/v0.8/sage-contracts.schema.json#/title','https://unapproved.example/schema.json','../out-of-scope.json','schemas/../schemas/v0.8/sage-contracts.schema.json',(Join-Path $Root 'schemas/v0.8/sage-contracts.schema.json'))) {
    foreach ($schemaField in @('input_schema_ref','output_schema_ref')) {
        $bad=Copy-Descriptor $cli; $bad.contract.$schemaField=$invalidReference
        $invalid=Test-SageAgentInterface -Descriptor $bad -Root $Root
        Assert-Interface ($invalid.errors -contains "SCHEMA_REFERENCE_INVALID:$schemaField") "bounded schema reference rejected in $schemaField"
        Assert-Interface ((Select-SageAgentInterface -Descriptors @($bad) -RequiredCapabilities @('json-schema-validation') -Root $Root).status -eq 'NO_MATCH') 'invalid schema reference cannot route'
    }
}
$mixed=Select-SageAgentInterface -Descriptors @($null,$cli) -RequiredCapabilities @('json-schema-validation')
Assert-Interface ($mixed.status -eq 'RECOMMENDED' -and $mixed.rejected[0].reasons -contains 'INVALID_DESCRIPTOR_INPUT') 'null mixed entry rejected while valid peer remains advisory'
foreach ($sideEffect in @('LOCAL_REVERSIBLE','LOCAL_DESTRUCTIVE','EXTERNAL_MUTATION','SECURITY_ACTIVE')) {
    $mutation=Copy-Descriptor $cli; $mutation.security.side_effect_class=$sideEffect
    Assert-Interface ((Test-SageAgentInterface -Descriptor $mutation).errors -contains 'MUTATION_DRY_RUN_REQUIRED') "$sideEffect requires dry run"
    $mutation.contract.dry_run=$true
    $restricted=Select-SageAgentInterface -Descriptors @($mutation) -RequiredCapabilities @('json-schema-validation')
    Assert-Interface ($restricted.status -eq 'NO_MATCH') "$sideEffect excluded from READ_ONLY"
    $bounded=Select-SageAgentInterface -Descriptors @($mutation) -RequiredCapabilities @('json-schema-validation') -MaxSideEffect MUTATING
    Assert-Interface (($bounded.status -eq 'RECOMMENDED') -eq ($sideEffect -eq 'LOCAL_REVERSIBLE')) "$sideEffect bounded side effect policy"
}
foreach ($path in @('docs\architecture\agent-native-interfaces.md','docs\architecture\cli-standard.md','docs\architecture\mcp-standard.md','docs\architecture\bridge-standard.md','docs\decisions\ADR-agent-interface-selection.md','docs\decisions\ADR-cli-anything-adoption.md','skills\interface-audit\SKILL.md','skills\mcp-review\SKILL.md','skills\cli-harness-review\SKILL.md')) {
  if (-not (Test-Path -LiteralPath (Join-Path $Root $path) -PathType Leaf)) { throw "Missing interface artifact: $path" }
}
[pscustomobject]@{ status = 'PASS'; checks=$checks; descriptor_count=$descriptors.Count; layers = @('NATIVE_API','THIN_BRIDGE','TYPED_CLI_OR_MCP','SKILL'); decisions = @('ADOPT','ADAPT','BUILD'); live_execution = $policy.live_execution; external_execution=$false } | ConvertTo-Json -Depth 10
