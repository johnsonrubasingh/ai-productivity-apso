from datetime import UTC, datetime

from fastapi import APIRouter

from apso_backend.core.config import get_settings

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "service": "apso-backend",
        "environment": settings.environment,
        "timestamp": datetime.now(UTC).isoformat(),
    }

