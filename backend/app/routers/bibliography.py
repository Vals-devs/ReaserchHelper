"""Bibliography generator router."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()


class BibliographyRequest(BaseModel):
    paper_ids: list[str]
    format: str  # "APA" | "IEEE" | "Chicago"


@router.post("/generate")
async def generate_bibliography(
    data: BibliographyRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate bibliography in APA, IEEE, or Chicago format."""
    # TODO: Implement bibliography formatting
    return {"format": data.format, "entries": []}
