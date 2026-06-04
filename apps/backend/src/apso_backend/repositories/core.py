from sqlalchemy import select
from sqlalchemy.orm import Session

from apso_backend.db.models import Project, Tenant, WorkItem
from apso_backend.schemas.core import ProjectCreate, TenantCreate


class TenantRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, payload: TenantCreate) -> Tenant:
        tenant = Tenant(
            name=payload.name,
            slug=payload.slug,
            timezone=payload.timezone,
            is_active=True,
        )
        self.session.add(tenant)
        self.session.commit()
        self.session.refresh(tenant)
        return tenant

    def list(self) -> list[Tenant]:
        return list(self.session.scalars(select(Tenant).order_by(Tenant.created_at.desc())))


class ProjectRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, *, tenant_id: str, payload: ProjectCreate) -> Project:
        project = Project(
            tenant_id=tenant_id,
            name=payload.name,
            key=payload.key,
            description=payload.description,
        )
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)
        return project

    def list_for_tenant(self, tenant_id: str) -> list[Project]:
        return list(
            self.session.scalars(
                select(Project).where(Project.tenant_id == tenant_id).order_by(Project.created_at.desc())
            )
        )


class WorkItemReadRepository:
    def __init__(self, session: Session):
        self.session = session

    def list_for_tenant(self, tenant_id: str, limit: int = 100) -> list[WorkItem]:
        return list(
            self.session.scalars(
                select(WorkItem)
                .where(WorkItem.tenant_id == tenant_id)
                .order_by(WorkItem.updated_at.desc())
                .limit(limit)
            )
        )

