from sqlalchemy.orm import Session
from app.models.document import Document, DocumentChunk, Summary, Citation
from app.models.chat import ChatHistory

def create_document(db: Session, owner_id: int, title: str, file_path: str, file_type: str, content_text: str):
    doc = Document(
        owner_id=owner_id,
        title=title,
        file_path=file_path,
        file_type=file_type,
        content_text=content_text,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def create_chunks(db: Session, document_id: int, chunks: list[str]):
    for idx, chunk in enumerate(chunks):
        db.add(DocumentChunk(document_id=document_id, chunk_index=idx, chunk_text=chunk))
    db.commit()

def save_summary(db: Session, document_id: int, summary_type: str, summary_text: str):
    item = Summary(document_id=document_id, summary_type=summary_type, summary_text=summary_text)
    db.add(item)
    db.commit()
    return item

def save_citation(db: Session, document_id: int, citation_text: str):
    item = Citation(document_id=document_id, citation_text=citation_text)
    db.add(item)
    db.commit()
    return item

def save_chat(db: Session, user_id: int, document_id: int | None, task_type: str, user_message: str, ai_response: str):
    item = ChatHistory(
        user_id=user_id,
        document_id=document_id,
        task_type=task_type,
        user_message=user_message,
        ai_response=ai_response,
    )
    db.add(item)
    db.commit()
    return item
