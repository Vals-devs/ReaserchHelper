"""Bibliography formatting service."""


def format_apa(paper: dict) -> str:
    """Format a paper in APA style."""
    authors = paper.get("authors", [])
    author_str = ", ".join(authors[:6])
    if len(authors) > 6:
        author_str += ", ... " + authors[-1]
    year = paper.get("year", "n.d.")
    title = paper.get("title", "")
    doi = paper.get("doi", "")
    doi_str = f" https://doi.org/{doi}" if doi else ""
    return f"{author_str} ({year}). {title}.{doi_str}"


def format_ieee(paper: dict) -> str:
    """Format a paper in IEEE style."""
    authors = paper.get("authors", [])
    author_str = ", ".join(authors[:3])
    if len(authors) > 3:
        author_str += " et al."
    year = paper.get("year", "n.d.")
    title = paper.get("title", "")
    doi = paper.get("doi", "")
    doi_str = f", doi: {doi}" if doi else ""
    return f'{author_str}, "{title}," {year}{doi_str}.'


def format_chicago(paper: dict) -> str:
    """Format a paper in Chicago style."""
    authors = paper.get("authors", [])
    author_str = ", ".join(authors[:3])
    if len(authors) > 3:
        author_str += " et al."
    year = paper.get("year", "n.d.")
    title = paper.get("title", "")
    doi = paper.get("doi", "")
    doi_str = f" https://doi.org/{doi}" if doi else ""
    return f'{author_str}. "{title}." {year}.{doi_str}'


FORMATTERS = {
    "APA": format_apa,
    "IEEE": format_ieee,
    "Chicago": format_chicago,
}


def generate_bibliography(papers: list[dict], format: str = "APA") -> list[str]:
    """Generate bibliography entries for a list of papers."""
    formatter = FORMATTERS.get(format, format_apa)
    return [formatter(p) for p in papers]
