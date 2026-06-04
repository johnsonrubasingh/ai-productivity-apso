from sqlalchemy import select
from sqlalchemy.orm import Session

from apso_backend.db.models import WorkItem
from apso_backend.schemas.jira import JiraIssueSummary


class WorkItemRepository:
    def __init__(self, session: Session):
        self.session = session

    def upsert_jira_issue(
        self,
        *,
        tenant_id: str,
        project_id: str | None,
        issue: JiraIssueSummary,
        raw_payload: dict,
    ) -> WorkItem:
        existing = self.session.scalar(
            select(WorkItem).where(
                WorkItem.tenant_id == tenant_id,
                WorkItem.source == "jira",
                WorkItem.external_id == issue.external_id,
            )
        )
        if existing is None:
            existing = WorkItem(
                tenant_id=tenant_id,
                project_id=project_id,
                external_id=issue.external_id,
                source="jira",
                issue_key=issue.issue_key,
                issue_type=issue.issue_type,
                status=issue.status,
                summary=issue.summary,
                description=issue.description_text,
                raw_payload=raw_payload,
            )
            self.session.add(existing)
        else:
            existing.project_id = project_id
            existing.issue_key = issue.issue_key
            existing.issue_type = issue.issue_type
            existing.status = issue.status
            existing.summary = issue.summary
            existing.description = issue.description_text
            existing.raw_payload = raw_payload

        return existing

