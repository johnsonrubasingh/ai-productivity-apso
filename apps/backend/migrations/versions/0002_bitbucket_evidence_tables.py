"""Add Bitbucket test and code evidence tables.

Revision ID: 0002_bitbucket_evidence_tables
Revises: 0001_initial_schema
Create Date: 2026-06-04
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0002_bitbucket_evidence_tables"
down_revision: str | None = "0001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "bitbucket_test_runs",
        sa.Column("repository_id", sa.String(length=36), nullable=True),
        sa.Column("pipeline_uuid", sa.String(length=120), nullable=False),
        sa.Column("step_uuid", sa.String(length=120), nullable=False),
        sa.Column("external_id", sa.String(length=260), nullable=False),
        sa.Column("total_tests", sa.Integer(), nullable=False),
        sa.Column("passed_tests", sa.Integer(), nullable=False),
        sa.Column("failed_tests", sa.Integer(), nullable=False),
        sa.Column("skipped_tests", sa.Integer(), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_bitbucket_test_runs_repository_id", "bitbucket_test_runs", ["repository_id"])
    op.create_index("ix_bitbucket_test_runs_pipeline_uuid", "bitbucket_test_runs", ["pipeline_uuid"])
    op.create_index("ix_bitbucket_test_runs_step_uuid", "bitbucket_test_runs", ["step_uuid"])
    op.create_index("ix_bitbucket_test_runs_tenant_id", "bitbucket_test_runs", ["tenant_id"])
    op.create_index(
        "ix_bitbucket_test_runs_tenant_external",
        "bitbucket_test_runs",
        ["tenant_id", "external_id"],
        unique=True,
    )

    op.create_table(
        "code_evidence",
        sa.Column("repository_id", sa.String(length=36), nullable=True),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("evidence_type", sa.String(length=80), nullable=False),
        sa.Column("reference", sa.String(length=260), nullable=False),
        sa.Column("file_path", sa.Text(), nullable=True),
        sa.Column("commit_sha", sa.String(length=120), nullable=True),
        sa.Column("content_excerpt", sa.Text(), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_code_evidence_repository_id", "code_evidence", ["repository_id"])
    op.create_index("ix_code_evidence_commit_sha", "code_evidence", ["commit_sha"])
    op.create_index("ix_code_evidence_tenant_id", "code_evidence", ["tenant_id"])
    op.create_index(
        "ix_code_evidence_tenant_reference",
        "code_evidence",
        ["tenant_id", "provider", "reference"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_table("code_evidence")
    op.drop_table("bitbucket_test_runs")
