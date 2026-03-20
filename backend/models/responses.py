from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int
    has_more: bool

    @classmethod
    def build(cls, items: list[T], total: int, limit: int, offset: int) -> "PaginatedResponse[T]":
        return cls(items=items, total=total, limit=limit, offset=offset, has_more=offset + limit < total)


class AgentRunResponse(BaseModel):
    run_id: str
    workflow_name: str
    status: str
    result: dict | None = None
    steps_log: list[str] = []
    citations: list[dict] = []
    duration_ms: int = 0
