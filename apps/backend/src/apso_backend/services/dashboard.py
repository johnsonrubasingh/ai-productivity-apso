from sqlalchemy import func, select
from sqlalchemy.orm import Session

from apso_backend.db.models import AiFinding, PipelineRun, PullRequest, Repository, WorkItem
from apso_backend.schemas.dashboard import DashboardMetric, ProjectHealthSummary


class DashboardService:
    def __init__(self, session: Session | None = None):
        self.session = session

    def project_health(self, *, tenant_id: str, project_id: str | None = None) -> ProjectHealthSummary:
        if self.session is None:
            return ProjectHealthSummary(
                tenant_id=tenant_id,
                project_id=project_id,
                metrics=[
                    DashboardMetric(name="Work items", value="DB not configured", label="placeholder"),
                    DashboardMetric(name="Open findings", value="DB not configured", label="placeholder"),
                ],
                notes=["Database is not configured; live project metrics are unavailable."],
            )

        filters = [WorkItem.tenant_id == tenant_id]
        finding_filters = [AiFinding.tenant_id == tenant_id]
        repo_filters = [Repository.tenant_id == tenant_id]
        if project_id:
            filters.append(WorkItem.project_id == project_id)
            finding_filters.append(AiFinding.project_id == project_id)
            repo_filters.append(Repository.project_id == project_id)

        work_items = self.session.scalar(select(func.count()).select_from(WorkItem).where(*filters)) or 0
        open_findings = (
            self.session.scalar(
                select(func.count()).select_from(AiFinding).where(*finding_filters, AiFinding.status == "open")
            )
            or 0
        )
        repositories = self.session.scalar(select(func.count()).select_from(Repository).where(*repo_filters)) or 0
        pull_requests = (
            self.session.scalar(
                select(func.count())
                .select_from(PullRequest)
                .join(Repository, PullRequest.repository_id == Repository.id, isouter=True)
                .where(PullRequest.tenant_id == tenant_id)
            )
            or 0
        )
        pipelines = self.session.scalar(select(func.count()).select_from(PipelineRun).where(PipelineRun.tenant_id == tenant_id)) or 0

        return ProjectHealthSummary(
            tenant_id=tenant_id,
            project_id=project_id,
            metrics=[
                DashboardMetric(name="Work items", value=int(work_items), label="actual"),
                DashboardMetric(name="Open findings", value=int(open_findings), label="actual"),
                DashboardMetric(name="Repositories", value=int(repositories), label="actual"),
                DashboardMetric(name="Pull requests", value=int(pull_requests), label="actual"),
                DashboardMetric(name="Pipeline runs", value=int(pipelines), label="actual"),
            ],
            notes=["Metrics are based only on data ingested into APSO."],
        )

