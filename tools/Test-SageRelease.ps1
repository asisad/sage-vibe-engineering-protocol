[CmdletBinding()]
param([string]$Root)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
if ([string]::IsNullOrWhiteSpace($Root)) { $Root=Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path) }
$manifest=Get-Content -Raw -LiteralPath (Join-Path $Root 'RELEASE_MANIFEST_v0.8.3.json') | ConvertFrom-Json -Depth 50
$required=@('README.md','docs\QUICKSTART.fa-en.md','sdk\python\pyproject.toml','sdk\python\src\sage_sdk\__init__.py','sdk\python\src\sage_sdk\contracts.py','sdk\python\src\sage_sdk\cli.py','RELEASE_MANIFEST_v0.8.3.json','SAGE_v0.8.3_STABLE_RELEASE.md','skills\registry.json','bundles\v0.8\core-engineering\bundle.json','runtime\production\SageLifecycle.psm1','tools\Test-SageLifecycle.ps1','tools\Test-SageDescriptorRegistry.ps1','skills\sage-intake\SKILL.md','skills\sage-discover\SKILL.md','skills\sage-plan\SKILL.md','skills\sage-implement\SKILL.md','skills\sage-verify\SKILL.md')
$missing=@($required | Where-Object { -not (Test-Path -LiteralPath (Join-Path $Root $_) -PathType Leaf) })
if($missing.Count -gt 0){throw "Release files missing: $($missing -join ', ')"}
if($manifest.version -ne '0.8.3' -or $manifest.status -ne 'STABLE'){throw 'Release manifest version/status invalid.'}
$python=Get-Command python -ErrorAction Stop
& $python.Source -m py_compile (Join-Path $Root 'sdk\python\src\sage_sdk\__init__.py'),(Join-Path $Root 'sdk\python\src\sage_sdk\contracts.py'),(Join-Path $Root 'sdk\python\src\sage_sdk\cli.py')
if($LASTEXITCODE -ne 0){throw 'Python SDK compilation failed.'}
$skills=@('sage-intake','sage-discover','sage-plan','sage-implement','sage-verify')
foreach($skill in $skills){$skillPath=Join-Path $Root "skills\$skill\SKILL.md"; if(-not (Test-Path -LiteralPath $skillPath -PathType Leaf)){throw "Skill missing: $skill"}}
$registry=Get-Content -Raw -LiteralPath (Join-Path $Root 'skills\registry.json') | ConvertFrom-Json -Depth 20
$bundle=Get-Content -Raw -LiteralPath (Join-Path $Root 'bundles\v0.8\core-engineering\bundle.json') | ConvertFrom-Json -Depth 20
if(($registry.skills.name -join '|') -ne ($skills -join '|')){throw 'Skill registry lifecycle order mismatch.'}
if(($bundle.lifecycle_contract.ordered_stages -join '|') -ne ($skills -join '|')){throw 'Bundle lifecycle order mismatch.'}
if($registry.offline -ne $true -or $bundle.lifecycle_contract.live_adapters -ne 'disabled_by_default'){throw 'Skill lifecycle safety boundary invalid.'}
[pscustomobject]@{status='PASS'; release=$manifest.release_id; version=$manifest.version; sdk='COMPILES'; skills=$skills; external_execution='DISABLED_BY_DEFAULT'} | ConvertTo-Json -Depth 10
