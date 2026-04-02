from pydantic import BaseModel
from datetime import datetime

class DocumentOut(BaseModel):
    id: int
    title: str
    file_type: str
    created_at: datetime

    model_config = {"from_attributes": True}

class UploadResponse(BaseModel):
    message: str
    document: DocumentOut
