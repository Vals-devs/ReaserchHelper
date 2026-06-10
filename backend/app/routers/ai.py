"""AI features router - summarize, explain, gap analysis, related suggestions."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.paper import Paper
from app.services import groq as groq_service

router = APIRouter()


from pydantic import BaseModel


class SummarizeRequest(BaseModel):
    paper_id: str


class TranslateRequest(BaseModel):
    text: str
    target_language: str = "id"  # "id" or "en"


class ExplainRequest(BaseModel):
    text: str
    language: str = "id"  # "id" or "en"


class GapAnalysisRequest(BaseModel):
    paper_ids: list[str]


class SuggestRelatedRequest(BaseModel):
    paper_id: str


@router.post("/summarize")
async def summarize_paper(
    data: SummarizeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate AI summary for a paper."""
    result = await db.execute(select(Paper).where(Paper.id == data.paper_id))
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    summary = await groq_service.summarize_paper(paper.title, paper.abstract or "")
    return {"paper_id": data.paper_id, "summary": summary}


@router.post("/translate")
async def translate_abstract(
    data: TranslateRequest,
    current_user: User = Depends(get_current_user),
):
    """Translate text to target language."""
    translation = await groq_service.translate_text(data.text, data.target_language)
    return {"translation": translation}


@router.post("/explain")
async def explain_text(
    data: ExplainRequest,
    current_user: User = Depends(get_current_user),
):
    """Explain text in plain language."""
    explanation = await groq_service.explain_text(data.text, data.language)
    return {"explanation": explanation}


@router.post("/gap-analysis")
async def gap_analysis(
    data: GapAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Analyze research gaps across multiple papers."""
    if len(data.paper_ids) < 3:
        raise HTTPException(status_code=400, detail="Select at least 3 papers")

    result = await db.execute(select(Paper).where(Paper.id.in_(data.paper_ids)))
    papers = result.scalars().all()
    if len(papers) < 3:
        raise HTTPException(status_code=404, detail="Not enough papers found")

    papers_data = [
        {
            "title": p.title,
            "abstract": p.abstract or "N/A",
            "full_text": p.full_text,  # Preferred by Groq for uploaded papers
        }
        for p in papers
    ]
    gaps = await groq_service.gap_analysis(papers_data)

    # Check if Groq returned an error string
    if isinstance(gaps, dict) and gaps.get("raw_response", "").startswith("[Groq"):
        raise HTTPException(status_code=502, detail=gaps["raw_response"])

    return {"gaps": gaps}


@router.post("/suggest-related")
async def suggest_related(
    data: SuggestRelatedRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Suggest related papers via AI keyword extraction + Semantic Scholar."""
    result = await db.execute(select(Paper).where(Paper.id == data.paper_id))
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    keywords = await groq_service.extract_keywords(paper.abstract or "")

    # Search Semantic Scholar with extracted keywords
    from app.services import semantic_scholar as s2_service
    suggestions = []
    if keywords:
        query = " ".join(keywords[:3]) if isinstance(keywords, list) else str(keywords)
        search_result = await s2_service.search_papers(query=query, limit=10)
        suggestions = search_result.get("results", [])

    return {"paper_id": data.paper_id, "keywords": keywords, "suggestions": suggestions}


class ChatMessage(BaseModel):
    role: str
    content: str


class PaperChatRequest(BaseModel):
    paper_id: str
    messages: list[ChatMessage]


@router.post("/chat")
async def chat_about_paper(
    data: PaperChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Chat/Q&A about a paper's content."""
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Paper)
        .options(selectinload(Paper.summaries))
        .where(Paper.id == data.paper_id)
    )
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    has_full_text = bool(paper.full_text)

    context = f"Judul Paper: {paper.title}\n"
    if paper.authors:
        context += f"Penulis: {', '.join(paper.authors) if isinstance(paper.authors, list) else str(paper.authors)}\n"
    if paper.year:
        context += f"Tahun: {paper.year}\n"

    # Include existing AI summaries in context
    if paper.summaries:
        context += "\n--- INFORMASI RINGKASAN & METODOLOGI AI SEBELUMNYA ---\n"
        for s in paper.summaries:
            context += f"Ringkasan AI: {s.summary_text}\n"
            if s.methodology:
                context += f"Metodologi AI: {s.methodology}\n"
            if s.key_findings:
                findings_str = ", ".join(s.key_findings) if isinstance(s.key_findings, list) else str(s.key_findings)
                context += f"Temuan Utama AI: {findings_str}\n"
        context += "---------------------------------------------------\n\n"

    if paper.abstract:
        context += f"Abstrak:\n{paper.abstract}\n"
    if paper.full_text:
        context += f"Teks Lengkap (sebagian):\n{paper.full_text[:6000]}\n"

    system_prompt = f"""Kamu adalah asisten AI peneliti akademik profesional yang membantu pengguna menganalisis dan memahami paper ilmiah berikut.
Jawab pertanyaan mereka berdasarkan konteks paper ini secara objektif, ilmiah, dan informatif.
Jawablah dalam bahasa Indonesia (atau gunakan bahasa Inggris jika pengguna bertanya dalam bahasa Inggris).
"""

    if not has_full_text:
        system_prompt += """
Catatan Penting: Saat ini Anda HANYA memiliki akses ke ABSTRAK paper (tidak ada PDF teks lengkap). 
Jika pengguna menanyakan tentang metodologi, kesimpulan, atau temuan spesifik yang tidak tertulis secara eksplisit, cobalah untuk melakukan deduksi ilmiah yang logis berdasarkan informasi di abstrak, alih-alih langsung menolak menjawab. Berikan estimasi/kesimpulan terbaik Anda dan sebutkan secara ramah bahwa ini adalah deduksi dari abstrak karena teks lengkap PDF belum diunggah.
"""
    else:
        system_prompt += """
Jika jawabannya tidak terdapat dalam dokumen paper tersebut, katakan secara jujur dan sopan bahwa informasi tersebut tidak ditemukan dalam dokumen paper ini.
"""

    system_prompt += f"""
Konteks Dokumen Paper:
---
{context}
---
"""

    formatted_messages = [{"role": "system", "content": system_prompt}]
    for msg in data.messages:
        formatted_messages.append({"role": msg.role, "content": msg.content})

    try:
        reply = await groq_service.chat_completion(
            messages=formatted_messages,
            model=groq_service.MODEL_DEFAULT,
            temperature=0.3,
            max_tokens=1000
        )
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memproses AI Chat: {e}")


