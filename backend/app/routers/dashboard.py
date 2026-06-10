"""Dashboard router - stats for current user."""

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.collection import Collection, CollectionPaper
from app.models.paper import AISummary

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get dynamic counts of user's saved papers, collections, and AI summaries."""
    # Number of collections
    collections_query = await db.execute(
        select(func.count(Collection.id)).where(Collection.user_id == current_user.id)
    )
    collections_count = collections_query.scalar() or 0

    # Number of papers saved in the user's collections
    papers_query = await db.execute(
        select(func.count(func.distinct(CollectionPaper.paper_id)))
        .join(Collection)
        .where(Collection.user_id == current_user.id)
    )
    papers_count = papers_query.scalar() or 0

    # Number of AI summaries for papers saved in the user's collections
    summaries_query = await db.execute(
        select(func.count(func.distinct(AISummary.id)))
        .join(CollectionPaper, AISummary.paper_id == CollectionPaper.paper_id)
        .join(Collection, CollectionPaper.collection_id == Collection.id)
        .where(Collection.user_id == current_user.id)
    )
    summaries_count = summaries_query.scalar() or 0

    return {
        "saved_papers": papers_count,
        "collections": collections_count,
        "ai_summaries": summaries_count,
    }
