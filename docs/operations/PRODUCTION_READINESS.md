# APSO Production Readiness

APSO is not production ready until every gate in this document passes for the
target `prod` environment.

## Required Gates

1. Backend contract tests pass with `python -m pytest apps/backend/tests`.
2. Frontend checks pass with `corepack pnpm lint`, `corepack pnpm typecheck`,
   and `corepack pnpm build`.
3. Static production checks pass with
   `python scripts/quality/production_readiness_check.py`.
4. `docs/api/openapi.json` is regenerated after backend route changes.
5. No raw Jira, Bitbucket, Supabase, AWS, OpenAI, Claude, Gemini, or database
   secrets are committed.
6. `APSO_ENV=prod` uses Supabase JWT authentication. Dev headers are not an
   acceptable production authentication mechanism.
7. Jira and Bitbucket remain read-only unless the backlog write-back feature is
   formally approved and implemented as a separate scoped release.
8. AWS remains mock-only until the production AWS user, IAM policy, and
   CodeCommit/CodeBuild/CodePipeline integration tests are supplied and passed.
9. Production model providers must be configured only through the AI Gateway.
   Business modules must not call OpenAI, Claude, Gemini, or Ollama directly.
10. Production Docker builds must use `docker-compose.prod.yml` or equivalent
    manifests with secrets supplied through the runtime environment.
11. Prometheus metrics and JSON request logs must be enabled before production
    traffic is accepted.
12. RBAC, rate limiting, and audit event generation must be enabled for
    protected operator actions.
13. CI security scans must pass: Gitleaks, Semgrep CE, Trivy, and OWASP
    Dependency-Check.

## Local Full Check

From the workspace root:

```powershell
.\scripts\quality\run-production-checks.ps1
```

## Current Readiness Status

Current status is pre-production. The application has backend and frontend
foundations, read-only integrations, AI analysis routes, dashboards, setup,
ingestion, explorer surfaces, CI gates, production Docker targets, a deployment
runbook, JSON request logging, Prometheus metrics, OSS observability manifests,
RBAC dependencies, in-memory rate limiting, and audit coverage for operator
actions. Frontend production calls no longer send development headers and can use
a session bearer token. CI now includes the locked security scanners. Bitbucket
backend coverage now includes repositories, pull requests, commits, pipelines,
pipeline steps, pipeline test reports, source file evidence, and diff evidence.
It still requires live production deployment, full Supabase Auth UI/session handling,
Supabase production auth verification against real users, distributed
Valkey-backed rate limiting before horizontal scaling, curated Grafana
dashboards, container/image scanning validation on the real CI runner, and AWS
integration once credentials are available. Jira and Bitbucket also need live
smoke validation with the configured read-only credentials before production
onboarding.
