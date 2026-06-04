from fastapi import APIRouter, Depends

from apso_backend.security.context import RequestContext, get_request_context

router = APIRouter()


@router.get("/me")
async def current_user(context: RequestContext = Depends(get_request_context)) -> dict[str, str]:
    return {
        "tenant_id": context.tenant_id,
        "user_id": context.user_id,
        "role": context.role,
    }

