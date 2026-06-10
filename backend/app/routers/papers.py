"""Paper search router - aggregate results from Semantic Scholar + arXiv."""

import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.paper import Paper
from app.models.search_history import SearchHistory
from app.services import semantic_scholar as s2_service
from app.services import arxiv as arxiv_service

logger = logging.getLogger(__name__)

router = APIRouter()


async def _noop_s2():
    return {"results": [], "total": 0}


async def _noop_arxiv():
    return []


def _merge_results(s2_results: list[dict], arxiv_results: list[dict]) -> list[dict]:
    """Merge and deduplicate results from both sources."""
    seen_doi: set[str] = set()
    seen_titles: set[str] = set()
    merged: list[dict] = []

    # Add Semantic Scholar results first (they have citation data)
    for paper in s2_results:
        title_key = paper["title"].lower().strip()[:80]
        doi = paper.get("doi")
        if doi:
            seen_doi.add(doi.lower())
        seen_titles.add(title_key)
        merged.append(paper)

    # Add arXiv results, skipping duplicates
    for paper in arxiv_results:
        title_key = paper["title"].lower().strip()[:80]
        doi = paper.get("doi")
        if doi and doi.lower() in seen_doi:
            continue
        if title_key in seen_titles:
            continue
        if doi:
            seen_doi.add(doi.lower())
        seen_titles.add(title_key)
        merged.append(paper)

    return merged


async def _cache_paper(db: AsyncSession, paper_data: dict) -> Paper:
    """Save or update a paper in the database cache."""
    # Check if paper already exists
    result = await db.execute(
        select(Paper).where(
            Paper.external_id == paper_data["external_id"],
            Paper.source == paper_data["source"],
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        # Update citation count if higher
        if paper_data.get("citation_count", 0) > existing.citation_count:
            existing.citation_count = paper_data["citation_count"]
        return existing

    # Create new paper record
    paper = Paper(
        external_id=paper_data["external_id"],
        source=paper_data["source"],
        title=paper_data["title"],
        authors=paper_data.get("authors", []),
        abstract=paper_data.get("abstract"),
        year=paper_data.get("year"),
        doi=paper_data.get("doi"),
        url=paper_data.get("url"),
        citation_count=paper_data.get("citation_count", 0),
        fields_of_study=paper_data.get("fields_of_study", []),
    )
    db.add(paper)
    await db.flush()
    return paper


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
    """Search papers from Semantic Scholar and/or arXiv concurrently."""
    errors: list[str] = []
    s2_results: list[dict] = []
    arxiv_results: list[dict] = []

    # Fetch from both sources concurrently
    tasks = []

    if source in ("all", "semantic_scholar"):
        tasks.append(
            s2_service.search_papers(
                query=q,
                limit=limit,
                offset=offset,
                year_from=year_from,
                year_to=year_to,
                fields_of_study=field,
            )
        )
    else:
        tasks.append(_noop_s2())

    if source in ("all", "arxiv"):
        tasks.append(arxiv_service.search_papers(query=q, max_results=limit, start=offset))
    else:
        tasks.append(_noop_arxiv())

    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process Semantic Scholar results
        s2_data = results[0]
        if isinstance(s2_data, Exception):
            errors.append(f"Semantic Scholar: {s2_data}")
        elif isinstance(s2_data, dict):
            s2_results = s2_data.get("results", [])
            if s2_data.get("error"):
                errors.append(s2_data["error"])

        # Process arXiv results
        arxiv_data = results[1]
        if isinstance(arxiv_data, Exception):
            errors.append(f"arXiv: {arxiv_data}")
        elif isinstance(arxiv_data, list):
            arxiv_results = arxiv_data

    except Exception as e:
        logger.error(f"Search aggregation error: {e}")
        errors.append(str(e))

    # Merge and deduplicate
    merged = _merge_results(s2_results, arxiv_results)

    # Cache papers in DB
    for paper_data in merged[:50]:  # Cache up to 50 per search
        try:
            await _cache_paper(db, paper_data)
        except Exception as e:
            logger.warning(f"Failed to cache paper: {e}")

    # Save search history
    try:
        history = SearchHistory(
            user_id=current_user.id,
            query=q,
            filters={"source": source, "year_from": year_from, "year_to": year_to, "field": field},
            result_count=len(merged),
        )
        db.add(history)
    except Exception as e:
        logger.warning(f"Failed to save search history: {e}")

    # Add IDs from DB cache to results
    result_with_ids = []
    for i, paper in enumerate(merged):
        # Try to find the cached paper to get its DB id
        result_obj = await db.execute(
            select(Paper).where(
                Paper.external_id == paper["external_id"],
                Paper.source == paper["source"],
            )
        )
        cached = result_obj.scalar_one_or_none()
        paper_with_id = {**paper, "id": cached.id if cached else f"temp_{i}"}
        result_with_ids.append(paper_with_id)

    response = {
        "query": q,
        "results": result_with_ids,
        "total": len(merged),
        "sources": {
            "semantic_scholar": len(s2_results),
            "arxiv": len(arxiv_results),
        },
    }
    if errors:
        response["errors"] = errors

    return response


@router.get("/{paper_id}")
async def get_paper(
    paper_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get paper details - from DB cache or external API."""
    # Try DB cache first
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()

    if paper:
        return {
            "id": paper.id,
            "external_id": paper.external_id,
            "source": paper.source,
            "title": paper.title,
            "authors": paper.authors,
            "abstract": paper.abstract,
            "full_text": paper.full_text,
            "year": paper.year,
            "doi": paper.doi,
            "url": paper.url,
            "citation_count": paper.citation_count,
            "fields_of_study": paper.fields_of_study,
            "page_count": paper.page_count,
        }

    raise HTTPException(status_code=404, detail="Paper not found")


@router.get("/{paper_id}/related")
async def get_related_papers(
    paper_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get related papers via Semantic Scholar recommendations."""
    # Get the paper from DB
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    related = []

    # Use Semantic Scholar recommendations if paper is from S2
    if paper.source == "semantic_scholar":
        recommendations = await s2_service.get_recommendations(paper.external_id, limit=10)
        for rec in recommendations:
            cached = await _cache_paper(db, rec)
            related.append({**rec, "id": cached.id})

    # Fallback: use Groq keyword extraction + S2 search
    if not related and paper.abstract:
        from app.services import groq as groq_service
        keywords = await groq_service.extract_keywords(paper.abstract)
        if keywords:
            query = " ".join(keywords[:3]) if isinstance(keywords, list) else str(keywords)
            search_result = await s2_service.search_papers(query=query, limit=10)
            for rec in search_result.get("results", []):
                # Skip the paper itself
                if rec.get("external_id") == paper.external_id:
                    continue
                cached = await _cache_paper(db, rec)
                related.append({**rec, "id": cached.id})

    return {"paper_id": paper_id, "related": related}
