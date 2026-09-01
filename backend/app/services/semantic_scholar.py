"""Semantic Scholar API wrapper with rate limiting and error handling."""

import asyncio
import logging
import time

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

BASE_URL = "https://api.semanticscholar.org/graph/v1"

# Rate limit: 1 request/second with API key
_last_request_time: float = 0.0
MIN_REQUEST_INTERVAL = 1.1  # seconds between requests
_rate_limit_lock = None


class SimpleTTLCache:
    """A simple in-memory TTL cache to store Semantic Scholar responses."""
    def __init__(self, ttl: int = 300):
        self.ttl = ttl
        self._cache = {}

    def get(self, key):
        if key in self._cache:
            val, expiry = self._cache[key]
            if time.time() < expiry:
                return val
            else:
                del self._cache[key]
        return None

    def set(self, key, value):
        self._cache[key] = (value, time.time() + self.ttl)


_search_cache = SimpleTTLCache(ttl=300)      # 5 minutes cache for searches
_paper_cache = SimpleTTLCache(ttl=600)       # 10 minutes cache for paper details
_recommendation_cache = SimpleTTLCache(ttl=600) # 10 minutes cache for recommendations


def get_headers() -> dict:
    if settings.SEMANTIC_SCHOLAR_API_KEY:
        return {"x-api-key": settings.SEMANTIC_SCHOLAR_API_KEY}
    return {}


async def _rate_limit():
    """Ensure at least MIN_REQUEST_INTERVAL between requests, using a lock to serialize concurrent queries."""
    global _last_request_time, _rate_limit_lock
    if _rate_limit_lock is None:
        _rate_limit_lock = asyncio.Lock()

    async with _rate_limit_lock:
        now = time.monotonic()
        elapsed = now - _last_request_time
        if elapsed < MIN_REQUEST_INTERVAL:
            await asyncio.sleep(MIN_REQUEST_INTERVAL - elapsed)
        _last_request_time = time.monotonic()


def infer_accreditation(journal_raw: str | None, venue_raw: str | None, citation_count: int = 0, doi: str | None = None) -> tuple[str, str]:
    """Infer journal/venue name and accreditation badge (Scopus Q1-Q4, Sinta 1-6, etc.)."""
    journal_name = (journal_raw or venue_raw or "").strip()
    if not journal_name:
        if citation_count >= 50:
            return ("Scopus Journal", "Scopus Q1")
        elif citation_count >= 15:
            return ("Scopus Journal", "Scopus Q2")
        return ("Academic Publication", "Scopus Indexed")

    lower_name = journal_name.lower()

    # 1. Indonesian Sinta Journal Detection
    is_indonesian = any(term in lower_name for term in [
        "jurnal", "indonesian journal", "ijain", "telkomnika", "iaes",
        "register", "juita", "sisforma", "joiv", "kinetik", "mia", "jsin",
        "juti", "tekno", "inomatika", "reksiana", "matrik", "kumpul"
    ]) or (doi and ".id" in doi.lower())

    if is_indonesian:
        if any(top in lower_name for top in ["telkomnika", "joiv", "ijain", "iaes", "jurnal ilmu komputer"]):
            return (journal_name, "Sinta 1")
        elif citation_count >= 20 or any(mid in lower_name for mid in ["register", "kinetik", "juita"]):
            return (journal_name, "Sinta 2")
        elif citation_count >= 8:
            return (journal_name, "Sinta 3")
        else:
            return (journal_name, "Sinta 4")

    # 2. High-Impact Scopus Q1 Detection
    q1_terms = [
        "ieee transactions", "acm computing surveys", "nature", "science", "cell", "lancet",
        "pattern analysis", "neurips", "icml", "cvpr", "kdd", "acl", "aaai",
        "ieee journal", "ieee communications", "nucleic acids", "information sciences",
        "knowledge-based systems", "expert systems with applications", "future generation computer systems"
    ]
    if any(term in lower_name for term in q1_terms) or citation_count >= 50:
        return (journal_name, "Scopus Q1")

    # 3. Scopus Q2 Detection
    q2_terms = [
        "journal of", "transactions on", "ieee", "acm", "springer", "elsevier",
        "mdpi", "wiley", "plos", "expert systems", "applied sciences", "sensors",
        "neurocomputing", "computers &", "computer networks"
    ]
    if citation_count >= 20 or any(term in lower_name for term in q2_terms):
        return (journal_name, "Scopus Q2")

    # 4. Scopus Q3 / Q4 Detection
    if citation_count >= 5:
        return (journal_name, "Scopus Q3")

    return (journal_name, "Scopus Q4")


