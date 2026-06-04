from pydantic import BaseModel, Field


class TenantCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    slug: str = Field(min_length=2, max_length=100)
    timezone: str = "Asia/Calcutta"


class TenantRead(BaseModel):
    id: str
    name: str
    slug: str
    timezone: str
    is_active: bool

    model_config = {"from_attributes": True}


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    key: str = Field(min_length=1, max_length=80)
    description: str | None = None


class ProjectRead(BaseModel):
    id: str
    tenant_id: str
    name: str
    key: str
    description: str | None = None

    model_config = {"from_attributes": True}


class WorkItemRead(BaseModel):
    id: str
    tenant_id: str
    project_id: str | None
    source: str
    external_id: str
    issue_key: str
    issue_type: str
    status: str
    summary: str
    description: str | None = None

    model_config = {"from_attributes": True}

