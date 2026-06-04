from typing import Generic, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T")


class PageMeta(BaseModel):
    limit: int = Field(ge=1)
    count: int = Field(ge=0)
    next_cursor: str | None = None


class Page(BaseModel, Generic[T]):
    items: list[T]
    meta: PageMeta


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail

