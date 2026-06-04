# APSO Project Baseline

This baseline records non-sensitive project setup details supplied for APSO development.

## External Systems

### Jira

- Base URL: `https://elixirlabs.atlassian.net/`
- User/email: `johnson.r@cardyai.com`
- MVP access model: read-only
- Required MVP scopes:
  - `read:account`
  - `read:jira-work`

### Bitbucket

- Workspace/repository group: `or-pems-2025`
- Web repository: `or-pems-plt-sandbox-web`
- Web branch: `develop`
- API repository: `or-pems-plt-sandbox-api`
- API branch: `develop`
- MVP access model: read-only

Required MVP read scopes:

- `read:account`
- `read:me`
- `read:user:bitbucket`
- `read:workspace:bitbucket`
- `read:project:bitbucket`
- `read:repository:bitbucket`
- `read:pullrequest:bitbucket`
- `read:pipeline:bitbucket`
- `read:test:bitbucket`

Optional diagnostic read scopes:

- `read:permission:bitbucket`
- `read:webhook:bitbucket`

Do not select write, admin, or delete scopes for MVP.

### Supabase

- Project URL: `https://rwjfllhcjsujrhvkvtuz.supabase.co`
- Database: Supabase Postgres
- Vector storage: `pgvector`
- Auth/user management: Supabase Auth

Sensitive Supabase keys, database passwords, JWT secrets, and service role credentials must stay outside source control.

### GitHub

- Repository: `https://github.com/johnsonrubasingh/ai-productivity-apso`

### AWS

- AWS user/role will be supplied later.
- AWS CodeCommit/CodeBuild/CodePipeline must remain mocked in `dev` until credentials are provided.

## MVP Scope

Build APSO as a read-only SDLC intelligence platform:

- extract Jira work items and metadata
- extract Bitbucket repositories, commits, pull requests, pipelines, tests, and code evidence
- mock AWS CodeCommit/CodeBuild/CodePipeline until AWS access is available
- analyze requirement gaps
- analyze code quality/security
- verify coverage and traceability
- generate explainable AI findings
- produce dashboards and proof-pack reports

## Backlog Only

The following require future approval and are not part of MVP:

- create Jira tickets from AI findings
- add comments to Jira stories
- update Jira priority
- change Jira labels
- move Jira issue status
- write AI recommendations back to Jira
- manage Jira webhooks
- create Bitbucket PR comments
- upload Bitbucket code insights
- trigger Bitbucket pipelines
- manage Bitbucket webhooks
- enable paid model providers
- enable live AWS integration

