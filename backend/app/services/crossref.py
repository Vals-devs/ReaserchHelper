"""CrossRef API wrapper."""

import httpx

BASE_URL = "https://api.crossref.org/works"


async def get_by_doi(doi: str) -> dict | None:
    """Fetch paper metadata from CrossRef by DOI."""
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{BASE_URL}/{doi}")
        if resp.status_code != 200:
            return None
        data = resp.json().get("message", {})

    authors = []
    for a in data.get("author", []):
        name = f"{a.get('given', '')} {a.get('family', '')}".strip()
        if name:
            authors.append(name)

    year = None
    date_parts = data.get("published-print", data.get("published-online", {})).get("date-parts", [[]])
    if date_parts and date_parts[0]:
        year = date_parts[0][0]

    return {
        "title": data.get("title", [""])[0] if data.get("title") else "",
        "authors": authors,
        "year": year,
        "doi": data.get("DOI"),
        "url": data.get("URL"),
        "abstract": data.get("abstract", ""),
        "citation_count": data.get("is-referenced-by-count", 0),
    }
