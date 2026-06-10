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
    return {"paper_id": data.paper_id, "keywords": keywords, "suggestions": []}
