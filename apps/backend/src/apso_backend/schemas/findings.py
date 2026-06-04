from typing import Literal

from pydantic import BaseModel, Field


FindingStatus = Literal["open", "accepted", "rejected", "false_positive", "assigned", "resolved"]


class FindingRead(BaseModel):
    id: str
    tenant_id: str
    project_id: str | None
    ai_run_id: str | None
    finding_type: str
    severity: str
    status: str
    title: str
    description: str
    evidence: list
    confidence: int | None = None

    model_config = {"from_attributes": True}


class FindingStatusUpdate(BaseModel):
    status: FindingStatus


class FindingCreate(BaseModel):
    project_id: str | None = None
    ai_run_id: str | None = None
    finding_type: str = Field(min_length=2, max_length=120)
    severity: Literal["low", "medium", "high", "critical"]
    title: str = Field(min_length=5, max_length=500)
    description: str = Field(min_length=10)
    evidence: list = Field(default_factory=list)
    confidence: int | None = Field(default=None, ge=0, le=100)


class PersistedAnalysisSummary(BaseModel):
    ai_run_id: str | None = None
    finding_ids: list[str] = Field(default_factory=list)
