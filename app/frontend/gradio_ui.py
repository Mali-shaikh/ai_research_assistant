import os
import gradio as gr


# ─── Theme & CSS ──────────────────────────────────────────────────────────────
THEME = gr.themes.Soft(primary_hue="indigo", secondary_hue="slate")
CSS = """
.app-header { text-align: center; margin-bottom: 8px; }
.status-box textarea { font-weight: 600; }
"""

# ─── Helpers ──────────────────────────────────────────────────────────────────

def parse_doc_id(doc_label):
    if not doc_label:
        return None
    try:
        return int(str(doc_label).split(" – ", 1)[0])
    except ValueError:
        return None


def get_user_from_token(token: str):
    if not token:
        return None
    try:
        from app.db.session import SessionLocal
        from app.models.user import User
        from app.utils.security import decode_access_token
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        db.close()
        return user
    except Exception:
        return None

# ─── UI Actions ───────────────────────────────────────────────────────────────

def register(full_name, email, password):
    try:
        from app.db.session import SessionLocal
        from app.services.auth_service import register_user
        from app.schemas.auth import RegisterRequest
        db = SessionLocal()
        payload = RegisterRequest(full_name=full_name, email=email, password=password)
        user = register_user(db, payload)
        db.close()
        return f"✅ Registered successfully! Email: {user.email} | ID: {user.id}"
    except Exception as e:
        return f"❌ {str(e)}" 


def login(email, password):
    try:
        from app.db.session import SessionLocal
        from app.services.auth_service import login_user
        from app.schemas.auth import LoginRequest
        db = SessionLocal()
        payload = LoginRequest(email=email, password=password)
        token = login_user(db, payload)
        db.close()
        return token, "✅ Login successful."
    except Exception as e:
        return "", f"❌ {str(e)}"


def fetch_documents(token):
    user = get_user_from_token(token)
    if not user:
        return gr.update(choices=[], value=None)
    try:
        from app.db.session import SessionLocal
        from app.models.document import Document
        db = SessionLocal()
        docs = db.query(Document).filter(Document.owner_id == user.id).order_by(Document.id.desc()).all()
        db.close()
        choices = [f"{doc.id} – {doc.title}" for doc in docs]
        return gr.update(choices=choices, value=choices[0] if choices else None)
    except Exception:
        return gr.update(choices=[], value=None)

def upload_document(file_obj, token):
    user = get_user_from_token(token)
    if not user:
        return "⚠️ Please login first.", gr.update()
    if file_obj is None:
        return "⚠️ Please choose a file.", gr.update()

    try:
        from app.db.session import SessionLocal
        from app.services.document_service import extract_text
        from app.services.repository_service import create_document, create_chunks
        from app.utils.text import chunk_text

        file_path = file_obj.name if hasattr(file_obj, "name") else str(file_obj)
        filename = os.path.basename(file_path)

        extracted_text = extract_text(file_path)
        if not extracted_text.strip():
            return "❌ Could not extract text from file.", gr.update()

        db = SessionLocal()
        ext = os.path.splitext(filename)[1].lower()
        doc = create_document(
            db=db,
            owner_id=user.id,
            title=filename,
            file_path=file_path,
            file_type=ext,
            content_text=extracted_text
        )
        create_chunks(db, doc.id, chunk_text(extracted_text))
        db.close()
        return f"✅ Uploaded: {filename}", fetch_documents(token)

    except Exception as e:
        return f"❌ Upload failed: {str(e)}", gr.update()
        


def send_chat(message, history, token, selected_doc):
    user = get_user_from_token(token)
    if not user:
        return "", history + [{"role": "assistant", "content": "⚠️ Please login first."}]
    if not message.strip():
        return "", history
    try:
        from app.db.session import SessionLocal
        from app.models.document import Document
        doc_text = ""
        doc_id = parse_doc_id(selected_doc)
        if doc_id:
            db = SessionLocal()
            doc = db.query(Document).filter(Document.id == doc_id, Document.owner_id == user.id).first()
            db.close()
            if doc:
                doc_text = doc.content_text

        msg_lower = message.lower()
        if any(k in msg_lower for k in ["summarize", "summary", "brief", "overview"]):
            if doc_text:
                from app.agents.summarizer_agent import summarize_document
                reply = summarize_document(doc_text)
            else:
                reply = "⚠️ Please select a document first to summarize."
        elif any(k in msg_lower for k in ["citation", "reference", "authors"]):
            if doc_text:
                from app.agents.citation_agent import extract_citations
                reply = extract_citations(doc_text)
            else:
                reply = "⚠️ Please select a document first."
        else:
            if doc_text:
                from app.agents.qa_agent import answer_question
                reply = answer_question(doc_text, message)
            else:
                from app.services.gemini_service import ask_gemini
                reply = ask_gemini(message)
    except Exception as e:
        reply = f"❌ Error: {str(e)}"

    return "", history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": reply},
    ]


