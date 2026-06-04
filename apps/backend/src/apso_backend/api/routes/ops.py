from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from apso_backend.core.metrics import metrics_registry
from apso_backend.schemas.ops import ReadinessResponse
from apso_backend.services.readiness import ReadinessService

router = APIRouter()


@router.get("/readiness", response_model=ReadinessResponse)
def readiness() -> ReadinessResponse:
    return ReadinessService().check()


@router.get("/metrics", response_class=PlainTextResponse)
def metrics() -> str:
    return metrics_registry.render_prometheus()
