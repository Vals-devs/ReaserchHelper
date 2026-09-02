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
from app.services import gemini as ai_service

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

    # Validate Magic Bytes (%PDF-) signature to prevent file spoofing
    if not file_bytes.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="File yang di-upload bukan dokumen PDF valid.",
        )

    # Calculate current storage used by this user
    user_papers_res = await db.execute(
        select(Paper).where(Paper.source == "uploaded", Paper.user_id == current_user.id)
    )
    user_papers = user_papers_res.scalars().all()
    current_used_bytes = sum(p.file_size_bytes or 0 for p in user_papers)
    user_quota = getattr(current_user, "storage_quota_bytes", 104857600) or 104857600

    if current_used_bytes + len(file_bytes) > user_quota:
        used_mb = round(current_used_bytes / (1024 * 1024), 1)
        quota_mb = round(user_quota / (1024 * 1024), 0)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Kuota penyimpanan Anda ({quota_mb:.0f} MB) telah penuh ({used_mb} MB terpakai). Tingkatkan ke Paket Pro untuk mendapatkan kuota 5 GB!",
        )

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
    metadata = await ai_service.extract_paper_metadata(
        pdf_data["full_text"],
        title_hint=pdf_data["title_hint"],
    )

    # Check for duplicate uploaded paper by title for THIS user (case-insensitive)
    normalized_title = metadata["title"].strip().lower()
    existing_check = await db.execute(
        select(Paper).where(Paper.source == "uploaded", Paper.user_id == current_user.id)
    )
    all_uploaded = existing_check.scalars().all()
    duplicate = None
    for p in all_uploaded:
        if p.title.strip().lower() == normalized_title:
            duplicate = p
            break

    if duplicate:
        # Delete the saved PDF file to avoid leaving orphan files on disk
        if file_path.exists():
            try:
                os.remove(file_path)
            except Exception:
                pass
        raise HTTPException(
            status_code=400,
            detail=f"Paper dengan judul ini sudah di-upload sebelumnya: '{duplicate.title}'",
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
        journal=metadata.get("journal", "Uploaded PDF"),
        accreditation=metadata.get("accreditation", "PDF Uploaded"),
        uploaded_file_path=str(file_path),
        user_id=current_user.id,
        file_size_bytes=len(file_bytes),
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
        "journal": paper.journal,
        "accreditation": paper.accreditation,
        "page_count": paper.page_count,
        "uploaded_at": paper.cached_at.isoformat(),
    }


@router.get("/storage-usage")
async def get_storage_usage(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's storage usage and quota."""
    user_papers_res = await db.execute(
        select(Paper).where(Paper.source == "uploaded", Paper.user_id == current_user.id)
    )
    user_papers = user_papers_res.scalars().all()
    
    used_bytes = 0
    for p in user_papers:
        if p.file_size_bytes and p.file_size_bytes > 0:
            used_bytes += p.file_size_bytes
        elif p.uploaded_file_path and os.path.exists(p.uploaded_file_path):
            try:
                sz = os.path.getsize(p.uploaded_file_path)
                p.file_size_bytes = sz
                used_bytes += sz
            except Exception:
                pass
        elif p.full_text:
            sz = len(p.full_text.encode("utf-8"))
            used_bytes += sz

    try:
        await db.flush()
    except Exception:
        pass

    quota_bytes = getattr(current_user, "storage_quota_bytes", 104857600) or 104857600
    plan_tier = getattr(current_user, "plan_tier", "free") or "free"

    percentage = min(100.0, round((used_bytes / quota_bytes) * 100, 1))

    return {
        "used_bytes": used_bytes,
        "quota_bytes": quota_bytes,
        "used_mb": round(used_bytes / (1024 * 1024), 2),
        "quota_mb": round(quota_bytes / (1024 * 1024), 0),
        "percentage": percentage,
        "plan_tier": plan_tier,
    }


@router.get("/papers")
async def list_uploaded_papers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all uploaded papers belonging to the current logged in user."""
    result = await db.execute(
        select(Paper)
        .where(Paper.source == "uploaded", Paper.user_id == current_user.id)
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
            "journal": p.journal or "Uploaded PDF",
            "accreditation": p.accreditation or "PDF Uploaded",
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
    """Delete an uploaded paper and its PDF file belonging to the user."""
    result = await db.execute(
        select(Paper).where(
            Paper.id == paper_id,
            Paper.source == "uploaded",
            Paper.user_id == current_user.id,
        )
    )
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper tidak ditemukan")

    # Delete PDF file
    if paper.uploaded_file_path and os.path.exists(paper.uploaded_file_path):
        os.remove(paper.uploaded_file_path)

    await db.delete(paper)
