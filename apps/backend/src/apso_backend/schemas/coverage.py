from pydantic import BaseModel, Field


class CoverageVerificationRequest(BaseModel):
    work_item_key: str
    linked_commits: int = Field(default=0, ge=0)
    linked_pull_requests: int = Field(default=0, ge=0)
    linked_test_runs: int = Field(default=0, ge=0)
    successful_pipeline_runs: int = Field(default=0, ge=0)
    coverage_percent: float | None = Field(default=None, ge=0, le=100)


class CoverageGap(BaseModel):
    gap_type: str
    severity: str
    description: str
    recommendation: str


class CoverageVerificationResponse(BaseModel):
    work_item_key: str
    coverage_confidence_score: int = Field(ge=0, le=100)
    gaps: list[CoverageGap]
    evidence_label: str = "actual_or_placeholder_inputs"
    read_only: bool = True

