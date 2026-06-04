# APSO Deployment Runbook

This runbook covers the current self-hosted production deployment shape. It uses
only the locked APSO stack and keeps secrets outside source control.

## Pre-Deployment Gates

Run from the workspace root:

```powershell
.\scripts\quality\run-production-checks.ps1
```

Do not deploy unless the command passes.

Security scanners are documented in `docs/security/SECURITY_SCANNING.md`.

## Required Production Variables

The production compose file requires these variables at runtime:

```text
APSO_FRONTEND_URL
APSO_API_URL
NEXT_PUBLIC_API_URL
JIRA_BASE_URL
JIRA_USERNAME
JIRA_API_TOKEN
BITBUCKET_WORKSPACE
BITBUCKET_USERNAME
BITBUCKET_API_TOKEN
SUPABASE_URL
SUPABASE_PUBLISHABLE_KEY
SUPABASE_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY
SUPABASE_DB_URL
SUPABASE_JWT_SECRET
MINIO_ENDPOINT
TEMPORAL_ENDPOINT
VALKEY_ENDPOINT
```

Use your deployment platform secret store, shell environment, or an untracked
`.env.prod.local` file. Never commit real values.

## Production Compose

```powershell
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

Backend:

- Runs with `APSO_ENV=prod`.
- Loads config from `/workspace/config`.
- Requires Supabase JWT bearer tokens for protected routes.
- Keeps Jira and Bitbucket read-only.
- Enforces RBAC and rate limiting for protected routes.

Frontend:

- Runs the Next.js standalone production server.
- Uses `APSO_BACKEND_API_URL=http://backend:8000/api/v1` for server-side calls.
- Uses `NEXT_PUBLIC_API_URL` for browser-side API calls.

## Post-Deployment Checks

```powershell
Invoke-WebRequest "$env:APSO_API_URL/api/v1/health"
Invoke-WebRequest "$env:APSO_API_URL/api/v1/ops/readiness"
Invoke-WebRequest "$env:APSO_FRONTEND_URL"
```

The readiness endpoint must not be treated as a replacement for CI gates. It is
a runtime diagnostic surface.

## Observability

APSO observability manifests are in `docker-compose.observability.yml` and
`observability/`. See `docs/operations/OBSERVABILITY.md`.

## Current Limitations

- AWS integration remains mock-only until credentials and IAM policy are
  supplied.
- Temporal worker execution is represented by the backend job-runner contract;
  durable workers still need to be deployed in a later slice.
- Production external AI providers remain disabled in the locked MVP config.
  OpenAI, Claude, or Gemini can be added later through the AI Gateway only.
