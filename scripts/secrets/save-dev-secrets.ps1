param(
  [string]$OutputPath = ".secrets\apso.dev.secrets.json.dpapi"
)

$ErrorActionPreference = "Stop"

function Read-SecretValue {
  param([string]$Prompt)
  $secure = Read-Host -Prompt $Prompt -AsSecureString
  return ConvertFrom-SecureString -SecureString $secure
}

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $OutputPath) | Out-Null

$secrets = [ordered]@{
  JIRA_USERNAME              = Read-SecretValue "Jira username/email"
  JIRA_API_TOKEN              = Read-SecretValue "Jira API token"
  BITBUCKET_USERNAME          = Read-SecretValue "Bitbucket username/email"
  BITBUCKET_API_TOKEN         = Read-SecretValue "Bitbucket API token"
  SUPABASE_PUBLISHABLE_KEY    = Read-SecretValue "Supabase publishable key"
  SUPABASE_ANON_KEY           = Read-SecretValue "Supabase anon key"
  SUPABASE_SERVICE_ROLE_KEY   = Read-SecretValue "Supabase service role key"
  SUPABASE_DB_PASSWORD        = Read-SecretValue "Supabase database password"
  SUPABASE_DB_URL             = Read-SecretValue "Supabase DB URL with password"
  SUPABASE_JWT_SECRET         = Read-SecretValue "Supabase JWT secret"
}

($secrets | ConvertTo-Json -Depth 3) | Set-Content -LiteralPath $OutputPath -Encoding UTF8

Write-Host "Encrypted development secrets saved to $OutputPath"
Write-Host "This file can only be decrypted by the same Windows user on this machine."
