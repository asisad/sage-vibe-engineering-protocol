[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$OutputDirectory, [switch]$InstallApproved)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if (-not $InstallApproved) { throw 'Explicit -InstallApproved is required; no image was built.' }
if (-not [IO.Path]::IsPathRooted($OutputDirectory) -or $OutputDirectory -match '(^|[\\/])\.\.([\\/]|$)') { throw 'Use a new absolute output directory.' }
$sageKitRoot = Split-Path -Parent $PSScriptRoot
$sageOutputRoot = [IO.Path]::GetFullPath($OutputDirectory).TrimEnd([IO.Path]::DirectorySeparatorChar)
if (Test-Path -LiteralPath $sageOutputRoot) { throw 'Output already exists; existing configuration is never overwritten.' }
if (-not (Test-Path -LiteralPath (Split-Path -Parent $sageOutputRoot) -PathType Container)) { throw 'Output parent must exist.' }
if ($sageOutputRoot.StartsWith($sageKitRoot,[StringComparison]::OrdinalIgnoreCase)) { throw 'Keep private state outside the kit.' }
$sageDocker = (Get-Command docker -ErrorAction Stop).Source
& $sageDocker build --tag sage-ruflo-coordinator:3.61.1 --file (Join-Path $sageKitRoot 'extensions/ruflo/runtime/Dockerfile') (Join-Path $sageKitRoot 'extensions/ruflo/runtime')
if ($LASTEXITCODE -ne 0) { throw 'Pinned image build failed; no live execution is claimed.' }
$sageImageId = (& $sageDocker image inspect sage-ruflo-coordinator:3.61.1 --format '{{.Id}}').Trim()
if ($LASTEXITCODE -ne 0 -or $sageImageId -notmatch '^sha256:[a-f0-9]{64}$') { throw 'Immutable local image identity unavailable.' }
New-Item -ItemType Directory -Path $sageOutputRoot | Out-Null
$sageBinding = @{schema_version='sage-ruflo-worker/0.1'; image_id=$sageImageId; coordination_root=(Join-Path $sageOutputRoot 'coordinator')}
$sageBindingFile = Join-Path $sageOutputRoot 'ruflo-binding.json'
[IO.File]::WriteAllText($sageBindingFile,($sageBinding | ConvertTo-Json),[Text.UTF8Encoding]::new($false))
@{status='PROVISIONED_NOT_LIVE_TESTED'; image_id=$sageImageId; configuration=$sageBindingFile; model_invocations=0} | ConvertTo-Json
