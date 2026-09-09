[CmdletBinding()]
param([string]$Root)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
if ([string]::IsNullOrWhiteSpace($Root)) {$Root=Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)}
$scope=Get-Content -Raw (Join-Path $Root 'config\security\default-local-scope.json') | ConvertFrom-Json -Depth 20
$strix=Get-Command strix -ErrorAction SilentlyContinue
$docker=Get-Command docker -ErrorAction SilentlyContinue
$llmSet=-not [string]::IsNullOrWhiteSpace($env:STRIX_LLM)
$keySet=-not [string]::IsNullOrWhiteSpace($env:LLM_API_KEY)
$dockerReady=$false
if ($docker) { & $docker.Source info --format '{{.ServerVersion}}' 2>$null | Out-Null; $dockerReady=($LASTEXITCODE -eq 0) }
$reasons=[System.Collections.Generic.List[string]]::new()
if (-not $strix) {$reasons.Add('Strix CLI not found')}
if (-not $dockerReady) {$reasons.Add('Docker Engine is not ready')}
if (-not $llmSet) {$reasons.Add('STRIX_LLM is not configured')}
if (-not $keySet) {$reasons.Add('LLM_API_KEY is not configured')}
$status=if($reasons.Count -eq 0){'READY_FOR_REVIEW'}else{'BLOCKED'}
[pscustomobject]@{status=$status; scope_id=$scope.scope_id; target=$scope.target; live_execution=$false; scan_executed=$false; external_target_contacted=$false; prerequisites=[pscustomobject]@{strix_present=[bool]$strix;docker_ready=$dockerReady;STRIX_LLM_set=$llmSet;LLM_API_KEY_set=$keySet}; reasons=@($reasons)} | ConvertTo-Json -Depth 10
