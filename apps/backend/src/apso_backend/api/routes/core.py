from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from apso_backend.db.session import get_db_session
from apso_backend.repositories.core import ProjectRepository, TenantRepository, WorkItemReadRepository
from apso_backend.schemas.core import ProjectCreate, ProjectRead, TenantCreate, TenantRead, WorkItemRead
from apso_backend.security.context import RequestContext, get_request_context, require_min_role
from apso_backend.services.audit import AuditService

router = APIRouter()


@router.post("/tenants", response_model=TenantRead)
def create_tenant(
    payload: TenantCreate,
    context: RequestContext = Depends(require_min_role("admin")),
    session: Session = Depends(get_db_session),
) -> TenantRead:
    tenant = TenantRepository(session).create(payload)
    AuditService(session).record(
        context=context,
        action="tenant.created",
        resource_type="tenant",
        resource_id=tenant.id,
        metadata={"slug": tenant.slug},
        commit=True,
    )
    return TenantRead.model_validate(tenant)


@router.get("/tenants", response_model=list[TenantRead])
def list_tenants(session: Session = Depends(get_db_session)) -> list[TenantRead]:
    return [TenantRead.model_validate(tenant) for tenant in TenantRepository(session).list()]


@router.post("/projects", response_model=ProjectRead)
def create_project(
    payload: ProjectCreate,
    context: RequestContext = Depends(require_min_role("lead")),
    session: Session = Depends(get_db_session),
) -> ProjectRead:
    project = ProjectRepository(session).create(tenant_id=context.tenant_id, payload=payload)
    AuditService(session).record(
        context=context,
        action="project.created",
        resource_type="project",
        resource_id=project.id,
        metadata={"key": project.key},
        commit=True,
    )
    return ProjectRead.model_validate(project)


@router.get("/projects", response_model=list[ProjectRead])
def list_projects(
    context: RequestContext = Depends(get_request_context),
    session: Session = Depends(get_db_session),
) -> list[ProjectRead]:
    return [
        ProjectRead.model_validate(project)
        for project in ProjectRepository(session).list_for_tenant(context.tenant_id)
    ]


@router.get("/work-items", response_model=list[WorkItemRead])
def list_work_items(
    limit: int = 100,
    context: RequestContext = Depends(get_request_context),
    session: Session = Depends(get_db_session),
) -> list[WorkItemRead]:
    if limit < 1 or limit > 500:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 500")
    return [
        WorkItemRead.model_validate(item)
        for item in WorkItemReadRepository(session).list_for_tenant(context.tenant_id, limit=limit)
    ]
