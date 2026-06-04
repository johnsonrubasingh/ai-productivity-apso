# APSO Backend

FastAPI backend foundation for APSO.

## Locked Scope

- Environments: `dev` and `prod` only.
- Jira: read-only for MVP.
- Bitbucket: read-only for MVP.
- AWS: mock until credentials are supplied later.
- AI: all model calls go through APSO AI Gateway.
- Secrets: never commit raw credentials.

## Run Locally

From the repository root:

```powershell
$env:APSO_ENV = "dev"
uvicorn apso_backend.main:app --app-dir apps/backend/src --reload
```

## Docker Dev

```powershell
docker compose -f docker-compose.dev.yml up --build backend
```

The Docker image installs only the backend dependencies declared in
`apps/backend/pyproject.toml`. Secrets must still be supplied through ignored
local environment files or shell environment variables.

## Smoke Check

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:PYTHONPATH = "C:\MyWorkspace\AI_Productivity_APSO\apps\backend\src"
python .\apps\backend\scripts\smoke_check.py
```

The smoke check exercises app startup, config loading, integration summaries,
scope declarations, AI task registration, auth dev-context fallback, and sample
Jira JQL output.

## Live Read-Only Checks

After creating an ignored `.env.dev.local`, run:

```powershell
$env:APSO_ENV = "dev"
$env:PYTHONPATH = "apps/backend/src"
python apps/backend/scripts/check_connectors.py
python apps/backend/scripts/check_database.py
python apps/backend/scripts/preflight_runtime.py
```

See `docs/development/LOCAL_BACKEND_SETUP.md`.

## RLS Policies

Tenant isolation SQL policies are staged in:

```text
apps/backend/db/sql/001_rls_policies.sql
```

Review before applying to Supabase/Postgres.

## Export API Contract

```powershell
$env:PYTHONPATH = "apps/backend/src"
python apps/backend/scripts/export_openapi.py
```

The generated contract is written to `docs/api/openapi.json`.

## Current API Foundation

- `GET /api/v1/health`
- `GET /api/v1/config/runtime`
- `GET /api/v1/auth/me`
- `GET /api/v1/integrations`
- `GET /api/v1/integrations/jira/scopes`
- `GET /api/v1/integrations/jira/check`
- `GET /api/v1/integrations/bitbucket/scopes`
- `GET /api/v1/integrations/bitbucket/check`
- `GET /api/v1/integrations/jira/issues/sample-jql`
- `POST /api/v1/integrations/jira/issues/search`
- `POST /api/v1/integrations/jira/issues/ingest`
- `GET /api/v1/integrations/bitbucket/repositories`
- `GET /api/v1/integrations/bitbucket/repositories/{repo_slug}/pull-requests`
- `GET /api/v1/integrations/bitbucket/repositories/{repo_slug}/commits`
- `GET /api/v1/integrations/bitbucket/repositories/{repo_slug}/pipelines`
- `POST /api/v1/integrations/bitbucket/repositories/ingest`
- `POST /api/v1/integrations/bitbucket/repositories/{repo_slug}/pull-requests/ingest`
- `POST /api/v1/integrations/bitbucket/repositories/{repo_slug}/commits/ingest`
- `POST /api/v1/integrations/bitbucket/repositories/{repo_slug}/pipelines/ingest`
- `GET /api/v1/ai/tasks`
- `GET /api/v1/ai/provider/health`
- `POST /api/v1/engines/definition-gap/analyze`
- `POST /api/v1/engines/code-quality/analyze`
- `POST /api/v1/engines/coverage/verify`
- `GET /api/v1/dashboard/project-health`
- `GET /api/v1/quality/scanners`
- `POST /api/v1/quality/scanners/dry-run`
- `POST /api/v1/quality/release-readiness`
- `POST /api/v1/reports/proof-pack`
- `POST /api/v1/jobs/run`
- `GET /api/v1/ops/readiness`
- `GET /api/v1/ops/metrics`
- `POST /api/v1/core/tenants`
- `GET /api/v1/core/tenants`
- `POST /api/v1/core/projects`
- `GET /api/v1/core/projects`
- `GET /api/v1/core/work-items`
- `POST /api/v1/findings`
- `GET /api/v1/findings`
- `PATCH /api/v1/findings/{finding_id}/status`

Routes that call live Jira, Bitbucket, database, or Ollama require the matching
local services/secrets to be configured. Scope and metadata routes are safe to
call without live credentials.

## Important

This backend reads configuration from `config/environments.<env>.yaml`.
Secrets are referenced by environment variable name and must not be stored in
source-controlled files.

For developer convenience, the backend will load `.env.dev.local` from the
workspace root when `APSO_ENV=dev`. This file is ignored by Git.
