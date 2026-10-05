Set-StrictMode -Version Latest
$root = Split-Path -Parent $PSScriptRoot
Import-Module (Join-Path $root 'runtime\production\SageAdapters.psm1') -Force
$registry = @{}
$files = @('agent-capability.json','tool-descriptor.json','provider-adapter.json') | ForEach-Object { Join-Path $root "fixtures\v0.8\registries\$_" }
$checks = 0; $failures = 0
function Assert-Sage([bool]$Condition,[string]$Name) { $script:checks++; if (-not $Condition) { $script:failures++; throw "FAIL: $Name" } }
foreach ($file in $files) {
    $descriptor = Get-Content -Raw -LiteralPath $file | ConvertFrom-Json -Depth 100
    Register-SageDescriptor -Registry $registry -Descriptor $descriptor | Out-Null
    Assert-Sage ($registry.descriptors.Count -gt 0) "registered $(Split-Path $file -Leaf)"
}
Assert-Sage ($registry.descriptors.Count -eq 3) 'all descriptor kinds registered'
$interface = Get-Content -Raw -LiteralPath (Join-Path $root 'fixtures\v0.8\interfaces\reference-validator-cli.json') | ConvertFrom-Json -Depth 100
Register-SageDescriptor -Registry $registry -Descriptor $interface | Out-Null
Assert-Sage ($registry.descriptors.Count -eq 4 -and $registry.descriptors[$interface.interface_id].registered_mode -eq 'OFFLINE') 'Agent-Native descriptor registered without execution'
$badInterface = $interface | ConvertTo-Json -Depth 100 | ConvertFrom-Json -Depth 100
$badInterface.interface_id = 'interface.invalid-preservation'
$badInterface.security.permission_preserved = $false
try { Register-SageDescriptor -Registry $registry -Descriptor $badInterface | Out-Null; throw 'unsafe interface accepted' } catch { Assert-Sage ($_.Exception.Message -like 'Invalid Agent-Native descriptor:*') 'unsafe interface rejected' }
Assert-Sage ($registry.descriptors.Count -eq 4) 'failed registration does not add descriptor'
$invalidTool = [pscustomobject]@{ record_type='tool_descriptor'; tool_id='tool.bad'; side_effect_class='READ_ONLY' }
try { Register-SageDescriptor -Registry $registry -Descriptor $invalidTool | Out-Null; throw 'schema-less tool accepted' } catch { Assert-Sage ($_.Exception.Message -like 'Invalid SAGE descriptor contract:*') 'schema-less generic tool rejected' }
Assert-Sage ($registry.descriptors.Count -eq 4) 'invalid generic descriptor does not mutate registry'
$duplicate = Get-Content -Raw -LiteralPath $files[0] | ConvertFrom-Json -Depth 100
try { Register-SageDescriptor -Registry $registry -Descriptor $duplicate | Out-Null; throw 'duplicate accepted' } catch { Assert-Sage ($_.Exception.Message -like 'Duplicate SAGE descriptor:*') 'duplicate rejected' }
$bad = [pscustomobject]@{ record_type='provider_adapter'; adapter_id='bad.adapter'; provider='fixture'; scope_preservation=$false; permission_preservation=$true; authority_preservation=$true; evidence_preservation=$true }
try { Register-SageDescriptor -Registry $registry -Descriptor $bad | Out-Null; throw 'unsafe provider accepted' } catch { Assert-Sage ($_.Exception.Message -like 'Provider descriptor must preserve scope*') 'unsafe provider rejected' }
[pscustomobject]@{ status=if ($failures -eq 0) { 'PASS' } else { 'FAIL' }; checks=$checks; failures=$failures; registered=$registry.descriptors.Count; external_execution=$false } | ConvertTo-Json -Compress
