"""Database and file storage cleanup service to prevent server bloat and memory leaks."""

import os
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, delete, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.models.paper import Paper, AISummary
from app.models.collection import CollectionPaper

logger = logging.getLogger(__name__)

UPLOADS_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"


async def purge_all_uploaded_papers(db: AsyncSession | None = None) -> dict:
    """Purge all uploaded papers and their physical PDF files."""
    removed_files = 0
    deleted_rows = 0

    # 1. Clear physical PDF files
    if UPLOADS_DIR.exists():
        for file in UPLOADS_DIR.glob("*"):
            if file.is_file() and file.name != ".gitkeep":
                try:
                    os.remove(file)
                    removed_files += 1
                except Exception as e:
                    logger.warning(f"Failed to delete file {file}: {e}")

    # 2. Clear DB records
    async def _do_delete(session: AsyncSession):
        nonlocal deleted_rows
        try:
            res = await session.execute(text("DELETE FROM papers WHERE source = 'uploaded'"))
            deleted_rows = res.rowcount if hasattr(res, 'rowcount') else 0
            await session.commit()
        except Exception as e:
            logger.warning(f"Failed to delete uploaded paper records from DB: {e}")

    if db:
        await _do_delete(db)
    else:
        async with async_session_factory() as session:
            await _do_delete(session)

    logger.info(f"Purged {deleted_rows} uploaded paper records and {removed_files} physical PDF files.")
    return {"deleted_records": deleted_rows, "removed_files": removed_files}


async def prune_stale_cache_papers(days: int = 14) -> int:
    """Prune cached search papers older than N days if NOT saved in any user's collection."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    pruned_count = 0

    try:
        async with async_session_factory() as db:
            # Get IDs of all papers saved in user collections
            saved_result = await db.execute(select(CollectionPaper.paper_id).distinct())
            saved_paper_ids = set(saved_result.scalars().all())

            # Find stale search papers
            stmt = select(Paper.id).where(
                Paper.source.in_(["semantic_scholar", "arxiv", "openalex"]),
                Paper.cached_at < cutoff,
            )
            if saved_paper_ids:
                stmt = stmt.where(~Paper.id.in_(saved_paper_ids))

            stale_result = await db.execute(stmt)
            stale_ids = stale_result.scalars().all()

            if stale_ids:
                await db.execute(delete(Paper).where(Paper.id.in_(stale_ids)))
                await db.commit()
                pruned_count = len(stale_ids)
                logger.info(f"Auto-pruned {pruned_count} stale search paper cache records older than {days} days.")
    except Exception as e:
        logger.warning(f"Failed to prune stale search paper cache: {e}")

    return pruned_count


async def cleanup_orphan_files() -> int:
    """Remove any PDF files in uploads/ directory that are not referenced in DB."""
    removed_count = 0
    if not UPLOADS_DIR.exists():
        return 0

    try:
        async with async_session_factory() as db:
            result = await db.execute(
                select(Paper.uploaded_file_path).where(
                    Paper.source == "uploaded",
                    Paper.uploaded_file_path.is_not(None),
                )
            )
            valid_paths = set(result.scalars().all())

            for file in UPLOADS_DIR.glob("*"):
                if file.is_file() and file.name != ".gitkeep":
                    if str(file) not in valid_paths:
                        try:
                            os.remove(file)
                            removed_count += 1
                        except Exception as e:
                            logger.warning(f"Failed to remove orphan file {file}: {e}")
    except Exception as e:
        logger.warning(f"Orphan file cleanup failed: {e}")

    return removed_count
