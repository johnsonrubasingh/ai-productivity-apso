from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from apso_backend.db.session import get_db_session
from apso_backend.repositories.findings import FindingRepository
from apso_backend.schemas.findings import FindingCreate, FindingRead, FindingStatusUpdate
from apso_backend.security.context import RequestContext, get_request_context, require_min_role
from apso_backend.services.audit import AuditService

router = APIRouter()


@router.post("", response_model=FindingRead)
def create_finding(
    payload: FindingCreate,
    context: RequestContext = Depends(require_min_role("developer")),
    session: Session = Depends(get_db_session),
) -> FindingRead:
    finding = FindingRepository(session).create(tenant_id=context.tenant_id, payload=payload)
    AuditService(session).record(
        context=context,
        action="finding.created",
        resource_type="ai_finding",
        resource_id=finding.id,
        metadata={"severity": finding.severity, "finding_type": finding.finding_type},
        commit=True,
    )
    return FindingRead.model_validate(finding)


@router.get("", response_model=list[FindingRead])
def list_findings(
    status: str | None = None,
    limit: int = 100,
    context: RequestContext = Depends(get_request_context),
    session: Session = Depends(get_db_session),
) -> list[FindingRead]:
    if limit < 1 or limit > 500:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 500")
    findings = FindingRepository(session).list_for_tenant(
        tenant_id=context.tenant_id,
        status=status,
        limit=limit,
    )
    return [FindingRead.model_validate(finding) for finding in findings]


@router.patch("/{finding_id}/status", response_model=FindingRead)
def update_finding_status(
    finding_id: str,
    payload: FindingStatusUpdate,
    context: RequestContext = Depends(require_min_role("developer")),
    session: Session = Depends(get_db_session),
) -> FindingRead:
    finding = FindingRepository(session).update_status(
        tenant_id=context.tenant_id,
        finding_id=finding_id,
        status=payload.status,
    )
    if finding is None:
        raise HTTPException(status_code=404, detail="Finding not found")
    AuditService(session).record(
        context=context,
        action="finding.status_updated",
        resource_type="ai_finding",
        resource_id=finding.id,
        metadata={"status": payload.status},
        commit=True,
    )
    return FindingRead.model_validate(finding)
