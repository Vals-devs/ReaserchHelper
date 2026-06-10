"""Paper search router - aggregate results from Semantic Scholar + arXiv."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/search")
async def search_papers(
    q: str = Query(..., min_length=1, description="Search query"),
    source: str = Query("all", description="Source: all, semantic_scholar, arxiv"),
    year_from: int | None = Query(None, description="Filter: year from"),
    year_to: int | None = Query(None, description="Filter: year to"),
    field: str | None = Query(None, description="Filter: field of study"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search papers from Semantic Scholar and/or arXiv."""
    # TODO: Implement search aggregation logic
    return {"query": q, "results": [], "total": 0}


@router.get("/{paper_id}")
async def get_paper(
    paper_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get paper details by ID."""
    # TODO: Implement paper detail fetch
    return {"paper_id": paper_id}


@router.get("/{paper_id}/related")
async def get_related_papers(
    paper_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get related papers via AI keyword extraction + Semantic Scholar."""
    # TODO: Implement related paper suggestion
    return {"paper_id": paper_id, "related": []}
