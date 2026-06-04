"""Initial APSO backend schema.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-06-01
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("create extension if not exists vector")

    op.create_table(
        "tenants",
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("timezone", sa.String(length=80), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_table(
        "projects",
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("key", sa.String(length=80), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_projects_tenant_id", "projects", ["tenant_id"])
    op.create_index("ix_projects_key", "projects", ["key"])

    op.create_table(
        "user_profiles",
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("display_name", sa.String(length=200), nullable=True),
        sa.Column("role", sa.String(length=80), nullable=False),
        sa.Column("supabase_user_id", sa.String(length=100), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_profiles_tenant_id", "user_profiles", ["tenant_id"])
    op.create_index("ix_user_profiles_email", "user_profiles", ["email"])
    op.create_index("ix_user_profiles_supabase_user_id", "user_profiles", ["supabase_user_id"])

    op.create_table(
        "integrations",
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("mode", sa.String(length=80), nullable=False),
        sa.Column("display_name", sa.String(length=200), nullable=False),
        sa.Column("config", sa.JSON(), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_integrations_tenant_id", "integrations", ["tenant_id"])
    op.create_index("ix_integrations_provider", "integrations", ["provider"])

    op.create_table(
        "sync_jobs",
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("checkpoint", sa.JSON(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sync_jobs_tenant_id", "sync_jobs", ["tenant_id"])
    op.create_index("ix_sync_jobs_provider", "sync_jobs", ["provider"])

    op.create_table(
        "work_items",
        sa.Column("project_id", sa.String(length=36), nullable=True),
        sa.Column("external_id", sa.String(length=120), nullable=False),
        sa.Column("source", sa.String(length=80), nullable=False),
        sa.Column("issue_key", sa.String(length=80), nullable=False),
        sa.Column("issue_type", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=120), nullable=False),
        sa.Column("summary", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_work_items_issue_key", "work_items", ["issue_key"])
    op.create_index("ix_work_items_project_id", "work_items", ["project_id"])
    op.create_index("ix_work_items_tenant_id", "work_items", ["tenant_id"])
    op.create_index(
        "ix_work_items_tenant_source_external",
        "work_items",
        ["tenant_id", "source", "external_id"],
        unique=True,
    )

    op.create_table(
        "repositories",
        sa.Column("project_id", sa.String(length=36), nullable=True),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("workspace", sa.String(length=200), nullable=True),
        sa.Column("slug", sa.String(length=200), nullable=False),
        sa.Column("default_branch", sa.String(length=120), nullable=False),
        sa.Column("clone_url", sa.Text(), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_repositories_project_id", "repositories", ["project_id"])
    op.create_index("ix_repositories_tenant_id", "repositories", ["tenant_id"])
    op.create_index(
        "ix_repositories_tenant_provider_slug",
        "repositories",
        ["tenant_id", "provider", "slug"],
        unique=True,
    )

    op.create_table(
        "pull_requests",
        sa.Column("repository_id", sa.String(length=36), nullable=True),
        sa.Column("external_id", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("state", sa.String(length=80), nullable=False),
        sa.Column("source_branch", sa.String(length=200), nullable=True),
        sa.Column("target_branch", sa.String(length=200), nullable=True),
        sa.Column("author", sa.String(length=320), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pull_requests_repository_id", "pull_requests", ["repository_id"])
    op.create_index("ix_pull_requests_tenant_id", "pull_requests", ["tenant_id"])

    op.create_table(
        "commits",
        sa.Column("repository_id", sa.String(length=36), nullable=True),
        sa.Column("hash", sa.String(length=120), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("author", sa.String(length=320), nullable=True),
        sa.Column("branch", sa.String(length=200), nullable=True),
        sa.Column("committed_at", sa.String(length=80), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_commits_hash", "commits", ["hash"])
    op.create_index("ix_commits_repository_id", "commits", ["repository_id"])
    op.create_index("ix_commits_tenant_id", "commits", ["tenant_id"])
    op.create_index(
        "ix_commits_tenant_repository_hash",
        "commits",
        ["tenant_id", "repository_id", "hash"],
        unique=True,
    )

    op.create_table(
        "pipeline_runs",
        sa.Column("repository_id", sa.String(length=36), nullable=True),
        sa.Column("external_id", sa.String(length=120), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=80), nullable=False),
        sa.Column("branch", sa.String(length=200), nullable=True),
        sa.Column("commit_sha", sa.String(length=120), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pipeline_runs_repository_id", "pipeline_runs", ["repository_id"])
    op.create_index("ix_pipeline_runs_tenant_id", "pipeline_runs", ["tenant_id"])
    op.create_index("ix_pipeline_runs_commit_sha", "pipeline_runs", ["commit_sha"])

    op.create_table(
        "ai_runs",
        sa.Column("task_name", sa.String(length=120), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("model_name", sa.String(length=160), nullable=False),
        sa.Column("prompt_version", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("validation_result", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_runs_task_name", "ai_runs", ["task_name"])
    op.create_index("ix_ai_runs_tenant_id", "ai_runs", ["tenant_id"])

    op.create_table(
        "ai_findings",
        sa.Column("ai_run_id", sa.String(length=36), nullable=True),
        sa.Column("project_id", sa.String(length=36), nullable=True),
        sa.Column("finding_type", sa.String(length=120), nullable=False),
        sa.Column("severity", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("confidence", sa.Integer(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["ai_run_id"], ["ai_runs.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_findings_ai_run_id", "ai_findings", ["ai_run_id"])
    op.create_index("ix_ai_findings_project_id", "ai_findings", ["project_id"])
    op.create_index("ix_ai_findings_tenant_id", "ai_findings", ["tenant_id"])

    op.create_table(
        "audit_events",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("actor_user_id", sa.String(length=36), nullable=True),
        sa.Column("action", sa.String(length=160), nullable=False),
        sa.Column("resource_type", sa.String(length=120), nullable=False),
        sa.Column("resource_id", sa.String(length=120), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_events_actor_user_id", "audit_events", ["actor_user_id"])
    op.create_index("ix_audit_events_tenant_id", "audit_events", ["tenant_id"])


def downgrade() -> None:
    op.drop_table("audit_events")
    op.drop_table("ai_findings")
    op.drop_table("ai_runs")
    op.drop_table("pipeline_runs")
    op.drop_table("commits")
    op.drop_table("pull_requests")
    op.drop_table("repositories")
    op.drop_table("work_items")
    op.drop_table("sync_jobs")
    op.drop_table("integrations")
    op.drop_table("user_profiles")
    op.drop_table("projects")
    op.drop_table("tenants")
