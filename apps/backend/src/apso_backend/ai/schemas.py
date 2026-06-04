from typing import Literal

from pydantic import BaseModel, Field


AiTaskName = Literal[
    "requirement_gap_analysis",
    "code_quality_explanation",
    "coverage_verification",
    "release_risk_summary",
    "executive_report_generation",
]


class AiTaskDefinition(BaseModel):
    name: AiTaskName
    description: str
    provider: Literal["ollama"]
    model: str
    prompt_version: str
    structured_output_required: bool = True
    evidence_required: bool = True


class EvidenceRef(BaseModel):
    source: Literal["jira", "bitbucket", "aws", "scanner", "manual"]
    artifact_type: str
    artifact_id: str
    url: str | None = None
    summary: str


class AiFindingOutput(BaseModel):
    finding_type: str
    severity: Literal["low", "medium", "high", "critical"]
    title: str = Field(min_length=5, max_length=300)
    description: str = Field(min_length=10)
    recommendation: str = Field(min_length=10)
    confidence: int = Field(ge=0, le=100)
    evidence: list[EvidenceRef] = Field(min_length=1)
    metric_label: Literal["actual", "estimated", "ai_inferred", "sample", "placeholder"]


class RequirementGapInput(BaseModel):
    tenant_id: str
    project_id: str
    issue_key: str
    summary: str
    description: str | None = None
    acceptance_criteria: str | None = None
    comments: list[str] = Field(default_factory=list)


class RequirementGapOutput(BaseModel):
    issue_key: str
    quality_score: int = Field(ge=0, le=100)
    findings: list[AiFindingOutput]
    ai_run_id: str | None = None
    finding_ids: list[str] = Field(default_factory=list)
