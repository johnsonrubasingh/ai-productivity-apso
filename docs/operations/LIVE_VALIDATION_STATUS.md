# APSO Live Validation Status

Date: 2026-06-05
Environment: dev

## Summary

Supabase dev database validation passed through the Supabase shared pooler.
Bitbucket live read-only validation passed for the configured workspace and
repositories. Jira authentication now passes through the Atlassian API gateway,
but Jira project and issue visibility are still empty for the configured
account/token.

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

Status: partially passed

- Backend configuration loaded Jira base URL and credential env vars.
- Direct site Basic Auth returns HTTP 401 for the scoped token.
- Atlassian gateway Basic Auth succeeds with the resolved cloud ID.
- APSO now supports both classic direct Jira tokens and scoped gateway tokens.
- Jira `/myself` validation passes.
- Jira search uses the current `/rest/api/3/search/jql` endpoint because the
  legacy `/rest/api/3/search` endpoint returns HTTP 410 in Jira Cloud.
- Search JQL executed successfully but returned zero issues.
- Jira project visibility check returned zero projects.
- Jira ingestion executed successfully but stored zero work items because no
  visible issues were returned.

Required next action:

- Grant the Jira account/token visibility to at least one Jira project on
  `https://elixirlabs.atlassian.net/`.
- Confirm the account can browse issues in Jira UI.
- Keep the current scopes:
  - `read:account`
  - `read:jira-work`
- Rerun Jira project search, issue search, and ingestion after project access is
  granted.

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

Status: passed with Jira data visibility pending

Validated routes:

- health
- integrations
- AI task catalog
- Jira and Bitbucket scope contracts
- Jira connection check
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

- Jira check: passed
- Bitbucket check: passed
- Backend readiness: ready
