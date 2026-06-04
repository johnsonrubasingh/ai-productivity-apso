# APSO SQL Scripts

This folder contains reviewed SQL scripts that are separate from Alembic schema
migrations.

## Files

- `001_rls_policies.sql`: tenant isolation baseline for Supabase/Postgres RLS.

## Rules

- Review SQL before applying to a live database.
- Apply migrations before applying RLS policies.
- The backend must set `app.current_tenant_id` for RLS-enforced transactions.
- Do not place credentials in SQL scripts.

