"""Semantic Scholar API wrapper."""

import httpx

from app.core.config import settings

BASE_URL = "https://api.semanticscholar.org/graph/v1"

HEADERS = {}


def get_headers() -> dict:
    if settings.SEMANTIC_SCHOLAR_API_KEY:
        return {"x-api-key": settings.SEMANTIC_SCHOLAR_API_KEY}
    return {}


async def search_papers(query: str, limit: int = 20, offset: int = 0, fields: str | None = None) -> dict:
    """Search papers on Semantic Scholar."""
    params = {
        "query": query,
        "limit": limit,
        "offset": offset,
        "fields": "title,authors,year,abstract,citationCount,externalIds,url,fieldsOfStudy",
    }
    if fields:
        params["fieldsOfStudy"] = fields

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{BASE_URL}/paper/search", params=params, headers=get_headers())
        resp.raise_for_status()
        return resp.json()


async def get_paper(paper_id: str) -> dict:
    """Get paper details by Semantic Scholar ID."""
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            f"{BASE_URL}/paper/{paper_id}",
            params={"fields": "title,authors,year,abstract,citationCount,externalIds,url,fieldsOfStudy"},
            headers=get_headers(),
        )
        resp.raise_for_status()
        return resp.json()
