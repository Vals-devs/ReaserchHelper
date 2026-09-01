"""Google Gemini API wrapper for AI features."""

import asyncio
import json
import logging
import re
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

MAX_CHARS_PER_PAPER = 4000
MAX_TOTAL_CHARS = 20000


def _parse_json_response(text: str) -> dict | list | str:
    """Parse JSON from AI response, handling markdown code blocks and extra text."""
    if not text or not text.strip():
        return text

    cleaned = text.strip()

    # 1. Direct parse
    try:
        return json.loads(cleaned)
    except (json.JSONDecodeError, ValueError):
        pass

    # 2. Strip markdown code fences (```json ... ```)
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


async def generate_content(
    prompt: str,
    system_instruction: str = "",
    model: str | None = None,
    temperature: float = 0.3,
    max_tokens: int = 2048,
    json_output: bool = False,
) -> str:
    """Send a generateContent request to Gemini API with automatic retries."""
    if not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY is not configured")
        return "[Gemini API key not configured]"

    target_model = model or settings.GEMINI_MODEL or "gemini-2.5-flash"
    url = f"{BASE_URL}/{target_model}:generateContent?key={settings.GEMINI_API_KEY}"

    payload: dict = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        },
    }

    if json_output:
        payload["generationConfig"]["responseMimeType"] = "application/json"

    if system_instruction:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }

    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )
                if resp.status_code in (429, 503) and attempt < max_retries:
                    wait_time = (attempt + 1) * 3.0
                    logger.warning(f"Gemini API returned status {resp.status_code}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                resp.raise_for_status()
                data = resp.json()
                
                candidates = data.get("candidates", [])
                if candidates and "content" in candidates[0]:
                    parts = candidates[0]["content"].get("parts", [])
                    if parts and "text" in parts[0]:
                        return parts[0]["text"]
                
                return ""
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (429, 503) and attempt < max_retries:
                wait_time = (attempt + 1) * 3.0
                logger.warning(f"Gemini API HTTPStatusError {e.response.status_code}. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue
            error_body = e.response.text[:300] if e.response else "unknown"
            logger.error(f"Gemini API error ({e.response.status_code}): {error_body}")
            return f"[Gemini API error: {e.response.status_code}]"
        except Exception as e:
            if attempt < max_retries:
                wait_time = (attempt + 1) * 3.0
                logger.warning(f"Gemini request failed: {e}. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue
            logger.error(f"Gemini request failed: {e}")
            return f"[Gemini request failed: {e}]"

    return "[Gemini request failed]"


async def chat_completion(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.3,
    max_tokens: int = 2048,
) -> str:
    """Send a chat completion request with list of messages (system, user, assistant)."""
    system_instruction = ""
    contents = []

    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            system_instruction += content + "\n"
        else:
            gemini_role = "model" if role in ("assistant", "model") else "user"
            contents.append({
                "role": gemini_role,
                "parts": [{"text": content}]
            })

    if not contents:
        contents = [{"role": "user", "parts": [{"text": "Hello"}]}]

    target_model = model or settings.GEMINI_MODEL or "gemini-2.5-flash"
    url = f"{BASE_URL}/{target_model}:generateContent?key={settings.GEMINI_API_KEY}"

    payload: dict = {
        "contents": contents,
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        },
    }

    if system_instruction.strip():
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction.strip()}]
        }

    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )
                if resp.status_code in (429, 503) and attempt < max_retries:
                    wait_time = (attempt + 1) * 3.0
                    logger.warning(f"Gemini chat_completion returned {resp.status_code}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                resp.raise_for_status()
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates and "content" in candidates[0]:
                    parts = candidates[0]["content"].get("parts", [])
                    if parts and "text" in parts[0]:
                        return parts[0]["text"]
                return ""
        except Exception as e:
            if attempt < max_retries:
                wait_time = (attempt + 1) * 3.0
                await asyncio.sleep(wait_time)
                continue
            logger.error(f"Gemini chat_completion failed: {e}")
            return f"[Gemini chat_completion failed: {e}]"

    return "[Gemini chat_completion failed]"


async def summarize_paper(title: str, abstract: str) -> dict:
    """Generate a paper summary in Bahasa Indonesia."""
    system_prompt = (
        "Kamu adalah asisten peneliti yang meringkas paper ilmiah dalam bahasa Indonesia. "
        "Selalu berikan output HANYA dalam format JSON valid dengan struktur: "
        '{"ringkasan": "ringkasan 3-5 kalimat", "temuan_utama": ["poin 1", "poin 2", "poin 3"], "metodologi": "deskripsi singkat metodologi"}'
    )

    user_prompt = f"Judul: {title}\nAbstrak: {abstract}\n\nRingkas paper tersebut ke dalam format JSON."

    result = await generate_content(
        prompt=user_prompt,
        system_instruction=system_prompt,
        temperature=0.2,
        json_output=True,
    )
    parsed = _parse_json_response(result)
    if isinstance(parsed, dict):
        return {
            "ringkasan": parsed.get("ringkasan", ""),
            "temuan_utama": parsed.get("temuan_utama", []),
            "metodologi": parsed.get("metodologi", ""),
        }
    return {"ringkasan": result, "temuan_utama": [], "metodologi": ""}


async def explain_text(text: str, language: str = "id") -> str:
    """Explain text in plain language."""
    lang_instruction = "bahasa Indonesia yang sederhana" if language == "id" else "simple English"
    prompt = f"Jelaskan teks akademis berikut dalam {lang_instruction}, seperti menjelaskan ke teman yang bukan ahli:\n\n{text}"

    return await generate_content(
        prompt=prompt,
        temperature=0.3,
    )


async def translate_text(text: str, target_language: str = "id") -> str:
    """Translate text to target language (default: Indonesian)."""
    if target_language == "id":
        lang_name = "bahasa Indonesia yang formal dan akademis"
    else:
        lang_name = "English (academic and formal)"

    system_prompt = "Kamu adalah penerjemah akademis profesional. Berikan hanya terjemahan tanpa komentar tambahan."
    prompt = (
        f"Terjemahkan teks akademis berikut ke {lang_name}.\n"
        "Pertahankan istilah teknis dalam tanda kurung jika perlu.\n\n"
        f"Teks asli:\n{text}"
    )

    return await generate_content(
        prompt=prompt,
        system_instruction=system_prompt,
        temperature=0.2,
    )


async def extract_paper_metadata(full_text: str, title_hint: str = "") -> dict:
    """Extract structured metadata from raw PDF text using AI."""
    text_sample = full_text[:4000]

    system_prompt = (
        "Ekstrak metadata dari paper ilmiah berikut ke format JSON dengan kunci:\n"
        '- "title": judul paper (string)\n'
        '- "authors": daftar nama author (array of strings)\n'
        '- "year": tahun publikasi (integer, atau null jika tidak ditemukan)\n'
        '- "abstract": abstrak atau ringkasan paper (string, 3-5 kalimat)\n'
    )

    prompt = f'Title Hint: "{title_hint}"\n\nTeks paper:\n{text_sample}'

    result = await generate_content(
        prompt=prompt,
        system_instruction=system_prompt,
        temperature=0.1,
        json_output=True,
    )
    parsed = _parse_json_response(result)
    if isinstance(parsed, dict):
        return {
            "title": parsed.get("title", title_hint or "Untitled Paper"),
            "authors": parsed.get("authors", []),
            "year": parsed.get("year"),
            "abstract": parsed.get("abstract", ""),
        }
    return {
        "title": title_hint or "Untitled Paper",
        "authors": [],
        "year": None,
        "abstract": "",
    }


async def gap_analysis(papers: list[dict]) -> dict:
    """Analyze research gaps across multiple papers."""
    papers_text_parts = []
    for i, p in enumerate(papers):
        content = p.get("full_text") or p.get("abstract", "N/A")
        if len(content) > MAX_CHARS_PER_PAPER:
            content = content[:MAX_CHARS_PER_PAPER] + "... [truncated]"
        papers_text_parts.append(f"=== Paper {i+1}: {p.get('title', 'Untitled')} ===\n{content}")

    papers_text = "\n\n".join(papers_text_parts)

    if len(papers_text) > MAX_TOTAL_CHARS:
        papers_text_parts = []
        for i, p in enumerate(papers):
            abstract = p.get("abstract", "N/A") or "N/A"
            if len(abstract) > 1000:
                abstract = abstract[:1000] + "..."
            papers_text_parts.append(f"=== Paper {i+1}: {p.get('title', 'Untitled')} ===\n{abstract}")
        papers_text = "\n\n".join(papers_text_parts)

    system_prompt = (
        "Kamu adalah seorang profesor dan peneliti berpengalaman. "
        "Analisis paper-paper berikut dan identifikasi research gap dalam format JSON valid dengan struktur:\n"
        "{\n"
        '  "topik_dominan": [{"name": "nama topik", "count": 1, "desc": "deskripsi"}],\n'
        '  "metodologi": [{"name": "nama metode", "freq": "Sering/Sedang/Jarang", "desc": "deskripsi"}],\n'
        '  "celah_penelitian": [{"title": "judul celah", "desc": "penjelasan detail", "priority": "Tinggi/Sedang"}],\n'
        '  "saran_topik": ["saran topik 1", "saran topik 2"]\n'
        "}"
    )

    result = await generate_content(
        prompt=papers_text,
        system_instruction=system_prompt,
        temperature=0.4,
        max_tokens=3000,
        json_output=True,
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
    system_prompt = (
        "Ekstrak 5-8 keyword penting dari abstrak berikut untuk query pencarian paper. "
        "Berikan output sebagai JSON array of strings, contoh: [\"keyword1\", \"keyword2\"]"
    )

    result = await generate_content(
        prompt=abstract,
        system_instruction=system_prompt,
        max_tokens=256,
        json_output=True,
    )
    parsed = _parse_json_response(result)
    if isinstance(parsed, list):
        return [str(k) for k in parsed]
    return [result]
