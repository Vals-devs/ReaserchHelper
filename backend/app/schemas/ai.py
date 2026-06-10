"""AI-related Pydantic schemas."""

from pydantic import BaseModel


class GapAnalysisResult(BaseModel):
    dominant_topics: list[dict]
    methodologies: list[dict]
    research_gaps: list[dict]
    suggestions: list[str]


class ExplainResult(BaseModel):
    original_text: str
    explanation: str
    language: str


class KeywordExtraction(BaseModel):
    keywords: list[str]
