from typing import Literal

from pydantic import BaseModel, Field


MetricLabel = Literal["actual", "estimated", "ai_inferred", "sample", "placeholder"]


class ProofMetric(BaseModel):
    name: str
    value: str
    label: MetricLabel
    evidence: str


class ProofPackRequest(BaseModel):
    project_id: str | None = None
    title: str = "APSO AI Productivity Proof Pack"
    include_placeholders: bool = True


class ProofPackSection(BaseModel):
    title: str
    summary: str
    metrics: list[ProofMetric] = Field(default_factory=list)


class ProofPackResponse(BaseModel):
    title: str
    sections: list[ProofPackSection]
    read_only: bool = True

