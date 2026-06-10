"""Upload router - PDF paper upload and management."""

import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.paper import Paper
from app.services.pdf_parser import extract_text_from_pdf
from app.services import groq as groq_service

router = APIRouter()

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


@router.post("/pdf", status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a PDF paper, extract text, and use AI to get metadata."""
    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Hanya file PDF yang diterima (.pdf)")

    # Read file bytes
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Ukuran file maksimal 50 MB")
    if len(file_bytes) < 100:
        raise HTTPException(status_code=400, detail="File terlalu kecil atau kosong")

    # Extract text from PDF
    try:
        pdf_data = extract_text_from_pdf(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Gagal membaca PDF: {str(e)}")

    if not pdf_data["full_text"].strip():
        raise HTTPException(
            status_code=400,
            detail="PDF tidak mengandung teks yang bisa dibaca (mungkin scan/image)",
        )

    # Save PDF to disk
    file_id = str(uuid.uuid4())
    safe_name = file.filename.replace(" ", "_")[:100]
    saved_filename = f"{file_id}_{safe_name}"
    file_path = UPLOAD_DIR / saved_filename
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # Use AI to extract metadata
    metadata = await groq_service.extract_paper_metadata(
        pdf_data["full_text"],
        title_hint=pdf_data["title_hint"],
    )

    # Create Paper record
    paper = Paper(
        external_id=f"upload_{file_id}",
        source="uploaded",
        title=metadata["title"],
        authors=metadata["authors"],
        abstract=metadata["abstract"] or None,
        full_text=pdf_data["full_text"],
        year=metadata["year"],
        uploaded_file_path=str(file_path),
        page_count=pdf_data["page_count"],
    )
    db.add(paper)
    await db.flush()
    await db.refresh(paper)

    return {
        "id": paper.id,
        "title": paper.title,
        "authors": paper.authors,
        "year": paper.year,
        "abstract": paper.abstract,
        "page_count": paper.page_count,
        "uploaded_at": paper.cached_at.isoformat(),
    }


@router.get("/papers")
async def list_uploaded_papers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all uploaded papers."""
    result = await db.execute(
        select(Paper)
        .where(Paper.source == "uploaded")
        .order_by(Paper.cached_at.desc())
    )
    papers = result.scalars().all()
    return [
        {
            "id": p.id,
            "title": p.title,
            "authors": p.authors,
            "year": p.year,
            "abstract": p.abstract,
            "page_count": p.page_count,
            "uploaded_at": p.cached_at.isoformat(),
        }
        for p in papers
    ]


@router.delete("/{paper_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_uploaded_paper(
    paper_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an uploaded paper and its PDF file."""
    result = await db.execute(
        select(Paper).where(Paper.id == paper_id, Paper.source == "uploaded")
    )
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper tidak ditemukan")

    # Delete PDF file
    if paper.uploaded_file_path and os.path.exists(paper.uploaded_file_path):
        os.remove(paper.uploaded_file_path)

    await db.delete(paper)
