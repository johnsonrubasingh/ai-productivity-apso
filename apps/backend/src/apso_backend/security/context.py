from dataclasses import dataclass
import os
from collections.abc import Iterable

from fastapi import Depends, Header, HTTPException, status

from apso_backend.core.config import get_settings
from apso_backend.security.jwt import verify_supabase_jwt


@dataclass(frozen=True)
class RequestContext:
    tenant_id: str
    user_id: str
    role: str


ROLE_RANKS = {
    "viewer": 10,
    "developer": 20,
    "lead": 30,
    "admin": 40,
    "owner": 50,
}


def normalize_role(role: str | None) -> str:
    return (role or "viewer").lower().strip()


def has_any_role(context: RequestContext, allowed_roles: Iterable[str]) -> bool:
    allowed = {normalize_role(role) for role in allowed_roles}
    return normalize_role(context.role) in allowed


def has_min_role(context: RequestContext, minimum_role: str) -> bool:
    return ROLE_RANKS.get(normalize_role(context.role), 0) >= ROLE_RANKS[normalize_role(minimum_role)]


def require_role(*allowed_roles: str):
    async def dependency(context: RequestContext = Depends(get_request_context)) -> RequestContext:
        if not has_any_role(context, allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{context.role}' is not permitted for this action",
            )
        return context

    return dependency


def require_min_role(minimum_role: str):
    async def dependency(context: RequestContext = Depends(get_request_context)) -> RequestContext:
        if not has_min_role(context, minimum_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{context.role}' is below required role '{minimum_role}'",
            )
        return context

    return dependency


async def get_request_context(
    authorization: str | None = Header(default=None),
    x_tenant_id: str | None = Header(default=None),
    x_user_id: str | None = Header(default=None),
    x_role: str | None = Header(default=None),
    x_apso_dev_tenant: str | None = Header(default=None),
    x_apso_dev_user: str | None = Header(default=None),
    x_apso_dev_role: str | None = Header(default=None),
) -> RequestContext:
    """Resolve request context from Supabase JWT.

    Dev fallback headers are allowed only when the configured JWT secret
    environment variable is not set. Production must provide a valid bearer token.
    """

    settings = get_settings()
    jwt_secret = os.getenv(settings.supabase.jwt_secret_env)
    tenant_header = x_tenant_id or x_apso_dev_tenant
    user_header = x_user_id or x_apso_dev_user
    role_header = x_role or x_apso_dev_role

    if authorization and authorization.lower().startswith("bearer "):
        if not jwt_secret:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Supabase JWT secret is not configured",
            )
        token = authorization.split(" ", 1)[1].strip()
        verified = verify_supabase_jwt(token, jwt_secret)
        tenant_id = (
            verified.claims.get("tenant_id")
            or verified.claims.get("app_metadata", {}).get("tenant_id")
            or tenant_header
        )
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="JWT is valid but tenant context is missing",
            )
        return RequestContext(
            tenant_id=str(tenant_id),
            user_id=verified.subject,
            role=normalize_role(str(verified.role or "authenticated")),
        )

    if jwt_secret and settings.environment == "prod":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    if not tenant_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing tenant context. Provide a Supabase bearer token or dev headers.",
        )
    return RequestContext(
        tenant_id=tenant_header,
        user_id=user_header or "dev-user",
        role=normalize_role(role_header or "developer"),
    )
