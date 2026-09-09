[CmdletBinding()]
param([string]$Root)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($Root)) { $Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path) }
$python = (Get-Command python -ErrorAction Stop).Source
$sdkRoot = Join-Path $Root 'sdk\python'
$fixture = Join-Path $Root 'fixtures\v0.8.2\deployment-contract.json'
$tempRoot = Join-Path ([IO.Path]::GetTempPath()) ('sage-sdk-smoke-' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tempRoot -Force | Out-Null
try {
    & $python -m venv $tempRoot
    if ($LASTEXITCODE -ne 0) { throw 'Could not create isolated Python environment.' }
    $venvPython = Join-Path $tempRoot 'Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf)) { throw 'Isolated Python executable is missing.' }
    # Build isolation provisions the declared setuptools build backend in the
    # temporary environment; runtime dependencies remain empty by contract.
    & $venvPython -m pip install --disable-pip-version-check --no-deps $sdkRoot | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'SDK installation failed.' }
    $version = (& $venvPython -c 'import sage_sdk; print(sage_sdk.__version__)').Trim()
    if ($version -ne '0.8.3') { throw "SDK version mismatch: $version" }
    $json = (& $venvPython -m sage_sdk validate $fixture | Out-String) | ConvertFrom-Json
    if ($json.status -ne 'PASS') { throw 'SDK CLI validation returned FAIL.' }
    [pscustomobject]@{ status = 'PASS'; package = 'sage-vibe-engineering'; version = $version; install = 'ISOLATED_VENV'; cli = 'PASS'; network = 'NOT_REQUIRED' } | ConvertTo-Json -Depth 5
}
finally {
    if (Test-Path -LiteralPath $tempRoot) { Remove-Item -LiteralPath $tempRoot -Recurse -Force }
}
