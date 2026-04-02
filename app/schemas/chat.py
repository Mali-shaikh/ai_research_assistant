from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    message: str
    document_id: Optional[int] = None

class ChatResponse(BaseModel):
    intent: str
    response: str

class CompareRequest(BaseModel):
    doc1_id: int
    doc2_id: int
