"""Search history router."""

from fastapi import APIRouter, Depends, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.search_history import SearchHistory

router = APIRouter()


@router.get("/")
async def list_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List search history for the current user."""
    result = await db.execute(
        select(SearchHistory)
        .where(SearchHistory.user_id == current_user.id)
        .order_by(SearchHistory.searched_at.desc())
        .limit(limit)
    )
    rows = result.scalars().all()
    return [
        {
            "id": str(h.id),
            "query": h.query,
            "filters": h.filters,
            "result_count": h.result_count,
            "searched_at": h.searched_at.isoformat() if h.searched_at else None,
        }
        for h in rows
    ]


@router.delete("/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_history_item(
    history_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a single history entry."""
    result = await db.execute(
        select(SearchHistory).where(
            SearchHistory.id == history_id,
            SearchHistory.user_id == current_user.id,
        )
    )
    item = result.scalar_one_or_none()
    if item:
        await db.delete(item)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_all_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Clear all search history for the current user."""
    await db.execute(
        delete(SearchHistory).where(SearchHistory.user_id == current_user.id)
    )
