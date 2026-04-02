from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.document import UploadResponse
from app.services.document_service import extract_text
from app.services.repository_service import create_document, create_chunks
from app.utils.files import validate_upload, build_safe_upload_path
from app.utils.text import chunk_text
from app.core.config import settings

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.post("/upload", response_model=UploadResponse)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    extension = validate_upload(file)
    content = file.file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_MB:
        raise HTTPException(status_code=400, detail=f"File exceeds {settings.MAX_UPLOAD_MB} MB limit.")

    destination = build_safe_upload_path(file.filename)
    Path(destination).write_bytes(content)

    extracted_text = extract_text(destination)
    if not extracted_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from file.")

    doc = create_document(
        db=db,
        owner_id=current_user.id,
        title=file.filename,
        file_path=destination,
        file_type=extension,
        content_text=extracted_text,
    )
    create_chunks(db, doc.id, chunk_text(extracted_text))

    return UploadResponse(message="Document uploaded successfully.", document=doc)

@router.get("")
def list_documents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    docs = (
        db.query(Document)
        .filter(Document.owner_id == current_user.id)
        .order_by(Document.id.desc())
        .all()
    )
    return docs
