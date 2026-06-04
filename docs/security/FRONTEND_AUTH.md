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

The `/auth` page stores a bearer token in browser `sessionStorage` and verifies
it through `/api/v1/auth/me`.

## Next Hardening Step

Replace manual token entry with Supabase Auth UI/session handling before a
commercial release. The backend contract is already ready for Supabase JWTs.
