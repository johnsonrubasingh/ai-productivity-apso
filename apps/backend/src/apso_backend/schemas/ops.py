from pydantic import BaseModel, Field


class ReadinessCheck(BaseModel):
    name: str
    status: str
    detail: str


class ReadinessResponse(BaseModel):
    status: str
    checks: list[ReadinessCheck] = Field(default_factory=list)

