$ErrorActionPreference = "Stop"

if (-not $env:APSO_ENV) {
  $env:APSO_ENV = "dev"
}

$env:PYTHONPATH = "apps/backend/src"

python apps/backend/scripts/preflight_runtime.py

if (-not $env:SUPABASE_DB_URL) {
  throw "SUPABASE_DB_URL is not set. Materialize .env.dev.local or export the variable before running migrations."
}

if (-not (Get-Command alembic -ErrorAction SilentlyContinue)) {
  throw "Alembic is not installed in this shell. Install backend dependencies first."
}

Push-Location "apps/backend"
try {
  alembic upgrade head
}
finally {
  Pop-Location
}
