$ErrorActionPreference = "Stop"

if (-not $env:APSO_ENV) {
  $env:APSO_ENV = "dev"
}

$env:PYTHONPATH = "apps/backend/src"

python apps/backend/scripts/preflight_runtime.py

Push-Location "apps/backend"
try {
  python -m alembic upgrade head
}
finally {
  Pop-Location
}
