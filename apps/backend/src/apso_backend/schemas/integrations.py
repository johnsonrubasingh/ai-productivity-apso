from pydantic import BaseModel


class IntegrationSummary(BaseModel):
    provider: str
    mode: str
    status: str
    read_only: bool
    configured: bool
    details: dict[str, str | int | bool | list[str]]

