"""Paper Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel


class PaperResponse(BaseModel):
    id: str
    external_id: str
    source: str
    title: str
    authors: list[str]
    abstract: str | None = None
    year: int | None = None
    doi: str | None = None
    url: str | None = None
    citation_count: int = 0
    fields_of_study: list[str] = []
    cached_at: datetime

    model_config = {"from_attributes": True}


class PaperSearchResponse(BaseModel):
    query: str
    results: list[PaperResponse]
    total: int


class AISummaryResponse(BaseModel):
    id: str
    paper_id: str
    summary_text: str
    key_findings: list[str]
    methodology: str | None = None
    generated_at: datetime

    model_config = {"from_attributes": True}
