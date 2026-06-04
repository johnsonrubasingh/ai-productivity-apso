from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apso_backend.db.session import get_optional_db_session
from apso_backend.schemas.jobs import JobRunRequest, JobRunResponse
from apso_backend.security.context import RequestContext, require_min_role
from apso_backend.services.audit import AuditService
from apso_backend.services.jobs import JobRunnerService

router = APIRouter()


@router.post("/run", response_model=JobRunResponse)
async def run_job(
    request: JobRunRequest,
    context: RequestContext = Depends(require_min_role("lead")),
    session: Session | None = Depends(get_optional_db_session),
) -> JobRunResponse:
    response = await JobRunnerService(session=session).run(request=request, context=context)
    if session is not None:
        AuditService(session).record(
            context=context,
            action="job.run",
            resource_type="job",
            resource_id=request.job_name,
            metadata={"status": response.status, "mode": response.mode},
            commit=True,
        )
    return response
