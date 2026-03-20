from typing import Optional

from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class AgentRunRequest(BaseModel):
    workflow_name: str
    query: str
    entity_id: str | None = None
    entity_type: str | None = None
    lead_list: list[dict] | None = None


class SaveEntityRequest(BaseModel):
    entity_id: str
    entity_type: str
    entity_name: str
    note: Optional[str] = None
    tags: Optional[list[str]] = Field(default_factory=list)


class UpdatePreferencesRequest(BaseModel):
    display_name: Optional[str] = None
    preferences: Optional[dict] = None


class CreateApiKeyRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    expires_in_days: Optional[int] = Field(default=None, ge=1, le=365)
