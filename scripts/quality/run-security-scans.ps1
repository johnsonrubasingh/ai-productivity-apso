param(
  [switch]$RequireTools
)

$ErrorActionPreference = "Stop"

Set-Location (Resolve-Path "$PSScriptRoot\..\..")

$missing = @()
$env:SEMGREP_SEND_METRICS = "off"
$pythonScripts = Join-Path $env:APPDATA "Python\Python312\Scripts"
if (Test-Path -LiteralPath $pythonScripts) {
  $env:Path = "$pythonScripts;$env:Path"
}

function Resolve-CommandPath {
  param([string]$Name)
  $command = Get-Command $Name -ErrorAction SilentlyContinue
  if ($command) {
    return $command.Source
  }

  $candidate = Join-Path $pythonScripts "$Name.exe"
  if (Test-Path -LiteralPath $candidate) {
    return $candidate
  }

  return $null
}

function Invoke-Or-MarkMissing {
  param(
    [string]$Name,
    [scriptblock]$Command
  )

  $resolved = Resolve-CommandPath $Name
  if (-not $resolved) {
    $script:missing += $Name
    Write-Warning "$Name is not installed; skipping local scan."
    return
  }

  & $Command
  if ($LASTEXITCODE -ne 0) {
    throw "$Name scan failed with exit code $LASTEXITCODE"
  }
}

Invoke-Or-MarkMissing "gitleaks" {
  $gitleaks = Resolve-CommandPath "gitleaks"
  & $gitleaks detect --no-git --source . --config .gitleaks.toml --redact --no-banner
}

Invoke-Or-MarkMissing "semgrep" {
  $semgrep = Resolve-CommandPath "semgrep"
  & $semgrep scan --config .semgrep.yml --error --exclude apps/frontend/node_modules --exclude apps/frontend/.next
}

Invoke-Or-MarkMissing "trivy" {
  $trivy = Resolve-CommandPath "trivy"
  & $trivy fs `
    --scanners vuln,secret,misconfig `
    --severity HIGH,CRITICAL `
    --exit-code 1 `
    --ignorefile .trivyignore `
    --skip-dirs apps/frontend/.next `
    --skip-dirs apps/frontend/node_modules `
    --skip-dirs runtime `
    --skip-dirs rendered_apso_plan `
    .
}

Invoke-Or-MarkMissing "dependency-check" {
  $dependencyCheck = Resolve-CommandPath "dependency-check"
  & $dependencyCheck `
    --project "APSO" `
    --scan apps/backend/pyproject.toml `
    --scan apps/frontend/package.json `
    --scan apps/frontend/pnpm-lock.yaml `
    --suppression dependency-check-suppression.xml `
    --disableYarnAudit `
    --disablePnpmAudit `
    --failOnCVSS 7 `
    --out runtime/dependency-check
}

if ($RequireTools -and $missing.Count -gt 0) {
  throw "Required security tools missing: $($missing -join ', ')"
}

if ($missing.Count -gt 0) {
  Write-Host "Security scan runner completed in advisory mode. Missing tools: $($missing -join ', ')"
}
else {
  Write-Host "Security scans completed successfully."
}
