param(
  [string]$InputPath = ".secrets\apso.dev.secrets.json.dpapi",
  [string]$OutputPath = ".env.dev.local"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $InputPath)) {
  throw "Encrypted secret file not found: $InputPath. Run scripts\secrets\save-dev-secrets.ps1 first."
}

function Unprotect-Value {
  param([string]$ProtectedValue)
  $secure = ConvertTo-SecureString -String $ProtectedValue
  $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
  try {
    return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
  }
  finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
  }
}

$protected = Get-Content -LiteralPath $InputPath -Raw | ConvertFrom-Json

$dbPassword = Unprotect-Value $protected.SUPABASE_DB_PASSWORD
$dbUrl = Unprotect-Value $protected.SUPABASE_DB_URL
if (-not $dbUrl) {
  $dbUrl = "postgresql://postgres:$dbPassword@db.rwjfllhcjsujrhvkvtuz.supabase.co:5432/postgres"
}

$lines = @(
  "# Generated local APSO dev environment. Do not commit.",
  "JIRA_BASE_URL=https://elixirlabs.atlassian.net/",
  "JIRA_USERNAME=$(Unprotect-Value $protected.JIRA_USERNAME)",
  "JIRA_API_TOKEN=$(Unprotect-Value $protected.JIRA_API_TOKEN)",
  "",
  "BITBUCKET_USERNAME=$(Unprotect-Value $protected.BITBUCKET_USERNAME)",
  "BITBUCKET_API_TOKEN=$(Unprotect-Value $protected.BITBUCKET_API_TOKEN)",
  "BITBUCKET_WORKSPACE=or-pems-2025",
  "",
  "SUPABASE_URL=https://rwjfllhcjsujrhvkvtuz.supabase.co",
  "SUPABASE_PUBLISHABLE_KEY=$(Unprotect-Value $protected.SUPABASE_PUBLISHABLE_KEY)",
  "SUPABASE_ANON_KEY=$(Unprotect-Value $protected.SUPABASE_ANON_KEY)",
  "SUPABASE_SERVICE_ROLE_KEY=$(Unprotect-Value $protected.SUPABASE_SERVICE_ROLE_KEY)",
  "SUPABASE_DB_URL=$dbUrl",
  "SUPABASE_JWT_SECRET=$(Unprotect-Value $protected.SUPABASE_JWT_SECRET)",
  "",
  "OLLAMA_BASE_URL=http://localhost:11434",
  "OLLAMA_CHAT_MODEL=qwen2.5-coder:14b",
  "OLLAMA_EMBEDDING_MODEL=qwen3-embedding:4b"
)

$lines | Set-Content -LiteralPath $OutputPath -Encoding UTF8
Write-Host "Materialized local env file: $OutputPath"
Write-Host "This file is ignored by Git. Keep it local."

