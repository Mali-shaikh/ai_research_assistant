from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.agents.citation_agent import extract_citations
from app.agents.compare_agent import compare_documents
from app.agents.intent_agent import detect_intent
from app.agents.qa_agent import answer_question
from app.agents.summarizer_agent import summarize_document
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse, CompareRequest
from app.services.gemini_service import ask_gemini
from app.services.repository_service import save_chat, save_citation, save_summary

router = APIRouter(tags=["chat"])

@router.post("/api/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    intent = detect_intent(payload.message)
    document_text = ""
    document = None

    if payload.document_id:
        document = db.query(Document).filter(
            Document.id == payload.document_id,
            Document.owner_id == current_user.id,
        ).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found.")
        document_text = document.content_text

    if intent == "summarize":
        if not document_text:
            result = "Please select a document for summarization."
        else:
            result = summarize_document(document_text)
            save_summary(db, document.id, "structured", result)
    elif intent == "citation":
        if not document_text:
            result = "Please select a document for citation extraction."
        else:
            result = extract_citations(document_text)
            save_citation(db, document.id, result)
    elif intent == "qa":
        if not document_text:
            result = "Please select a document before asking document-based questions."
        else:
            result = answer_question(document_text, payload.message)
    else:
        result = ask_gemini(payload.message)

    save_chat(db, current_user.id, payload.document_id, intent, payload.message, result)
    return ChatResponse(intent=intent, response=result)

@router.post("/api/compare")
def compare(
    payload: CompareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc1 = db.query(Document).filter(Document.id == payload.doc1_id, Document.owner_id == current_user.id).first()
    doc2 = db.query(Document).filter(Document.id == payload.doc2_id, Document.owner_id == current_user.id).first()

    if not doc1 or not doc2:
        raise HTTPException(status_code=404, detail="One or both documents not found.")

    result = compare_documents(doc1.content_text, doc2.content_text)
    return {"comparison_result": result}
