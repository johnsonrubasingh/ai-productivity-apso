# APSO Live Validation Status

Date: 2026-06-04
Environment: dev

## Summary

Supabase dev database validation passed through the Supabase shared pooler.
Bitbucket live read-only validation passed for the configured workspace and
repositories. Jira live validation is blocked because Atlassian returns HTTP
401 for the provided Jira email/token pair.

No secrets are stored in this document.

## Supabase

Status: passed

- Dev environment file is local-only and ignored by Git.
- Direct Supabase database hostname resolved only to IPv6 from this machine.
- Shared Supabase pooler resolved to IPv4 and was used for validation.
- Database connection succeeded.
- Alembic migrations applied:
  - `0001_initial_schema`
  - `0002_bitbucket_evidence_tables`
- `pgvector` is enabled.
- Tenant RLS SQL was applied.

## Jira

Status: blocked

- Backend configuration loaded Jira base URL and credential env vars.
- Jira connection check reached Atlassian.
- Atlassian returned HTTP 401 for the configured Jira token.
- The same token also returned HTTP 401 when tested with the alternate local Git
  identity email.

Required next action:

- Regenerate a Jira API token for the Jira account that can access
  `https://elixirlabs.atlassian.net/`.
- Ensure the token has:
  - `read:account`
  - `read:jira-work`
- Update the ignored local `.env.dev.local` value and rerun connector checks.

## Bitbucket

Status: passed

Bitbucket account check passed for the configured read-only token.

Validated repositories:

- `or-pems-plt-sandbox-web`, branch `develop`
- `or-pems-plt-sandbox-api`, branch `develop`

Validated evidence:

- Repository listing
- Pull request listing and ingestion
- Commit listing and ingestion
- Pipeline listing and ingestion
- Pipeline step listing
- Pipeline test report ingestion where available
- Source file listing and evidence ingestion
- Pull request or commit diff evidence ingestion

Observed dev database counts after validation:

- repositories: 10
- pull_requests: 2
- commits: 60
- pipeline_runs: 10
- bitbucket_test_runs: 1
- code_evidence: 5

## APSO Smoke

Status: passed with Jira blocked

Validated routes:

- health
- integrations
- AI task catalog
- Jira and Bitbucket scope contracts
- Bitbucket connection check
- runtime config
- auth context
- protected-route rejection without context
- definition gap engine
- scanner catalog
- release readiness
- proof-pack generation
- job runner
- ops readiness
- code quality engine
- coverage verification
- dashboard project health

The smoke run reported:

- Jira check: failed, HTTP 401
- Bitbucket check: passed
- Backend readiness: ready