def normalize_paper(raw: dict) -> dict:
    """Normalize a Semantic Scholar paper response to our common format."""
    authors = []
    for a in raw.get("authors", []):
        name = a.get("name", "")
        if name:
            authors.append(name)

    external_ids = raw.get("externalIds") or {}
    doi = external_ids.get("DOI") or raw.get("doi")

    venue_info = raw.get("venue") or ""
    pub_venue = raw.get("publicationVenue") or {}
    journal_info = raw.get("journal") or {}
    journal_str = pub_venue.get("name") or (journal_info.get("name") if isinstance(journal_info, dict) else str(journal_info)) or venue_info

    citation_count = raw.get("citationCount", 0)
    journal_name, accreditation = infer_accreditation(journal_str, venue_info, citation_count, doi)

    return {
        "external_id": raw.get("paperId", ""),
        "source": "semantic_scholar",
        "title": raw.get("title", ""),
        "authors": authors,
        "abstract": raw.get("abstract"),
        "year": raw.get("year"),
        "doi": doi,
        "url": raw.get("url") or (f"https://doi.org/{doi}" if doi else None),
        "citation_count": citation_count,
        "fields_of_study": raw.get("fieldsOfStudy") or [],
        "journal": journal_name,
        "accreditation": accreditation,
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
    # Check cache first
    cache_key = f"{query}:{limit}:{offset}:{year_from}:{year_to}:{fields_of_study}"
    cached = _search_cache.get(cache_key)
    if cached is not None:
        logger.info(f"Returning cached Semantic Scholar search for query: {query}")
        return cached

    params: dict = {
        "query": query,
        "limit": min(limit, 100),
        "offset": offset,
        "fields": "title,authors,year,abstract,citationCount,externalIds,url,fieldsOfStudy,venue,publicationVenue,journal",
    }
    if year_from or year_to:
        yr = f"{year_from or ''}-{year_to or ''}"
        params["year"] = yr
    if fields_of_study:
        params["fieldsOfStudy"] = fields_of_study

    max_retries = 2
    for attempt in range(max_retries + 1):
        await _rate_limit()
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                resp = await client.get(
                    f"{BASE_URL}/paper/search",
                    params=params,
                    headers=get_headers(),
                )
                if resp.status_code == 429 and attempt < max_retries:
                    logger.warning(f"Semantic Scholar search returned 429. Retrying in 2 seconds (attempt {attempt + 1}/{max_retries})...")
                    await asyncio.sleep(2.0)
                    continue
                resp.raise_for_status()
                data = resp.json()

            results = [normalize_paper(p) for p in data.get("data", [])]
            response_data = {"results": results, "total": data.get("total", len(results))}
            _search_cache.set(cache_key, response_data)
            return response_data

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429 and attempt < max_retries:
                logger.warning(f"Semantic Scholar search HTTP status error 429. Retrying in 2 seconds (attempt {attempt + 1}/{max_retries})...")
                await asyncio.sleep(2.0)
                continue
            logger.error(f"Semantic Scholar API error ({e.response.status_code}): {e.response.text[:200]}")
            if e.response.status_code == 429:
                return {
                    "results": [],
                    "total": 0,
                    "error": "Batas permintaan (rate limit) Semantic Scholar terlampaui. Menampilkan hasil pencarian dari arXiv sebagai cadangan."
                }
            return {"results": [], "total": 0, "error": f"Semantic Scholar error: {e.response.status_code}"}
        except Exception as e:
            if attempt < max_retries:
                logger.warning(f"Semantic Scholar search request failed: {e}. Retrying in 2 seconds...")
                await asyncio.sleep(2.0)
                continue
            logger.error(f"Semantic Scholar request failed: {e}")
            return {"results": [], "total": 0, "error": f"Semantic Scholar unavailable: {e}"}


async def get_paper(paper_id: str) -> dict | None:
    """Get paper details by Semantic Scholar paper ID."""
    cached = _paper_cache.get(paper_id)
    if cached is not None:
        return cached

    max_retries = 2
    for attempt in range(max_retries + 1):
        await _rate_limit()
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    f"{BASE_URL}/paper/{paper_id}",
                    params={"fields": "title,authors,year,abstract,citationCount,externalIds,url,fieldsOfStudy,venue,publicationVenue,journal,references,referenceCount"},
                    headers=get_headers(),
                )
                if resp.status_code == 429 and attempt < max_retries:
                    logger.warning(f"Semantic Scholar get_paper returned 429. Retrying in 2 seconds (attempt {attempt + 1}/{max_retries})...")
                    await asyncio.sleep(2.0)
                    continue
                resp.raise_for_status()
                data = normalize_paper(resp.json())
                _paper_cache.set(paper_id, data)
                return data
        except Exception as e:
            if attempt < max_retries:
                logger.warning(f"Semantic Scholar get_paper failed: {e}. Retrying in 2 seconds...")
                await asyncio.sleep(2.0)
                continue
            logger.error(f"Semantic Scholar get_paper failed: {e}")
            return None


async def get_recommendations(paper_id: str, limit: int = 10) -> list[dict]:
    """Get paper recommendations based on a paper."""
    cache_key = f"{paper_id}:{limit}"
    cached = _recommendation_cache.get(cache_key)
    if cached is not None:
        return cached

    max_retries = 2
    for attempt in range(max_retries + 1):
        await _rate_limit()
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                resp = await client.get(
                    f"{BASE_URL}/recommendations/v1/papers/forpaper/{paper_id}",
                    params={"limit": limit, "fields": "title,authors,year,abstract,citationCount,externalIds,url,fieldsOfStudy"},
                    headers=get_headers(),
                )
                if resp.status_code == 429 and attempt < max_retries:
                    logger.warning(f"Semantic Scholar recommendations returned 429. Retrying in 2 seconds (attempt {attempt + 1}/{max_retries})...")
                    await asyncio.sleep(2.0)
                    continue
                resp.raise_for_status()
                data = resp.json()
                results = [normalize_paper(p) for p in data.get("recommendedPapers", [])]
                _recommendation_cache.set(cache_key, results)
                return results
        except Exception as e:
            if attempt < max_retries:
                logger.warning(f"Semantic Scholar recommendations failed: {e}. Retrying in 2 seconds...")
                await asyncio.sleep(2.0)
                continue
            logger.error(f"Semantic Scholar recommendations failed: {e}")
            return []

