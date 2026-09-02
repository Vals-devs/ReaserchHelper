"""Paper search router - aggregate results from Semantic Scholar + arXiv."""

import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, async_session_factory
from app.core.security import get_current_user
from app.models.user import User
from app.models.paper import Paper
from app.models.search_history import SearchHistory
from app.services import semantic_scholar as s2_service
from app.services import arxiv as arxiv_service
from app.services import openalex as openalex_service

logger = logging.getLogger(__name__)

router = APIRouter()


async def _noop_s2():
    return {"results": [], "total": 0}


async def _noop_arxiv():
    return []


async def _noop_openalex():
    return []


async def _bg_cache_search_results(user_id: str, q: str, filters: dict, papers: list[dict]):
    """Bulk cache search results and save search history in the background."""
    ext_ids = [p["external_id"] for p in papers if p.get("external_id")]
    if not ext_ids:
        return

    try:
        async with async_session_factory() as db:
            result = await db.execute(select(Paper.external_id).where(Paper.external_id.in_(ext_ids)))
            existing_ids = set(result.scalars().all())

            new_papers = []
            for p in papers:
                if p.get("external_id") not in existing_ids:
                    existing_ids.add(p["external_id"])
                    new_papers.append(
                        Paper(
                            external_id=p["external_id"],
                            source=p["source"],
                            title=p["title"],
                            authors=p.get("authors", []),
                            abstract=p.get("abstract"),
                            year=p.get("year"),
                            doi=p.get("doi"),
                            url=p.get("url"),
                            citation_count=p.get("citation_count", 0),
                            fields_of_study=p.get("fields_of_study", []),
                            journal=p.get("journal"),
                            accreditation=p.get("accreditation"),
                        )
                    )

            if new_papers:
                db.add_all(new_papers)

            # Save search history
            history = SearchHistory(
                user_id=user_id,
                query=q,
                filters=filters,
                result_count=len(papers),
            )
            db.add(history)
            await db.commit()
    except Exception as e:
        logger.warning(f"Background caching failed: {e}")


def _merge_results(s2_results: list[dict], openalex_results: list[dict], arxiv_results: list[dict]) -> list[dict]:
    """Merge and deduplicate results from Semantic Scholar, OpenAlex, and arXiv."""
    seen_doi: set[str] = set()
    seen_titles: set[str] = set()
    merged: list[dict] = []

    for source_list in [s2_results, openalex_results, arxiv_results]:
        for paper in source_list:
            title_key = paper.get("title", "").lower().strip()[:80]
            if not title_key:
                continue
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
        journal=paper_data.get("journal"),
        accreditation=paper_data.get("accreditation"),
    )
    db.add(paper)
    await db.flush()
    return paper


@router.get("/search")
async def search_papers(
    background_tasks: BackgroundTasks,
    q: str = Query(..., min_length=1, description="Search query"),
    source: str = Query("all", description="Source: all, semantic_scholar, openalex, arxiv"),
    year_from: int | None = Query(None, description="Filter: year from"),
    year_to: int | None = Query(None, description="Filter: year to"),
    field: str | None = Query(None, description="Filter: field of study"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search papers from Semantic Scholar, OpenAlex, and arXiv concurrently."""
    try:
        errors: list[str] = []
        s2_results: list[dict] = []
        openalex_results: list[dict] = []
        arxiv_results: list[dict] = []

        # Fetch from all sources concurrently
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

        if source in ("all", "openalex"):
            tasks.append(openalex_service.search_papers(query=q, limit=limit))
        else:
            tasks.append(_noop_openalex())

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

            # Process OpenAlex results
            oa_data = results[1]
            if isinstance(oa_data, Exception):
                errors.append(f"OpenAlex: {oa_data}")
            elif isinstance(oa_data, list):
                openalex_results = oa_data

            # Process arXiv results
            arxiv_data = results[2]
            if isinstance(arxiv_data, Exception):
                errors.append(f"arXiv: {arxiv_data}")
            elif isinstance(arxiv_data, list):
                arxiv_results = arxiv_data

        except Exception as e:
            logger.error(f"Search aggregation error: {e}")
            errors.append(str(e))

        # Merge and deduplicate
        merged = _merge_results(s2_results, openalex_results, arxiv_results)

        # Assign external_id as default ID instantly
        result_with_ids = [{**p, "id": p["external_id"]} for p in merged]

        # Enqueue background caching & history saving without blocking HTTP response
        filters = {"source": source, "year_from": year_from, "year_to": year_to, "field": field}
        background_tasks.add_task(_bg_cache_search_results, current_user.id, q, filters, merged[:50])

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

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Paper search endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/{paper_id}")
async def get_paper(
    paper_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get paper details - from DB cache, by external ID, or via external API fallback."""
    import uuid

    # 1. Try DB lookup by UUID primary key
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()

    # 2. If not found by primary key, try DB lookup by external_id
    if not paper:
        result = await db.execute(select(Paper).where(Paper.external_id == paper_id))
        paper = result.scalar_one_or_none()

    # 3. If still not found in DB, fetch from Semantic Scholar API
    if not paper and not paper_id.startswith("temp_"):
        external_paper = await s2_service.get_paper(paper_id)
        if external_paper:
            try:
                paper = await _cache_paper(db, external_paper)
            except Exception as e:
                logger.warning(f"Failed to cache fetched paper {paper_id}: {e}")
                # Transient fallback paper object
                paper = Paper(
                    id=str(uuid.uuid4()),
                    external_id=external_paper["external_id"],
                    source=external_paper["source"],
                    title=external_paper["title"],
                    authors=external_paper.get("authors", []),
                    abstract=external_paper.get("abstract"),
                    year=external_paper.get("year"),
                    doi=external_paper.get("doi"),
                    url=external_paper.get("url"),
                    citation_count=external_paper.get("citation_count", 0),
                    fields_of_study=external_paper.get("fields_of_study", []),
                    journal=external_paper.get("journal"),
                    accreditation=external_paper.get("accreditation"),
                )

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
            "journal": paper.journal,
            "accreditation": paper.accreditation,
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

    # Fallback: use Gemini keyword extraction + S2 search
    if not related and paper.abstract:
        from app.services import gemini as ai_service
        keywords = await ai_service.extract_keywords(paper.abstract)
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
