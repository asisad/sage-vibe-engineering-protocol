Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$root = Split-Path -Parent $PSScriptRoot
Import-Module (Join-Path $root 'runtime\production\SageAdapters.psm1') -Force
$config = Get-Content -Raw (Join-Path $root 'config\security\strix-adapter.json') | ConvertFrom-Json -Depth 20
$valid = Get-Content -Raw (Join-Path $root 'fixtures\v0.8\strix-dry-run-request.json') | ConvertFrom-Json -Depth 20
$checks=0
function Assert([bool]$ok,[string]$name) { $script:checks++; if (-not $ok) { throw "FAIL: $name" } }
$ready = Test-SageStrixDryRun -Config $config -Request $valid
Assert ($ready.status -eq 'READY_FOR_REVIEW' -and -not $ready.executed) 'valid request is reviewable and not executed'
$missing = [pscustomobject]@{ target=''; authority=[pscustomobject]@{status='DENIED'} }
$blocked = Test-SageStrixDryRun -Config $config -Request $missing
Assert ($blocked.status -eq 'BLOCKED') 'missing approval target credentials blocked'
Assert ($blocked.reasons.Count -ge 3) 'block reasons disclosed'
$out = [pscustomobject]@{ status='PASS'; checks=$checks; live_execution=$false; external_target_contacted=$false; valid_status=$ready.status; blocked_status=$blocked.status }
$out | ConvertTo-Json -Compress
