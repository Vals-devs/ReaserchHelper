"""arXiv API wrapper."""

import logging

import httpx
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

BASE_URL = "https://export.arxiv.org/api/query"

ATOM_NS = "{http://www.w3.org/2005/Atom}"
ARXIV_NS = "{http://arxiv.org/schemas/atom}"


def parse_entry(entry: ET.Element) -> dict:
    """Parse a single arXiv API entry into a dict."""
    title = entry.findtext(f"{ATOM_NS}title", "").strip().replace("\n", " ")
    summary = entry.findtext(f"{ATOM_NS}summary", "").strip().replace("\n", " ")
    authors = [a.findtext(f"{ATOM_NS}name", "") for a in entry.findall(f"{ATOM_NS}author")]
    published = entry.findtext(f"{ATOM_NS}published", "")
    arxiv_id = entry.findtext(f"{ATOM_NS}id", "").split("/abs/")[-1]
    doi = entry.findtext(f"{ARXIV_NS}doi", "")
    categories = [c.get("term", "") for c in entry.findall(f"{ATOM_NS}category")]

    return {
        "external_id": arxiv_id,
        "source": "arxiv",
        "title": title,
        "authors": authors,
        "abstract": summary,
        "year": int(published[:4]) if published else None,
        "doi": doi or None,
        "url": f"https://arxiv.org/abs/{arxiv_id}",
        "fields_of_study": categories,
        "citation_count": 0,
    }


async def search_papers(query: str, max_results: int = 20, start: int = 0) -> list[dict]:
    """Search arXiv for papers."""
    params = {
        "search_query": f"all:{query}",
        "start": start,
        "max_results": max_results,
        "sortBy": "relevance",
    }
    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            resp = await client.get(BASE_URL, params=params)
            resp.raise_for_status()

        root = ET.fromstring(resp.text)
        entries = root.findall(f"{ATOM_NS}entry")
        return [parse_entry(e) for e in entries]
    except Exception as e:
        logger.error(f"arXiv search failed: {e}")
        return []
