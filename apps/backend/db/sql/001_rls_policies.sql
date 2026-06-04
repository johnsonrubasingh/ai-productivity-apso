-- APSO tenant isolation policy baseline.
-- Review before applying to Supabase Postgres.
--
-- The backend must set app.current_tenant_id for each database transaction
-- before executing tenant-scoped queries if database-level RLS is enforced.

create schema if not exists app;

create or replace function app.current_tenant_id()
returns text
language sql
stable
as $$
  select nullif(current_setting('app.current_tenant_id', true), '')
$$;

alter table if exists user_profiles enable row level security;
alter table if exists projects enable row level security;
alter table if exists integrations enable row level security;
alter table if exists sync_jobs enable row level security;
alter table if exists work_items enable row level security;
alter table if exists repositories enable row level security;
alter table if exists commits enable row level security;
alter table if exists pull_requests enable row level security;
alter table if exists pipeline_runs enable row level security;
alter table if exists bitbucket_test_runs enable row level security;
alter table if exists code_evidence enable row level security;
alter table if exists ai_runs enable row level security;
alter table if exists ai_findings enable row level security;
alter table if exists audit_events enable row level security;

drop policy if exists tenant_isolation_user_profiles on user_profiles;
create policy tenant_isolation_user_profiles on user_profiles
  using (tenant_id = app.current_tenant_id())
  with check (tenant_id = app.current_tenant_id());

drop policy if exists tenant_isolation_projects on projects;
create policy tenant_isolation_projects on projects
  using (tenant_id = app.current_tenant_id())
  with check (tenant_id = app.current_tenant_id());

drop policy if exists tenant_isolation_integrations on integrations;
create policy tenant_isolation_integrations on integrations
  using (tenant_id = app.current_tenant_id())
  with check (tenant_id = app.current_tenant_id());

drop policy if exists tenant_isolation_sync_jobs on sync_jobs;
create policy tenant_isolation_sync_jobs on sync_jobs
  using (tenant_id = app.current_tenant_id())
  with check (tenant_id = app.current_tenant_id());

drop policy if exists tenant_isolation_work_items on work_items;
create policy tenant_isolation_work_items on work_items
  using (tenant_id = app.current_tenant_id())
  with check (tenant_id = app.current_tenant_id());

drop policy if exists tenant_isolation_repositories on repositories;
create policy tenant_isolation_repositories on repositories
  using (tenant_id = app.current_tenant_id())
  with check (tenant_id = app.current_tenant_id());

drop policy if exists tenant_isolation_commits on commits;
create policy tenant_isolation_commits on commits
  using (tenant_id = app.current_tenant_id())
  with check (tenant_id = app.current_tenant_id());

drop policy if exists tenant_isolation_pull_requests on pull_requests;
create policy tenant_isolation_pull_requests on pull_requests
  using (tenant_id = app.current_tenant_id())
  with check (tenant_id = app.current_tenant_id());

drop policy if exists tenant_isolation_pipeline_runs on pipeline_runs;
create policy tenant_isolation_pipeline_runs on pipeline_runs
  using (tenant_id = app.current_tenant_id())
  with check (tenant_id = app.current_tenant_id());

drop policy if exists tenant_isolation_bitbucket_test_runs on bitbucket_test_runs;
create policy tenant_isolation_bitbucket_test_runs on bitbucket_test_runs
  using (tenant_id = app.current_tenant_id())
  with check (tenant_id = app.current_tenant_id());

drop policy if exists tenant_isolation_code_evidence on code_evidence;
create policy tenant_isolation_code_evidence on code_evidence
  using (tenant_id = app.current_tenant_id())
  with check (tenant_id = app.current_tenant_id());

drop policy if exists tenant_isolation_ai_runs on ai_runs;
create policy tenant_isolation_ai_runs on ai_runs
  using (tenant_id = app.current_tenant_id())
  with check (tenant_id = app.current_tenant_id());

drop policy if exists tenant_isolation_ai_findings on ai_findings;
create policy tenant_isolation_ai_findings on ai_findings
  using (tenant_id = app.current_tenant_id())
  with check (tenant_id = app.current_tenant_id());

drop policy if exists tenant_isolation_audit_events on audit_events;
create policy tenant_isolation_audit_events on audit_events
  using (tenant_id = app.current_tenant_id())
  with check (tenant_id = app.current_tenant_id());
