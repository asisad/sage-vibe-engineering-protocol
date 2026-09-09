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
$duplicate = Get-Content -Raw -LiteralPath $files[0] | ConvertFrom-Json -Depth 100
try { Register-SageDescriptor -Registry $registry -Descriptor $duplicate | Out-Null; throw 'duplicate accepted' } catch { Assert-Sage ($_.Exception.Message -like 'Duplicate SAGE descriptor:*') 'duplicate rejected' }
$bad = [pscustomobject]@{ record_type='provider_adapter'; adapter_id='bad.adapter'; provider='fixture'; scope_preservation=$false; permission_preservation=$true; authority_preservation=$true; evidence_preservation=$true }
try { Register-SageDescriptor -Registry $registry -Descriptor $bad | Out-Null; throw 'unsafe provider accepted' } catch { Assert-Sage ($_.Exception.Message -like 'Provider descriptor must preserve scope*') 'unsafe provider rejected' }
[pscustomobject]@{ status=if ($failures -eq 0) { 'PASS' } else { 'FAIL' }; checks=$checks; failures=$failures; registered=$registry.descriptors.Count; external_execution=$false } | ConvertTo-Json -Compress
