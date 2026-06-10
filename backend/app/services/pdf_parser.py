"""PDF text extraction using PyMuPDF."""

import fitz  # PyMuPDF


def extract_text_from_pdf(file_bytes: bytes) -> dict:
    """Extract text from a PDF file.

    Returns:
        {
            "full_text": str,      # All text concatenated
            "page_count": int,     # Number of pages
            "title_hint": str,     # Best guess at title from first page
            "pages": list[str],    # Text per page
        }
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages = []
    for page in doc:
        text = page.get_text("text").strip()
        if text:
            pages.append(text)

    full_text = "\n\n".join(pages)
    page_count = len(doc)

    # Try to extract title from first page (first non-empty line that looks like a title)
    title_hint = ""
    if pages:
        first_page_lines = [
            line.strip()
            for line in pages[0].split("\n")
            if line.strip() and len(line.strip()) > 5
        ]
        # Title is usually one of the first few lines, often the longest
        candidates = first_page_lines[:5]
        if candidates:
            title_hint = max(candidates, key=len)

    doc.close()

    return {
        "full_text": full_text,
        "page_count": page_count,
        "title_hint": title_hint,
        "pages": pages,
    }
