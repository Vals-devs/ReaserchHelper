"""Groq API wrapper for AI features."""

import json
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

BASE_URL = "https://api.groq.com/openai/v1/chat/completions"

MODEL_DEFAULT = "llama-3.1-8b-instant"
MODEL_LONG = "llama-3.3-70b-versatile"

# Max chars per paper text to fit in Groq context window (~8k tokens)
MAX_CHARS_PER_PAPER = 2500
MAX_TOTAL_CHARS = 12000


def _parse_json_response(text: str) -> dict | list | str:
    """Try to parse JSON from AI response, handling markdown code blocks."""
    # Strip markdown code fences
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # Remove first and last line (``` markers)
        lines = [l for l in lines[1:] if not l.strip().startswith("```")]
        cleaned = "\n".join(lines).strip()
    try:
        return json.loads(cleaned)
    except (json.JSONDecodeError, ValueError):
        return text


async def chat_completion(
    messages: list[dict],
    model: str = MODEL_DEFAULT,
    temperature: float = 0.3,
    max_tokens: int = 2048,
) -> str:
    """Send a chat completion request to Groq API."""
    if not settings.GROQ_API_KEY:
        return "[Groq API key not configured]"

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        try:
            resp = await client.post(
                BASE_URL,
                json=payload,
                headers={
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            error_body = e.response.text[:300] if e.response else "unknown"
            logger.error(f"Groq API error ({e.response.status_code}): {error_body}")
            return f"[Groq API error: {e.response.status_code}]"
        except Exception as e:
            logger.error(f"Groq request failed: {e}")
            return f"[Groq request failed: {e}]"


async def summarize_paper(title: str, abstract: str) -> dict:
    """Generate a paper summary in Bahasa Indonesia."""
    prompt = f"""Ringkas paper ilmiah berikut dalam bahasa Indonesia.
Berikan output dalam format JSON dengan kunci:
- "ringkasan": ringkasan 3-5 kalimat
- "temuan_utama": array 3-5 poin temuan utama
- "metodologi": deskripsi singkat metodologi yang digunakan

Judul: {title}
Abstrak: {abstract}

Output JSON:"""

    result = await chat_completion(
        [{"role": "user", "content": prompt}],
        model=MODEL_DEFAULT,
    )
    parsed = _parse_json_response(result)
    if isinstance(parsed, dict):
        return parsed
    return {"ringkasan": result, "temuan_utama": [], "metodologi": ""}


async def explain_text(text: str, language: str = "id") -> str:
    """Explain text in plain language."""
    lang_instruction = "bahasa Indonesia yang sederhana" if language == "id" else "simple English"
    prompt = f"""Jelaskan teks akademis berikut dalam {lang_instruction}, seperti menjelaskan ke teman yang bukan ahli:

{text}

Penjelasan:"""

    return await chat_completion(
        [{"role": "user", "content": prompt}],
        model=MODEL_DEFAULT,
    )


async def extract_paper_metadata(full_text: str, title_hint: str = "") -> dict:
    """Extract structured metadata from raw PDF text using AI.

    Returns: {"title": str, "authors": list[str], "year": int|None, "abstract": str}
    """
    # Truncate text to fit in context
    text_sample = full_text[:4000]

    prompt = f"""Ekstrak metadata dari paper ilmiah berikut. Berikan output HANYA dalam format JSON (tanpa markdown) dengan kunci:
- "title": judul paper (string)
- "authors": daftar nama author (array of strings)
- "year": tahun publikasi (integer, atau null jika tidak ditemukan)
- "abstract": abstrak atau ringkasan paper (string, 3-5 kalimat)

Jika judul tidak jelas, gunakan title hint berikut sebagai referensi: "{title_hint}"

Teks paper (bagian awal):
---
{text_sample}
---

Output JSON:"""

    result = await chat_completion(
        [{"role": "user", "content": prompt}],
        model=MODEL_DEFAULT,
        temperature=0.1,
    )
    parsed = _parse_json_response(result)
    if isinstance(parsed, dict):
        return {
            "title": parsed.get("title", title_hint or "Untitled Paper"),
            "authors": parsed.get("authors", []),
            "year": parsed.get("year"),
            "abstract": parsed.get("abstract", ""),
        }
    # Fallback
    return {
        "title": title_hint or "Untitled Paper",
        "authors": [],
        "year": None,
        "abstract": "",
    }


async def gap_analysis(papers: list[dict]) -> dict:
    """Analyze research gaps across multiple papers.

    Each paper dict should have: title, abstract or full_text.
    """
    papers_text_parts = []
    for i, p in enumerate(papers):
        # Prefer full_text over abstract for richer analysis
        content = p.get("full_text") or p.get("abstract", "N/A")
        if len(content) > MAX_CHARS_PER_PAPER:
            content = content[:MAX_CHARS_PER_PAPER] + "... [truncated]"
        papers_text_parts.append(
            f"=== Paper {i+1}: {p['title']} ===\n{content}"
        )

    papers_text = "\n\n".join(papers_text_parts)

    # If total text is too long, fall back to abstracts only
    if len(papers_text) > MAX_TOTAL_CHARS:
        logger.info(f"Gap analysis prompt too long ({len(papers_text)} chars), falling back to abstracts")
        papers_text_parts = []
        for i, p in enumerate(papers):
            abstract = p.get("abstract", "N/A") or "N/A"
            if len(abstract) > 800:
                abstract = abstract[:800] + "..."
            papers_text_parts.append(
                f"=== Paper {i+1}: {p['title']} ===\n{abstract}"
            )
        papers_text = "\n\n".join(papers_text_parts)

    prompt = f"""Kamu adalah seorang profesor dan peneliti berpengalaman. Analisis paper-paper berikut dan identifikasi research gap.

{papers_text}

Berikan analisis mendalam dalam format JSON (tanpa markdown) dengan struktur:
{{
  "topik_dominan": [
    {{"name": "nama topik", "count": jumlah paper yang membahas, "desc": "deskripsi singkat"}}
  ],
  "metodologi": [
    {{"name": "nama metode", "freq": "Sering/Sedang/Jarang", "desc": "deskripsi"}}
  ],
  "celah_penelitian": [
    {{"title": "judul celah", "desc": "penjelasan detail", "priority": "Tinggi/Sedang"}}
  ],
  "saran_topik": [
    "saran topik riset lanjutan 1",
    "saran topik riset lanjutan 2"
  ]
}}

Output JSON:"""

    result = await chat_completion(
        [{"role": "user", "content": prompt}],
        model=MODEL_LONG,
        max_tokens=2048,
        temperature=0.4,
    )
    parsed = _parse_json_response(result)
    if isinstance(parsed, dict):
        return parsed
    return {
        "topik_dominan": [],
        "metodologi": [],
        "celah_penelitian": [],
        "saran_topik": [],
        "raw_response": result,
    }


async def extract_keywords(abstract: str) -> list[str]:
    """Extract key search terms from an abstract."""
    prompt = f"""Ekstrak 5-8 keyword penting dari abstrak berikut untuk digunakan sebagai query pencarian paper terkait.
Berikan output sebagai array JSON string.

Abstrak: {abstract}

Output JSON array:"""

    result = await chat_completion(
        [{"role": "user", "content": prompt}],
        model=MODEL_DEFAULT,
        max_tokens=256,
    )
    parsed = _parse_json_response(result)
    if isinstance(parsed, list):
        return [str(k) for k in parsed]
    return [result]
