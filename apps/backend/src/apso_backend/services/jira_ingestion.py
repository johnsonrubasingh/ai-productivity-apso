from pydantic import BaseModel
from sqlalchemy.orm import Session

from apso_backend.integrations.jira.normalizer import normalize_issue
from apso_backend.integrations.jira.client import JiraClient
from apso_backend.repositories.work_items import WorkItemRepository
from apso_backend.schemas.jira import JiraIssueSummary


class JiraIngestionResult(BaseModel):
    total_from_jira: int
    received: int
    upserted: int
    issues: list[JiraIssueSummary]
    read_only: bool = True


class JiraIngestionService:
    def __init__(self, session: Session):
        self.session = session

    async def search_and_ingest(
        self,
        *,
        tenant_id: str,
        project_id: str | None,
        jql: str,
        max_results: int,
    ) -> JiraIngestionResult:
        client = JiraClient.from_settings()
        payload = await client.search_issues(jql=jql, max_results=max_results)
        raw_issues = payload.get("issues", [])
        normalized = [normalize_issue(issue, client.settings) for issue in raw_issues]

        repo = WorkItemRepository(self.session)
        for raw_issue, issue in zip(raw_issues, normalized, strict=False):
            repo.upsert_jira_issue(
                tenant_id=tenant_id,
                project_id=project_id,
                issue=issue,
                raw_payload=raw_issue,
            )
        self.session.commit()

        return JiraIngestionResult(
            total_from_jira=int(payload.get("total", len(raw_issues))),
            received=len(raw_issues),
            upserted=len(normalized),
            issues=normalized,
        )

