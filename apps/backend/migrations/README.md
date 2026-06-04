# APSO Backend Migrations

Alembic is the locked migration tool for the backend.

The bundled runtime used by Codex in this session does not include Alembic,
but the backend `pyproject.toml` declares it as a project dependency.

Rules:

- Every schema change must have a migration.
- Do not manually change production schema.
- Do not add tenant data tables without tenant isolation.
- Do not store raw secrets in migrations or seed data.

