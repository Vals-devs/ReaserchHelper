"""Google Gemini API wrapper for AI features."""

import asyncio
import json
import logging
import re
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

MAX_CHARS_PER_PAPER = 2500
MAX_TOTAL_CHARS = 15000


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
    """Send a generateContent request to Gemini API with automatic retries and model fallback."""
    if not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY is not configured")
        return "[Gemini API key not configured]"

    primary_model = model or settings.GEMINI_MODEL or "gemini-3.5-flash-lite"
    candidate_models = [primary_model]
    for fallback in ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-3.6-flash", "gemini-flash-latest"]:
        if fallback not in candidate_models:
            candidate_models.append(fallback)

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

    for current_model in candidate_models:
        url = f"{BASE_URL}/{current_model}:generateContent?key={settings.GEMINI_API_KEY}"
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=60) as client:
                    resp = await client.post(
                        url,
                        json=payload,
                        headers={"Content-Type": "application/json"},
                    )
                    if resp.status_code == 404:
                        logger.warning(f"Gemini model {current_model} returned 404. Trying next model...")
                        break  # Try next candidate_model

                    if resp.status_code in (429, 503) and attempt < max_retries:
                        wait_time = (attempt + 1) * 3.0
                        logger.warning(f"Gemini API ({current_model}) returned {resp.status_code}. Retrying in {wait_time}s...")
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
                if e.response.status_code == 404:
                    logger.warning(f"Gemini model {current_model} returned 404. Trying next model...")
                    break
                if e.response.status_code in (429, 503) and attempt < max_retries:
                    wait_time = (attempt + 1) * 3.0
                    logger.warning(f"Gemini API HTTPStatusError {e.response.status_code}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                error_body = e.response.text[:300] if e.response else "unknown"
                logger.error(f"Gemini API error ({e.response.status_code}): {error_body}")
                if e.response.status_code in (400, 403):
                    return f"[Gemini API key tidak valid / ditolak: {error_body}]"
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
    """Send a chat completion request with list of messages using generate_content."""
    system_instruction = ""
    prompt_parts = []

    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            system_instruction += content + "\n"
        elif role in ("user", "human"):
            prompt_parts.append(f"User: {content}")
        elif role in ("assistant", "model"):
            prompt_parts.append(f"Assistant: {content}")

    prompt = "\n\n".join(prompt_parts) if prompt_parts else "Hello"

    return await generate_content(
        prompt=prompt,
        system_instruction=system_instruction.strip(),
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )


async def summarize_paper(title: str, abstract: str) -> dict:
    """Generate a high-quality paper summary in Bahasa Indonesia."""
    system_prompt = (
        "Kamu adalah seorang Profesor dan Asisten Peneliti Akademis Senior yang berpengalaman dalam menelaah jurnal ilmiah. "
        "Tugasmu adalah menganalisis paper ilmiah berikut dan membuat ringkasan yang informatif, mendalam, ilmiah, dan terstruktur dalam Bahasa Indonesia.\n\n"
        "Panduan Komponen Output JSON:\n"
        "- 'ringkasan': Sintesis 3-5 kalimat ilmiah yang padat, menjelaskan latar belakang masalah, tujuan utama penelitian, dan kesimpulan akhir.\n"
        "- 'temuan_utama': Array berisi 3-5 poin temuan kualitatif/kuantitatif spesifik beserta signifikansi risetnya.\n"
        "- 'metodologi': Deskripsi lugas mengenai pendekatan riset, dataset, algoritma/teknik yang digunakan, serta metrik evaluasinya.\n\n"
        "Selalu berikan output HANYA dalam format JSON valid dengan struktur:\n"
        '{"ringkasan": "...", "temuan_utama": ["poin 1", "poin 2"], "metodologi": "..."}'
    )

    user_prompt = f"Paper Ilmiah:\nJudul: {title}\nAbstrak: {abstract}\n\nBerikan ringkasan akademik lengkap dalam format JSON."

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
    """Explain complex academic text in plain, accessible language."""
    if language == "id":
        system_prompt = (
            "Kamu adalah seorang Dosen dan Mentor Riset Akademik yang ramah dan komunikatif. "
            "Tugasmu adalah menjelaskan bagian teks akademis berikut ke dalam Bahasa Indonesia yang sederhana, komunikatif, dan mudah dipahami oleh mahasiswa tingkat awal.\n"
            "Gunakan analogi atau contoh nyata jika relevan, uraikan istilah ilmiah yang rumit dalam tanda kurung, dan gunakan struktur poin-poin agar nyaman dibaca."
        )
    else:
        system_prompt = (
            "You are an expert Academic Research Mentor. "
            "Explain the following complex academic text in simple, clear, and plain English for students.\n"
            "Use clear analogies, define technical terms in brackets, and break down complex concepts into readable points."
        )

    return await generate_content(
        prompt=text,
        system_instruction=system_prompt,
        temperature=0.3,
    )


async def translate_text(text: str, target_language: str = "id") -> str:
    """Translate academic text to formal target language (default: Indonesian PUEBI)."""
    if target_language == "id":
        system_prompt = (
            "Kamu adalah Penerjemah Akademis Profesional dan Editor Jurnal Ilmiah Internasional. "
            "Tugasmu adalah menerjemahkan teks akademis berikut ke Bahasa Indonesia formal (baku & akademik) sesuai standar Pedoman Umum Ejaan Bahasa Indonesia (PUEBI).\n"
            "Aturan Penulisan:\n"
            "- Pertahankan istilah teknis/istilah asing yang spesifik dalam tanda kurung '(istilah)' pada kemunculan pertama.\n"
            "- Jaga presisi makna ilmiah dan struktur kalimat akademis.\n"
            "- Berikan HANYA teks terjemahan akhir tanpa kata pengantar atau komentar tambahan."
        )
    else:
        system_prompt = (
            "You are a professional Academic Translator and Scientific Journal Editor. "
            "Translate the following text into formal academic English.\n"
            "Maintain technical terms in brackets where helpful and preserve scientific accuracy.\n"
            "Provide ONLY the final translation without any introductory text."
        )

    return await generate_content(
        prompt=text,
        system_instruction=system_prompt,
        temperature=0.2,
    )


async def extract_paper_metadata(full_text: str, title_hint: str = "") -> dict:
    """Extract structured metadata from raw PDF text using AI."""
    text_sample = full_text[:4000]

    system_prompt = (
        "Kamu adalah pakar ekstraksi data karya ilmiah berbasis AI. "
        "Tugasmu adalah menganalisis teks paper berikut dan mengekstrak metadata utamanya secara presisi ke dalam format JSON.\n\n"
        "Aturan Ekstraksi:\n"
        "- 'title': Judul lengkap paper ilmiah.\n"
        "- 'authors': Daftar nama penulis (array of strings).\n"
        "- 'year': Tahun publikasi (integer, atau null jika tidak ditemukan).\n"
        "- 'abstract': Abstrak atau ringkasan 3-5 kalimat dari teks paper.\n\n"
        "Berikan output HANYA dalam format JSON valid."
    )

    prompt = f'Title Hint (jika ada): "{title_hint}"\n\nTeks Paper:\n{text_sample}'

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
    """Analyze research gaps across multiple papers with deep academic prompts."""
    papers_text_parts = []
    for i, p in enumerate(papers):
        content = p.get("abstract") or p.get("full_text", "N/A") or "N/A"
        if len(content) > 1800:
            content = content[:1800] + "... [truncated]"
        papers_text_parts.append(f"=== Paper {i+1}: {p.get('title', 'Untitled')} ===\n{content}")

    papers_text = "\n\n".join(papers_text_parts)

    system_prompt = (
        "Kamu adalah seorang Guru Besar, Peneliti Senior, dan Ketua Dewan Penguji Riset Akademis. "
        "Tugasmu adalah melakukan Analisis Celah Penelitian (Research Gap Analysis) yang kritis, akademis, dan komprehensif berdasarkan kumpulan paper referensi berikut.\n\n"
        "Petunjuk Analisis:\n"
        "1. 'topik_dominan': Identifikasi 2-4 tren topik utama yang paling sering dibahas beserta deskripsi tren risetnya.\n"
        "2. 'metodologi': Evaluasi 2-4 pendekatan/algoritma/metode yang digunakan, frekuensinya (Sering/Sedang/Jarang), dan kelemahannya.\n"
        "3. 'celah_penelitian': Identifikasi 2-4 celah riset (research gap) konkret yang belum tereksplorasi, sertakan penjelasan detail mengapa ini menjadi celah dan kontribusi ilmiah jika diteliti, serta prioritasnya (Tinggi/Sedang).\n"
        "4. 'saran_topik': Berikan 3-5 usulan judul/topik skripsi/tugas akhir yang spesifik, inovatif, dan siap diteliti oleh mahasiswa.\n\n"
        "Selalu berikan output HANYA dalam format JSON valid dengan struktur:\n"
        "{\n"
        '  "topik_dominan": [{"name": "...", "count": 1, "desc": "..."}],\n'
        '  "metodologi": [{"name": "...", "freq": "Sering/Sedang/Jarang", "desc": "..."}],\n'
        '  "celah_penelitian": [{"title": "...", "desc": "...", "priority": "Tinggi/Sedang"}],\n'
        '  "saran_topik": ["Saran Judul 1...", "Saran Judul 2..."]\n'
        "}"
    )

    result = await generate_content(
        prompt=papers_text,
        system_instruction=system_prompt,
        temperature=0.3,
        max_tokens=2048,
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
        "Kamu adalah pakar temu balik informasi (information retrieval) dan pustakawan ilmiah. "
        "Tugasmu adalah menganalisis abstrak berikut dan mengekstrak 5-8 kata kunci/frasa akademis paling relevan (kombinasi Bahasa Inggris & Indonesia) untuk query pencarian paper ilmiah terkait.\n"
        "Berikan output HANYA sebagai JSON array of strings, contoh: [\"deep learning\", \"cybersecurity\", \"vulnerability scanning\"]"
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