class GapChatRequest(BaseModel):
    paper_ids: list[str]
    messages: list[ChatMessage]


@router.post("/gap-chat")
async def chat_about_gaps(
    data: GapChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Chat/Q&A about a research gap analysis for a set of papers."""
    if not data.paper_ids:
        raise HTTPException(status_code=400, detail="Select at least one paper")

    # Fetch papers
    result = await db.execute(select(Paper).where(Paper.id.in_(data.paper_ids)))
    papers = result.scalars().all()

    if not papers:
        raise HTTPException(status_code=404, detail="No papers found")

    # Construct papers context
    papers_context = ""
    for i, p in enumerate(papers):
        papers_context += f"=== Paper {i+1}: {p.title} ===\n"
        if p.authors:
            papers_context += f"Penulis: {', '.join(p.authors) if isinstance(p.authors, list) else str(p.authors)}\n"
        if p.year:
            papers_context += f"Tahun: {p.year}\n"
        if p.abstract:
            papers_context += f"Abstrak: {p.abstract[:1000]}\n"
        papers_context += "\n"

    system_prompt = f"""Kamu adalah Profesor dan Peneliti Akademik Senior yang bertindak sebagai mentor riset. 
Tugasmu adalah membantu peneliti mendiskusikan celah riset (research gap), merumuskan judul penelitian baru, menyusun pertanyaan penelitian (research questions), serta merekomendasikan metodologi yang tepat berdasarkan kumpulan paper referensi berikut:

--- KUMPULAN PAPER REFERENSI ---
{papers_context}
--------------------------------

Jawablah pertanyaan peneliti secara ramah, akademis, mendalam, dan membimbing. Gunakan format Markdown yang rapi (bullet points, bold text) dalam jawabanmu agar mudah dibaca.
Jika pertanyaan di luar konteks riset paper ini, cobalah untuk tetap membimbing mereka secara ilmiah.
Jawablah dalam bahasa Indonesia (atau gunakan bahasa Inggris jika mereka bertanya dalam bahasa Inggris).
"""

    formatted_messages = [{"role": "system", "content": system_prompt}]
    for msg in data.messages:
        formatted_messages.append({"role": msg.role, "content": msg.content})

    try:
        reply = await groq_service.chat_completion(
            messages=formatted_messages,
            model=groq_service.MODEL_LONG,
            temperature=0.4,
            max_tokens=1000
        )
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memproses Gap AI Chat: {e}")
