from fastapi import APIRouter

from apso_backend.core.config import get_settings
from apso_backend.core.redaction import redact_mapping

router = APIRouter()


@router.get("/runtime")
def runtime_config() -> dict:
    settings = get_settings()
    return redact_mapping(settings.model_dump(mode="json"))

