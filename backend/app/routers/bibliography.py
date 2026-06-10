"""Bibliography generator router."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.paper import Paper
from app.services import bibliography as bib_service

router = APIRouter()


class BibliographyRequest(BaseModel):
    paper_ids: list[str]
    format: str  # "APA" | "IEEE" | "Chicago"


@router.post("/generate")
async def generate_bibliography(
    data: BibliographyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate bibliography in APA, IEEE, or Chicago format."""
    if not data.paper_ids:
        return {"format": data.format, "entries": []}

    # Fetch papers from database
    result = await db.execute(select(Paper).where(Paper.id.in_(data.paper_ids)))
    papers = result.scalars().all()

    # Map paper objects to dictionaries for the formatting service
    paper_dicts = []
    for paper in papers:
        paper_dicts.append({
            "title": paper.title,
            "authors": paper.authors if isinstance(paper.authors, list) else [],
            "year": paper.year,
            "doi": paper.doi,
            "url": paper.url
        })

    entries = bib_service.generate_bibliography(paper_dicts, format=data.format)
    return {"format": data.format, "entries": entries}
