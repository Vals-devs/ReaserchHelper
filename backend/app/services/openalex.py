"""OpenAlex API wrapper for rich academic paper retrieval (Scopus/ISI indexed journals)."""

import asyncio
import logging
import httpx

from app.services.semantic_scholar import infer_accreditation

logger = logging.getLogger(__name__)

BASE_URL = "https://api.openalex.org/works"


def normalize_openalex_paper(raw: dict) -> dict:
    """Normalize an OpenAlex paper response to common paper format."""
    # Authors
    authors = []
    for memb in raw.get("authorships", []):
        author_obj = memb.get("author") or {}
        name = author_obj.get("display_name")
        if name:
            authors.append(name)

    # Year
    year = raw.get("publication_year")

    # DOI
    doi_raw = raw.get("doi") or ""
    doi = doi_raw.replace("https://doi.org/", "").strip() if doi_raw else None

    # URL
    url = raw.get("landing_page_url") or raw.get("doi") or (f"https://doi.org/{doi}" if doi else None)

    # Citation count
    citation_count = raw.get("cited_by_count", 0)

    # Abstract reconstruction from inverted index if present
    abstract = None
    inv_abstract = raw.get("abstract_inverted_index")
    if inv_abstract and isinstance(inv_abstract, dict):
        try:
            word_pos = []
            for word, positions in inv_abstract.items():
                for pos in positions:
                    word_pos.append((pos, word))
            word_pos.sort(key=lambda x: x[0])
            abstract = " ".join([w[1] for w in word_pos])
            if len(abstract) > 2000:
                abstract = abstract[:2000] + "..."
        except Exception:
            abstract = None

    # Venue & Journal
    primary_location = raw.get("primary_location") or {}
    source_obj = primary_location.get("source") or {}
    venue_name = source_obj.get("display_name") or ""

    # Concepts / Fields of study
    concepts = []
    for c in raw.get("concepts", []):
        c_name = c.get("display_name")
        if c_name:
            concepts.append(c_name)

    journal_name, accreditation = infer_accreditation(venue_name, venue_name, citation_count, doi)

    openalex_id = raw.get("id", "").split("/")[-1]

    return {
        "external_id": f"openalex_{openalex_id}",
        "source": "openalex",
        "title": raw.get("title") or "Untitled Paper",
        "authors": authors,
        "abstract": abstract,
        "year": year,
        "doi": doi,
        "url": url,
        "citation_count": citation_count,
        "fields_of_study": concepts[:5],
        "journal": journal_name,
        "accreditation": accreditation,
    }


async def search_papers(query: str, limit: int = 20) -> list[dict]:
    """Search OpenAlex for top academic journal papers."""
    params = {
        "search": query,
        "per-page": min(limit, 50),
        "sort": "cited_by_count:desc",
    }
    headers = {
        "User-Agent": "ResearchFinder/1.0 (mailto:researchfinder@example.com)"
    }
    try:
        async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
            resp = await client.get(BASE_URL, params=params, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        results = [normalize_openalex_paper(w) for w in data.get("results", [])]
        return results
    except Exception as e:
        logger.warning(f"OpenAlex search failed: {e}")
        return []
