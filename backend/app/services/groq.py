"""Groq API wrapper — delegates to Gemini API as default service provider."""

import logging
from app.services import gemini

logger = logging.getLogger(__name__)

MODEL_DEFAULT = "gemini-2.0-flash"
MODEL_LONG = "gemini-2.0-flash"

# Forward function calls to Gemini service for full backward compatibility
chat_completion = gemini.chat_completion
summarize_paper = gemini.summarize_paper
explain_text = gemini.explain_text
translate_text = gemini.translate_text
extract_paper_metadata = gemini.extract_paper_metadata
gap_analysis = gemini.gap_analysis
extract_keywords = gemini.extract_keywords
