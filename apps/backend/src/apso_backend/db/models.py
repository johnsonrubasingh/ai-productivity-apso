from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from apso_backend.db.base import Base, IdMixin, TenantScopedMixin, TimestampMixin


class Tenant(Base, IdMixin, TimestampMixin):
    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    timezone: Mapped[str] = mapped_column(String(80), default="Asia/Calcutta", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class UserProfile(Base, IdMixin, TenantScopedMixin, TimestampMixin):
    __tablename__ = "user_profiles"

    email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    display_name: Mapped[str | None] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(80), nullable=False, default="developer")
    supabase_user_id: Mapped[str | None] = mapped_column(String(100), index=True)


class Project(Base, IdMixin, TenantScopedMixin, TimestampMixin):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    key: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)


class Integration(Base, IdMixin, TenantScopedMixin, TimestampMixin):
    __tablename__ = "integrations"

    provider: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    mode: Mapped[str] = mapped_column(String(80), nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    config: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class SyncJob(Base, IdMixin, TenantScopedMixin, TimestampMixin):
    __tablename__ = "sync_jobs"

    provider: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="pending")
    started_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    checkpoint: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)


class WorkItem(Base, IdMixin, TenantScopedMixin, TimestampMixin):
    __tablename__ = "work_items"

    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id"), index=True)
    external_id: Mapped[str] = mapped_column(String(120), nullable=False)
    source: Mapped[str] = mapped_column(String(80), nullable=False, default="jira")
    issue_key: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    issue_type: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(120), nullable=False)
    summary: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    __table_args__ = (
        Index("ix_work_items_tenant_source_external", "tenant_id", "source", "external_id", unique=True),
    )


class Repository(Base, IdMixin, TenantScopedMixin, TimestampMixin):
    __tablename__ = "repositories"

    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id"), index=True)
    provider: Mapped[str] = mapped_column(String(80), nullable=False)
    workspace: Mapped[str | None] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(200), nullable=False)
    default_branch: Mapped[str] = mapped_column(String(120), nullable=False, default="develop")
    clone_url: Mapped[str | None] = mapped_column(Text)
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    __table_args__ = (
        Index("ix_repositories_tenant_provider_slug", "tenant_id", "provider", "slug", unique=True),
    )


class PullRequest(Base, IdMixin, TenantScopedMixin, TimestampMixin):
    __tablename__ = "pull_requests"

    repository_id: Mapped[str | None] = mapped_column(ForeignKey("repositories.id"), index=True)
    external_id: Mapped[str] = mapped_column(String(120), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    state: Mapped[str] = mapped_column(String(80), nullable=False)
    source_branch: Mapped[str | None] = mapped_column(String(200))
    target_branch: Mapped[str | None] = mapped_column(String(200))
    author: Mapped[str | None] = mapped_column(String(320))
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class Commit(Base, IdMixin, TenantScopedMixin, TimestampMixin):
    __tablename__ = "commits"

    repository_id: Mapped[str | None] = mapped_column(ForeignKey("repositories.id"), index=True)
    hash: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    message: Mapped[str | None] = mapped_column(Text)
    author: Mapped[str | None] = mapped_column(String(320))
    branch: Mapped[str | None] = mapped_column(String(200))
    committed_at: Mapped[str | None] = mapped_column(String(80))
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    __table_args__ = (
        Index("ix_commits_tenant_repository_hash", "tenant_id", "repository_id", "hash", unique=True),
    )


class PipelineRun(Base, IdMixin, TenantScopedMixin, TimestampMixin):
    __tablename__ = "pipeline_runs"

    repository_id: Mapped[str | None] = mapped_column(ForeignKey("repositories.id"), index=True)
    external_id: Mapped[str] = mapped_column(String(120), nullable=False)
    provider: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(80), nullable=False)
    branch: Mapped[str | None] = mapped_column(String(200))
    commit_sha: Mapped[str | None] = mapped_column(String(120), index=True)
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class AiRun(Base, IdMixin, TenantScopedMixin, TimestampMixin):
    __tablename__ = "ai_runs"

    task_name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(80), nullable=False)
    model_name: Mapped[str] = mapped_column(String(160), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    validation_result: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class AiFinding(Base, IdMixin, TenantScopedMixin, TimestampMixin):
    __tablename__ = "ai_findings"

    ai_run_id: Mapped[str | None] = mapped_column(ForeignKey("ai_runs.id"), index=True)
    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id"), index=True)
    finding_type: Mapped[str] = mapped_column(String(120), nullable=False)
    severity: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="open")
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    confidence: Mapped[int | None] = mapped_column(Integer)


class AuditEvent(Base, IdMixin, TenantScopedMixin):
    __tablename__ = "audit_events"

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    actor_user_id: Mapped[str | None] = mapped_column(String(36), index=True)
    action: Mapped[str] = mapped_column(String(160), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(120), nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(120))
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
