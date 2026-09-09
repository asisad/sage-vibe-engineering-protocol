[CmdletBinding()]
param([string]$Root)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
if ([string]::IsNullOrWhiteSpace($Root)) { $Root=Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path) }
$manifest=Get-Content -Raw -LiteralPath (Join-Path $Root 'RELEASE_MANIFEST_v0.8.2.json') | ConvertFrom-Json -Depth 50
$required=@('README.md','docs\QUICKSTART.fa-en.md','sdk\python\pyproject.toml','sdk\python\src\sage_sdk\__init__.py','sdk\python\src\sage_sdk\contracts.py','sdk\python\src\sage_sdk\cli.py','RELEASE_MANIFEST_v0.8.2.json')
$missing=@($required | Where-Object { -not (Test-Path -LiteralPath (Join-Path $Root $_) -PathType Leaf) })
if($missing.Count -gt 0){throw "Release files missing: $($missing -join ', ')"}
if($manifest.version -ne '0.8.2' -or $manifest.status -ne 'RELEASE_CANDIDATE'){throw 'Release manifest version/status invalid.'}
$python=Get-Command python -ErrorAction Stop
& $python.Source -m py_compile (Join-Path $Root 'sdk\python\src\sage_sdk\__init__.py'),(Join-Path $Root 'sdk\python\src\sage_sdk\contracts.py'),(Join-Path $Root 'sdk\python\src\sage_sdk\cli.py')
if($LASTEXITCODE -ne 0){throw 'Python SDK compilation failed.'}
[pscustomobject]@{status='PASS'; release=$manifest.release_id; version=$manifest.version; sdk='COMPILES'; external_execution='DISABLED_BY_DEFAULT'} | ConvertTo-Json -Depth 10
