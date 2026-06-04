from pydantic import BaseModel, Field


class ReleaseReadinessRequest(BaseModel):
    project_id: str | None = None
    release_name: str
    open_high_risk_findings: int = Field(default=0, ge=0)
    failed_pipeline_runs: int = Field(default=0, ge=0)
    stories_without_tests: int = Field(default=0, ge=0)
    unresolved_requirement_gaps: int = Field(default=0, ge=0)


class ReleaseReadinessResponse(BaseModel):
    release_name: str
    readiness_score: int = Field(ge=0, le=100)
    status: str
    blockers: list[str]
    read_only: bool = True

