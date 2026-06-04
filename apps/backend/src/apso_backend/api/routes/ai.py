from fastapi import APIRouter

from apso_backend.ai.gateway import AiGateway
from apso_backend.ai.schemas import AiTaskDefinition

router = APIRouter()


@router.get("/tasks", response_model=list[AiTaskDefinition])
def list_ai_tasks() -> list[AiTaskDefinition]:
    return AiGateway.from_settings().supported_tasks()


@router.get("/provider/health")
async def provider_health() -> dict:
    return await AiGateway.from_settings().health()
