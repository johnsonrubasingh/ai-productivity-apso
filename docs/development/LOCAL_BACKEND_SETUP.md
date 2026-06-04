# APSO Local Backend Setup

This guide prepares the backend for live read-only connector checks and database migrations.

## 1. Create ignored local env file

Copy `.env.example` to `.env.dev.local` in the workspace root.

Do not commit `.env.dev.local`.

Recommended safer option on Windows:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\secrets\save-dev-secrets.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\secrets\materialize-dev-env.ps1
```

The first command prompts for secrets and stores them encrypted for the current
Windows user. The second command materializes `.env.dev.local`, which is ignored
by Git.

Required values:

```text
JIRA_USERNAME=
JIRA_API_TOKEN=
BITBUCKET_USERNAME=
BITBUCKET_API_TOKEN=
SUPABASE_DB_URL=
SUPABASE_JWT_SECRET=
```

Optional values:

```text
SUPABASE_URL=
SUPABASE_PUBLISHABLE_KEY=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
OLLAMA_BASE_URL=http://localhost:11434
```

## 2. Install backend dependencies

Use a local virtual environment or container. The backend dependencies are declared in:

```text
apps/backend/pyproject.toml
```

## 3. Run smoke check

```powershell
$env:APSO_ENV = "dev"
$env:PYTHONPATH = "apps/backend/src"
python apps/backend/scripts/smoke_check.py
```

## 4. Check live connectors

This uses only read-only Jira and Bitbucket calls.

```powershell
$env:APSO_ENV = "dev"
$env:PYTHONPATH = "apps/backend/src"
python apps/backend/scripts/check_connectors.py
```

Expected result once secrets are set:

```text
jira: {"ok": true, ...}
bitbucket: {"ok": true, ...}
```

## 5. Check database

```powershell
$env:APSO_ENV = "dev"
$env:PYTHONPATH = "apps/backend/src"
python apps/backend/scripts/check_database.py
```

## 6. Runtime preflight

```powershell
$env:APSO_ENV = "dev"
$env:PYTHONPATH = "apps/backend/src"
python apps/backend/scripts/preflight_runtime.py
```

## 7. Run migrations

```powershell
powershell -ExecutionPolicy Bypass -File apps/backend/scripts/run_migrations.ps1
```

## Rules

- Jira and Bitbucket remain read-only.
- AWS remains mocked until later.
- Do not commit secrets.
- Do not enable external AI providers in dev.
