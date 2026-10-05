[CmdletBinding()]
param([string]$Root)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
if ([string]::IsNullOrWhiteSpace($Root)) { $Root=Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path) }
$manifest=Get-Content -Raw -LiteralPath (Join-Path $Root 'RELEASE_MANIFEST_v0.8.4.json') | ConvertFrom-Json -Depth 50
$required=@('README.md','docs\QUICKSTART.fa-en.md','docs\diagrams\sage-architecture.mmd','docs\architecture\agent-native-interfaces.md','docs\architecture\cli-standard.md','docs\architecture\mcp-standard.md','docs\architecture\bridge-standard.md','docs\decisions\ADR-agent-interface-selection.md','docs\decisions\ADR-cli-anything-adoption.md','sdk\python\pyproject.toml','sdk\python\src\sage_sdk\__init__.py','sdk\python\src\sage_sdk\__main__.py','sdk\python\src\sage_sdk\contracts.py','sdk\python\src\sage_sdk\cli.py','RELEASE_MANIFEST_v0.8.3.json','SAGE_v0.8.3_STABLE_RELEASE.md','skills\registry.json','bundles\v0.8\core-engineering\bundle.json','runtime\production\SageLifecycle.psm1','schemas\v0.8\sage-strix-adapter.schema.json','schemas\v0.8\sage-agent-interface.schema.json','config\security\strix-adapter.json','tools\Test-SageLifecycle.ps1','tools\Test-SageDescriptorRegistry.ps1','tools\Test-SageDiagram.ps1','tools\Test-SageStrixAdapter.ps1','tools\Test-SageSdk.ps1','tools\Test-SageAgentInterfaces.ps1','skills\sage-intake\SKILL.md','skills\sage-discover\SKILL.md','skills\sage-plan\SKILL.md','skills\sage-implement\SKILL.md','skills\sage-verify\SKILL.md','skills\interface-audit\SKILL.md','skills\mcp-review\SKILL.md','skills\cli-harness-review\SKILL.md')
$missing=@($required | Where-Object { -not (Test-Path -LiteralPath (Join-Path $Root $_) -PathType Leaf) })
if($missing.Count -gt 0){throw "Release files missing: $($missing -join ', ')"}
$candidateFiles=@('RELEASE_MANIFEST_v0.8.4.json','SAGE_v0.8.4_AGENT_NATIVE_RELEASE.md','SAGE_v0.8.4_AGENT_NATIVE_INTERFACE_DELTA.md','docs\architecture\api-adapter-standard.md','runtime\reference\SageAgentInterfaces.psm1','history\SAGE_v0.8_EXECUTION_PROTOCOL_AND_SKILL_CONTRACT_v0.8.0-formalized.md')
foreach($path in $candidateFiles){if(-not (Test-Path -LiteralPath (Join-Path $Root $path) -PathType Leaf)){throw "Release candidate file missing: $path"}}
if($manifest.version -ne '0.8.4' -or $manifest.release_id -ne 'sage-v0.8.4' -or $manifest.status -ne 'REVIEW_CANDIDATE'){throw 'Release manifest version/status invalid.'}
if($manifest.security_certified -ne $false -or $manifest.security_scan.status -ne 'PENDING' -or $manifest.external_execution -ne 'DISABLED_BY_DEFAULT'){throw 'Release candidate must preserve pending security scan and execution boundary.'}
if(-not (Test-Path -LiteralPath (Join-Path $Root $manifest.security_scan.evidence_ref) -PathType Leaf)){throw 'Strix pending evidence reference is missing.'}
$historicalManifest=Get-Content -Raw -LiteralPath (Join-Path $Root 'RELEASE_MANIFEST_v0.8.3.json') | ConvertFrom-Json -Depth 50
if($historicalManifest.version -ne '0.8.3' -or $historicalManifest.status -ne 'STABLE' -or $historicalManifest.artifacts -contains 'agent-native-interfaces'){throw 'Historical 0.8.3 manifest must remain preserved.'}
$projectText=Get-Content -Raw -LiteralPath (Join-Path $Root 'sdk\python\pyproject.toml')
$initText=Get-Content -Raw -LiteralPath (Join-Path $Root 'sdk\python\src\sage_sdk\__init__.py')
$projectVersion=[regex]::Match($projectText,'(?m)^version\s*=\s*"([^"]+)"\s*$').Groups[1].Value
$moduleVersion=[regex]::Match($initText,'(?m)^__version__\s*=\s*"([^"]+)"\s*$').Groups[1].Value
if($projectVersion -ne $manifest.version -or $moduleVersion -ne $manifest.version){throw 'SDK metadata/module/release version mismatch.'}
$python=Get-Command python -ErrorAction Stop
# Resolve paths before the native call. Inline comma expressions in native
# argument mode are parsed differently by runner/PowerShell versions.
$sdkCompilePaths=@(
    (Join-Path $Root 'sdk\python\src\sage_sdk\__init__.py')
    (Join-Path $Root 'sdk\python\src\sage_sdk\contracts.py')
    (Join-Path $Root 'sdk\python\src\sage_sdk\cli.py')
)
& $python.Source -m py_compile @sdkCompilePaths
if($LASTEXITCODE -ne 0){throw 'Python SDK compilation failed.'}
$skills=@('sage-intake','sage-discover','sage-plan','sage-implement','sage-verify')
$allSkills=@($skills)+@('interface-audit','mcp-review','cli-harness-review')
foreach($skill in $allSkills){
    $skillPath=Join-Path $Root "skills\$skill\SKILL.md"
    if(-not (Test-Path -LiteralPath $skillPath -PathType Leaf)){throw "Skill missing: $skill"}
    $skillText=Get-Content -Raw -LiteralPath $skillPath
    $frontmatter=[regex]::Match($skillText,'\A---\r?\n(?<body>[\s\S]*?)\r?\n---(?:\r?\n|$)')
    if(-not $frontmatter.Success){throw "Skill YAML frontmatter missing: $skill"}
    $name=[regex]::Match($frontmatter.Groups['body'].Value,'(?m)^name:\s*([^\r\n]+)').Groups[1].Value.Trim().Trim('"', "'")
    $description=[regex]::Match($frontmatter.Groups['body'].Value,'(?m)^description:\s*([^\r\n]+)').Groups[1].Value.Trim().Trim('"', "'")
    if($name -ne $skill -or [string]::IsNullOrWhiteSpace($description) -or $description -in @('|','>')){throw "Skill frontmatter name/description invalid: $skill"}
}
$registry=Get-Content -Raw -LiteralPath (Join-Path $Root 'skills\registry.json') | ConvertFrom-Json -Depth 20
$bundle=Get-Content -Raw -LiteralPath (Join-Path $Root 'bundles\v0.8\core-engineering\bundle.json') | ConvertFrom-Json -Depth 20
if($bundle.version -ne $manifest.version -or $registry.schema_version -ne "sage/$($manifest.version)"){throw 'Bundle/registry/release version mismatch.'}
if(@($registry.skills).Count -ne $allSkills.Count -or (@($registry.skills.name | Sort-Object) -join '|') -ne (@($allSkills | Sort-Object) -join '|')){throw 'Release skill registry must contain exactly eight unique skills.'}
if((@($bundle.skills | Sort-Object) -join '|') -ne (@($allSkills | Sort-Object) -join '|')){throw 'Bundle must expose all eight registered skills.'}
if((@($registry.skills | Where-Object { $_.name -in $skills }).name -join '|') -ne ($skills -join '|')){throw 'Skill registry lifecycle order mismatch.'}
if(($bundle.lifecycle_contract.ordered_stages -join '|') -ne ($skills -join '|')){throw 'Bundle lifecycle order mismatch.'}
if($registry.offline -ne $true -or $bundle.lifecycle_contract.live_adapters -ne 'disabled_by_default'){throw 'Skill lifecycle safety boundary invalid.'}
foreach($route in @(@{name='interface-audit';stage='DISCOVER';authority='advisory'},@{name='mcp-review';stage='VERIFY';authority='evidence_only'},@{name='cli-harness-review';stage='VERIFY';authority='evidence_only'})){
    $entry=@($registry.skills | Where-Object { $_.name -eq $route.name })[0]
    if($entry.stage -ne $route.stage -or $entry.authority -ne $route.authority){throw "Specialized skill routing/authority invalid: $($route.name)"}
}
[pscustomobject]@{status='PASS'; release=$manifest.release_id; version=$manifest.version; release_status=$manifest.status; sdk='COMPILES'; skills=$allSkills; security_scan=$manifest.security_scan.status; external_execution='DISABLED_BY_DEFAULT'} | ConvertTo-Json -Depth 10
