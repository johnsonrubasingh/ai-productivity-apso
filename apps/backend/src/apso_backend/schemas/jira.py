from pydantic import BaseModel, Field


class JiraIssueSearchRequest(BaseModel):
    jql: str = Field(min_length=1, max_length=2000)
    max_results: int = Field(default=25, ge=1, le=100)


class JiraIssueIngestRequest(JiraIssueSearchRequest):
    project_id: str | None = None


class JiraIssueSummary(BaseModel):
    external_id: str
    issue_key: str
    issue_type: str
    status: str
    summary: str
    description_text: str | None = None
    priority: str | None = None
    assignee: str | None = None
    reporter: str | None = None
    updated: str | None = None
    source_url: str


class JiraIssueSearchResponse(BaseModel):
    total: int
    max_results: int
    issues: list[JiraIssueSummary]
    read_only: bool = True


class JiraIssueIngestResponse(BaseModel):
    total_from_jira: int
    received: int
    upserted: int
    issues: list[JiraIssueSummary]
    read_only: bool = True
