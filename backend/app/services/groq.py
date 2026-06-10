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
    """Try to parse JSON from AI response, handling markdown code blocks and extra text."""
    if not text or not text.strip():
        return text

    cleaned = text.strip()

    # 1. Try direct parse first
    try:
        return json.loads(cleaned)
    except (json.JSONDecodeError, ValueError):
        pass

    # 2. Strip markdown code fences (```json ... ``` or ``` ... ```)
    import re
    fence_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?\s*```', cleaned, re.DOTALL)
    if fence_match:
        try:
            return json.loads(fence_match.group(1).strip())
        except (json.JSONDecodeError, ValueError):
            pass

    # 3. Find first { and last } to extract JSON object
    first_brace = cleaned.find('{')
    last_brace = cleaned.rfind('}')
    if first_brace != -1 and last_brace > first_brace:
        try:
            return json.loads(cleaned[first_brace:last_brace + 1])
        except (json.JSONDecodeError, ValueError):
            pass

    # 4. Find first [ and last ] to extract JSON array
    first_bracket = cleaned.find('[')
    last_bracket = cleaned.rfind(']')
    if first_bracket != -1 and last_bracket > first_bracket:
        try:
            return json.loads(cleaned[first_bracket:last_bracket + 1])
        except (json.JSONDecodeError, ValueError):
            pass

    return text


async def chat_completion(
    messages: list[dict],
    model: str = MODEL_DEFAULT,
    temperature: float = 0.3,
    max_tokens: int = 2048,
) -> str:
    """Send a chat completion request to Groq API with automatic retries for rate limits."""
    import asyncio
    if not settings.GROQ_API_KEY:
        return "[Groq API key not configured]"

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    BASE_URL,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                        "Content-Type": "application/json",
                    },
                )
                if resp.status_code == 429 and attempt < max_retries:
                    wait_time = (attempt + 1) * 3.0
                    logger.warning(f"Groq API returned 429. Retrying in {wait_time} seconds (attempt {attempt + 1}/{max_retries})...")
                    await asyncio.sleep(wait_time)
                    continue
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429 and attempt < max_retries:
                wait_time = (attempt + 1) * 3.0
                logger.warning(f"Groq API HTTPStatusError 429. Retrying in {wait_time} seconds (attempt {attempt + 1}/{max_retries})...")
                await asyncio.sleep(wait_time)
                continue
            error_body = e.response.text[:300] if e.response else "unknown"
            logger.error(f"Groq API error ({e.response.status_code}): {error_body}")
            return f"[Groq API error: {e.response.status_code}]"
        except Exception as e:
            if attempt < max_retries:
                wait_time = (attempt + 1) * 3.0
                logger.warning(f"Groq request failed: {e}. Retrying in {wait_time} seconds (attempt {attempt + 1}/{max_retries})...")
                await asyncio.sleep(wait_time)
                continue
            logger.error(f"Groq request failed: {e}")
            return f"[Groq request failed: {e}]"


async def summarize_paper(title: str, abstract: str) -> dict:
    """Generate a paper summary in Bahasa Indonesia."""
    system_prompt = """Kamu adalah asisten peneliti yang meringkas paper ilmiah dalam bahasa Indonesia.
Selalu berikan output HANYA dalam format JSON valid (tanpa markdown, tanpa teks tambahan) dengan struktur:
{"ringkasan": "ringkasan 3-5 kalimat", "temuan_utama": ["poin 1", "poin 2", "poin 3"], "metodologi": "deskripsi singkat metodologi"}"""

    user_prompt = f"""Ringkas paper berikut:

Judul: {title}
Abstrak: {abstract}

Berikan HANYA JSON:"""

    result = await chat_completion(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        model=MODEL_DEFAULT,
        temperature=0.2,
    )
    parsed = _parse_json_response(result)
    if isinstance(parsed, dict):
        return {
            "ringkasan": parsed.get("ringkasan", ""),
            "temuan_utama": parsed.get("temuan_utama", []),
            "metodologi": parsed.get("metodologi", ""),
        }
    # Fallback: return raw text as ringkasan
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


async def translate_text(text: str, target_language: str = "id") -> str:
    """Translate text to target language (default: Indonesian)."""
    if target_language == "id":
        lang_name = "bahasa Indonesia yang formal dan akademis"
    else:
        lang_name = "English (academic and formal)"

    prompt = f"""Terjemahkan teks akademis berikut ke {lang_name}. 
Pertahankan istilah teknis dalam tanda kurung jika perlu.
Berikan HANYA terjemahan tanpa penjelasan tambahan.

Teks asli:
{text}

Terjemahan:"""

    return await chat_completion(
        [
            {"role": "system", "content": "Kamu adalah penerjemah akademis profesional. Berikan hanya terjemahan tanpa komentar tambahan."},
            {"role": "user", "content": prompt},
        ],
        model=MODEL_DEFAULT,
        temperature=0.2,
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
