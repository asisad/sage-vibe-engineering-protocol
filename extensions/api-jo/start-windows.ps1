param([switch]$StartVault)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if ($StartVault) {
  if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { throw 'Docker Desktop and docker compose are required for Agent Vault.' }
  if (-not $env:AGENT_VAULT_MASTER_PASSWORD) {
    $secure = Read-Host -Prompt 'Enter Agent Vault master password (not saved)' -AsSecureString
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    try { $env:AGENT_VAULT_MASTER_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr) }
    finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }
  }
  docker compose -f compose.agent-vault.yaml up -d
  Remove-Item Env:AGENT_VAULT_MASTER_PASSWORD -ErrorAction SilentlyContinue
  Write-Host 'Agent Vault management panel: http://127.0.0.1:14321'
}
python api_jo.py seed | Out-Null
Write-Host 'APIJo search panel: http://127.0.0.1:8765'
python api_jo.py serve