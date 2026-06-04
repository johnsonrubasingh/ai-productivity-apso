from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apso_backend.db.session import get_optional_db_session
from apso_backend.schemas.dashboard import ProjectHealthSummary
from apso_backend.security.context import RequestContext, get_request_context
from apso_backend.services.dashboard import DashboardService

router = APIRouter()


@router.get("/project-health", response_model=ProjectHealthSummary)
def project_health(
    project_id: str | None = None,
    context: RequestContext = Depends(get_request_context),
    session: Session | None = Depends(get_optional_db_session),
) -> ProjectHealthSummary:
    return DashboardService(session).project_health(tenant_id=context.tenant_id, project_id=project_id)

