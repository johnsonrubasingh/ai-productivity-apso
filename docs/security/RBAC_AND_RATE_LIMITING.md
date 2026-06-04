# APSO RBAC and Rate Limiting

APSO backend routes resolve tenant, user, and role from Supabase bearer tokens in
production. Development may use explicit dev headers only when production JWT
enforcement is not active.

## Roles

Roles are ordered from least to most privileged:

```text
viewer < developer < lead < admin < owner
```

Current policy:

- `viewer`: read-only diagnostic and list views.
- `developer`: AI analysis, scanner dry-runs, release readiness checks, proof
  pack generation, finding creation/status updates.
- `lead`: ingestion, job runner, and project setup operations.
- `admin`: tenant setup and all lower-level operations.
- `owner`: reserved for future tenant administration.

## Development Headers

Accepted development headers:

```text
x-tenant-id
x-user-id
x-role
```

APSO frontend also sends:

```text
x-apso-dev-tenant
x-apso-dev-user
x-apso-dev-role
```

Production must use Supabase bearer tokens. If `APSO_ENV=prod` and
`SUPABASE_JWT_SECRET` is configured, dev headers are rejected.

## Rate Limiting

The backend uses an in-memory fixed-window limiter for the current single-node
deployment shape.

Config:

```yaml
security:
  rate_limit_requests: 120
  rate_limit_window_seconds: 60
```

For multi-replica production, replace this with Valkey-backed distributed rate
limiting before horizontal scaling.

## Audit

The backend records audit events for setup, ingestion, job runner, and finding
mutation actions when database-backed routes execute successfully.
