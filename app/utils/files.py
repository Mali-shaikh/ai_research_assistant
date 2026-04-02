import os
import uuid
from pathlib import Path
from fastapi import HTTPException, UploadFile
from app.core.config import settings

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def validate_upload(file: UploadFile) -> str:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename.")
    extension = os.path.splitext(file.filename)[1].lower()
    if extension not in settings.allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {extension}")
    return extension

def build_safe_upload_path(filename: str) -> str:
    extension = os.path.splitext(filename)[1].lower()
    safe_name = f"{uuid.uuid4().hex}{extension}"
    return str(UPLOAD_DIR / safe_name)
