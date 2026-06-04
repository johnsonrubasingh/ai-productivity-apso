# APSO Frontend Auth

The frontend must not use development headers in production.

## Development

When `NODE_ENV !== production`, the frontend API helper may send APSO development
headers so local developers can exercise backend routes without a Supabase login
flow.

```text
X-APSO-Dev-User
X-APSO-Dev-Tenant
X-APSO-Dev-Role
```

These headers are rejected by the backend in `APSO_ENV=prod` when
`SUPABASE_JWT_SECRET` is configured.

## Production

When `NODE_ENV=production`, the frontend sends no development headers. Protected
calls require a bearer token:

```text
Authorization: Bearer <supabase-access-token>
```

The `/auth` page uses Supabase Auth email/password sign-in when these public
frontend variables are configured:

```text
NEXT_PUBLIC_SUPABASE_URL
NEXT_PUBLIC_SUPABASE_ANON_KEY
```

After sign-in, the returned Supabase access token is mirrored into
`sessionStorage` for backend API calls and verified through `/api/v1/auth/me`.
Manual bearer-token entry remains available as a development and troubleshooting
fallback.

## Remaining Hardening

Before commercial production, validate the full browser sign-in, token refresh,
sign-out, and backend `/auth/me` flow against the target Supabase project in both
`dev` and `prod`.