def compare_docs(doc1, doc2, token):
    user = get_user_from_token(token)
    if not user:
        return "⚠️ Please login first."
    if not doc1 or not doc2:
        return "⚠️ Please select both documents."
    try:
        from app.db.session import SessionLocal
        from app.models.document import Document
        from app.agents.compare_agent import compare_documents
        db = SessionLocal()
        d1 = db.query(Document).filter(Document.id == parse_doc_id(doc1), Document.owner_id == user.id).first()
        d2 = db.query(Document).filter(Document.id == parse_doc_id(doc2), Document.owner_id == user.id).first()
        db.close()
        if not d1 or not d2:
            return "❌ One or both documents not found."
        return compare_documents(d1.content_text, d2.content_text)
    except Exception as e:
        return f"❌ Comparison failed: {str(e)}"


# ─── UI Layout ────────────────────────────────────────────────────────────────

DESCRIPTION = """
# 🔬 AI Academic Research Assistant
**Upload** research papers · **Chat** with them · **Compare** two papers · **Extract** citations
"""

with gr.Blocks(title="AI Academic Research Assistant", theme=THEME, css=CSS) as demo:
    token_state = gr.State("")

    gr.Markdown(DESCRIPTION, elem_classes="app-header")

    with gr.Tab("🔐 Auth"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Register")
                reg_name     = gr.Textbox(label="Full Name", placeholder="Jane Doe")
                reg_email    = gr.Textbox(label="Email", placeholder="jane@example.com")
                reg_password = gr.Textbox(label="Password", type="password")
                reg_btn      = gr.Button("Register", variant="primary")
                reg_output   = gr.Textbox(label="Response", interactive=False)
 
            with gr.Column():
                gr.Markdown("### Login")
                login_email    = gr.Textbox(label="Email", placeholder="jane@example.com")
                login_password = gr.Textbox(label="Password", type="password")
                login_btn      = gr.Button("Login", variant="primary")
                login_status   = gr.Textbox(label="Login Status", interactive=False, elem_classes="status-box")

        reg_btn.click(register, inputs=[reg_name, reg_email, reg_password], outputs=reg_output)
        login_btn.click(login, inputs=[login_email, login_password], outputs=[token_state, login_status])

    with gr.Tab("📄 Upload & Documents"):
        with gr.Row():
            with gr.Column(scale=1):
                file_input    = gr.File(label="Upload PDF / DOCX / TXT / MD")
                upload_btn    = gr.Button("Upload Document", variant="primary")
                upload_status = gr.Textbox(label="Upload Status", interactive=False, elem_classes="status-box")
            with gr.Column(scale=1):
                doc_dropdown     = gr.Dropdown(label="Your Documents", choices=[], interactive=True)
                refresh_docs_btn = gr.Button("🔄 Refresh Documents")

        upload_btn.click(upload_document, inputs=[file_input, token_state], outputs=[upload_status, doc_dropdown])
        refresh_docs_btn.click(fetch_documents, inputs=[token_state], outputs=[doc_dropdown])

    with gr.Tab("💬 Chat"):
        with gr.Row():
            chat_doc_dropdown = gr.Dropdown(label="Select Document (optional)", choices=[], interactive=True, scale=4)
            refresh_chat_btn  = gr.Button("🔄 Refresh", scale=1)
        chatbot   = gr.Chatbot(height=420, label="Conversation", type="messages")
        msg_input = gr.Textbox(placeholder='e.g. "Summarize this paper"', label="Your message", lines=2)
        with gr.Row():
            send_btn  = gr.Button("Send ▶", variant="primary", scale=3)
            clear_btn = gr.Button("Clear 🗑", scale=1)

        send_btn.click(send_chat, inputs=[msg_input, chatbot, token_state, chat_doc_dropdown], outputs=[msg_input, chatbot])
        msg_input.submit(send_chat, inputs=[msg_input, chatbot, token_state, chat_doc_dropdown], outputs=[msg_input, chatbot])
        clear_btn.click(lambda: [], outputs=chatbot)
        refresh_chat_btn.click(fetch_documents, inputs=[token_state], outputs=[chat_doc_dropdown])

    with gr.Tab("⚖️ Compare Papers"):
        with gr.Row():
            compare_doc1 = gr.Dropdown(label="Document 1", choices=[], interactive=True)
            compare_doc2 = gr.Dropdown(label="Document 2", choices=[], interactive=True)
        with gr.Row():
            compare_refresh = gr.Button("🔄 Refresh Document Lists")
            compare_btn     = gr.Button("Compare ⚖️", variant="primary")
        compare_output = gr.Textbox(label="Comparison Result", lines=20, interactive=False)

        def refresh_both(token):
            result = fetch_documents(token)
            return result, result

        compare_refresh.click(refresh_both, inputs=[token_state], outputs=[compare_doc1, compare_doc2])
        compare_btn.click(compare_docs, inputs=[compare_doc1, compare_doc2, token_state], outputs=[compare_output])
