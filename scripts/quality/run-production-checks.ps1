$ErrorActionPreference = "Stop"

Set-Location (Resolve-Path "$PSScriptRoot\..\..")

$env:PYTHONDONTWRITEBYTECODE = "1"
$env:PYTHONPATH = "apps/backend/src"

function Invoke-Native {
  param(
    [Parameter(Mandatory = $true)]
    [scriptblock]$Command
  )

  & $Command
  if ($LASTEXITCODE -ne 0) {
    throw "Command failed with exit code $LASTEXITCODE"
  }
}

Invoke-Native { python scripts/quality/production_readiness_check.py }
Invoke-Native { python -m pytest apps/backend/tests }
Invoke-Native { powershell -ExecutionPolicy Bypass -File scripts/quality/run-security-scans.ps1 }

Push-Location apps/frontend
try {
  Invoke-Native { corepack pnpm lint }
  Invoke-Native { corepack pnpm typecheck }
  Invoke-Native { corepack pnpm build }
}
finally {
  Pop-Location
}
