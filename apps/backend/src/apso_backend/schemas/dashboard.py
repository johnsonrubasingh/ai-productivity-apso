from pydantic import BaseModel, Field


class DashboardMetric(BaseModel):
    name: str
    value: int | str
    label: str


class ProjectHealthSummary(BaseModel):
    tenant_id: str
    project_id: str | None = None
    metrics: list[DashboardMetric] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    read_only: bool = True

