"""Collection Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel


class CollectionCreate(BaseModel):
    name: str
    description: str | None = None
    is_public: bool = False


class CollectionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_public: bool | None = None


class CollectionResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: str | None = None
    is_public: bool
    created_at: datetime
    paper_count: int = 0

    model_config = {"from_attributes": True}


class CollectionPaperAdd(BaseModel):
    paper_id: str
