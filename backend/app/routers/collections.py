"""Collections router - CRUD for paper collections."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.collection import Collection, CollectionPaper
from app.schemas.collection import (
    CollectionCreate,
    CollectionUpdate,
    CollectionResponse,
    CollectionPaperAdd,
)

router = APIRouter()


@router.get("/", response_model=list[CollectionResponse])
async def list_collections(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all collections for the current user."""
    result = await db.execute(
        select(Collection).where(Collection.user_id == current_user.id).order_by(Collection.created_at.desc())
    )
    return result.scalars().all()


@router.post("/", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
async def create_collection(
    data: CollectionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new collection."""
    collection = Collection(
        user_id=current_user.id,
        name=data.name,
        description=data.description,
        is_public=data.is_public,
    )
    db.add(collection)
    await db.flush()
    await db.refresh(collection)
    return CollectionResponse.model_validate(collection)


@router.put("/{collection_id}", response_model=CollectionResponse)
async def update_collection(
    collection_id: str,
    data: CollectionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a collection."""
    result = await db.execute(
        select(Collection).where(Collection.id == collection_id, Collection.user_id == current_user.id)
    )
    collection = result.scalar_one_or_none()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    if data.name is not None:
        collection.name = data.name
    if data.description is not None:
        collection.description = data.description
    if data.is_public is not None:
        collection.is_public = data.is_public
    await db.flush()
    await db.refresh(collection)
    return CollectionResponse.model_validate(collection)


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(
    collection_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a collection."""
    result = await db.execute(
        select(Collection).where(Collection.id == collection_id, Collection.user_id == current_user.id)
    )
    collection = result.scalar_one_or_none()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    await db.delete(collection)


@router.post("/{collection_id}/papers", status_code=status.HTTP_201_CREATED)
async def add_paper_to_collection(
    collection_id: str,
    data: CollectionPaperAdd,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a paper to a collection."""
    # Verify collection ownership
    result = await db.execute(
        select(Collection).where(Collection.id == collection_id, Collection.user_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Collection not found")

    cp = CollectionPaper(collection_id=collection_id, paper_id=data.paper_id)
    db.add(cp)
    await db.flush()
    return {"message": "Paper added to collection"}


@router.delete("/{collection_id}/papers/{paper_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_paper_from_collection(
    collection_id: str,
    paper_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a paper from a collection."""
    result = await db.execute(
        select(CollectionPaper).where(
            CollectionPaper.collection_id == collection_id,
            CollectionPaper.paper_id == paper_id,
        )
    )
    cp = result.scalar_one_or_none()
    if cp:
        await db.delete(cp)


@router.put("/{collection_id}/papers/{paper_id}/notes")
async def update_paper_notes(
    collection_id: str,
    paper_id: str,
    notes: str = "",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update notes for a paper in a collection."""
    result = await db.execute(
        select(CollectionPaper).where(
            CollectionPaper.collection_id == collection_id,
            CollectionPaper.paper_id == paper_id,
        )
    )
    cp = result.scalar_one_or_none()
    if not cp:
        raise HTTPException(status_code=404, detail="Paper not in collection")
    cp.notes = notes
    await db.flush()
    return {"message": "Notes updated"}
