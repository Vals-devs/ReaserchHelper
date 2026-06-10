"""Semantic Scholar API wrapper with rate limiting and error handling."""

import asyncio
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

BASE_URL = "https://api.semanticscholar.org/graph/v1"

# Rate limit: 1 request/second with API key
_last_request_time: float = 0.0
MIN_REQUEST_INTERVAL = 1.1  # seconds between requests


def get_headers() -> dict:
    if settings.SEMANTIC_SCHOLAR_API_KEY:
        return {"x-api-key": settings.SEMANTIC_SCHOLAR_API_KEY}
    return {}


async def _rate_limit():
    """Ensure at least MIN_REQUEST_INTERVAL between requests."""
    global _last_request_time
    import time
    now = time.monotonic()
    elapsed = now - _last_request_time
    if elapsed < MIN_REQUEST_INTERVAL:
        await asyncio.sleep(MIN_REQUEST_INTERVAL - elapsed)
    _last_request_time = time.monotonic()


def normalize_paper(raw: dict) -> dict:
    """Normalize a Semantic Scholar paper response to our common format."""
    authors = []
    for a in raw.get("authors", []):
        name = a.get("name", "")
        if name:
            authors.append(name)

    external_ids = raw.get("externalIds") or {}
    doi = external_ids.get("DOI") or raw.get("doi")

    return {
        "external_id": raw.get("paperId", ""),
        "source": "semantic_scholar",
        "title": raw.get("title", ""),
        "authors": authors,
        "abstract": raw.get("abstract"),
        "year": raw.get("year"),
        "doi": doi,
        "url": raw.get("url") or (f"https://doi.org/{doi}" if doi else None),
        "citation_count": raw.get("citationCount", 0),
        "fields_of_study": raw.get("fieldsOfStudy") or [],
    }


async def search_papers(
    query: str,
    limit: int = 20,
    offset: int = 0,
    year_from: int | None = None,
    year_to: int | None = None,
    fields_of_study: str | None = None,
) -> dict:
    """Search papers on Semantic Scholar.

    Returns: {"results": list[dict], "total": int}
    """
    await _rate_limit()

    params: dict = {
        "query": query,
        "limit": min(limit, 100),
        "offset": offset,
        "fields": "title,authors,year,abstract,citationCount,externalIds,url,fieldsOfStudy",
    }
    if year_from or year_to:
        yr = f"{year_from or ''}-{year_to or ''}"
        params["year"] = yr
    if fields_of_study:
        params["fieldsOfStudy"] = fields_of_study

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(
                f"{BASE_URL}/paper/search",
                params=params,
                headers=get_headers(),
            )
            resp.raise_for_status()
            data = resp.json()

        results = [normalize_paper(p) for p in data.get("data", [])]
        return {"results": results, "total": data.get("total", len(results))}

    except httpx.HTTPStatusError as e:
        logger.error(f"Semantic Scholar API error ({e.response.status_code}): {e.response.text[:200]}")
        return {"results": [], "total": 0, "error": f"Semantic Scholar error: {e.response.status_code}"}
    except Exception as e:
        logger.error(f"Semantic Scholar request failed: {e}")
        return {"results": [], "total": 0, "error": f"Semantic Scholar unavailable: {e}"}


async def get_paper(paper_id: str) -> dict | None:
    """Get paper details by Semantic Scholar paper ID."""
    await _rate_limit()

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{BASE_URL}/paper/{paper_id}",
                params={"fields": "title,authors,year,abstract,citationCount,externalIds,url,fieldsOfStudy,references,referenceCount"},
                headers=get_headers(),
            )
            resp.raise_for_status()
            return normalize_paper(resp.json())
    except Exception as e:
        logger.error(f"Semantic Scholar get_paper failed: {e}")
        return None


async def get_recommendations(paper_id: str, limit: int = 10) -> list[dict]:
    """Get paper recommendations based on a paper."""
    await _rate_limit()

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(
                f"{BASE_URL}/recommendations/v1/papers/forpaper/{paper_id}",
                params={"limit": limit, "fields": "title,authors,year,abstract,citationCount,externalIds,url,fieldsOfStudy"},
                headers=get_headers(),
            )
            resp.raise_for_status()
            data = resp.json()
        return [normalize_paper(p) for p in data.get("recommendedPapers", [])]
    except Exception as e:
        logger.error(f"Semantic Scholar recommendations failed: {e}")
        return []
