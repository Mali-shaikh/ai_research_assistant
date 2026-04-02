import os
import requests
import gradio as gr

API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")

# ─── API helpers ─────────────────────────────────────────────────────────────

def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"} if token else {}


def register(full_name, email, password):
    r = requests.post(
        f"{API_BASE}/api/auth/register",
        json={"full_name": full_name, "email": email, "password": password},
        timeout=60,
    )
    try:
        return r.json()
    except Exception:
        return {"detail": r.text}


def login(email, password):
    r = requests.post(
        f"{API_BASE}/api/auth/login",
        json={"email": email, "password": password},
        timeout=60,
    )
    if r.status_code == 200:
        return r.json()["access_token"], "✅ Login successful."
    try:
        return "", f"❌ {r.json().get('detail', 'Login failed.')}"
    except Exception:
        return "", f"❌ {r.text}"


def fetch_documents(token):
    """Return updated dropdown choices for user's documents."""
    if not token:
        return gr.update(choices=[], value=None)
    r = requests.get(
        f"{API_BASE}/api/documents",
        headers=auth_headers(token),
        timeout=60,
    )
    if r.status_code != 200:
        return gr.update(choices=[], value=None)
    docs = r.json()
    choices = [f"{doc['id']} – {doc['title']}" for doc in docs]
    return gr.update(choices=choices, value=choices[0] if choices else None)


def parse_doc_id(doc_label) -> int | None:
    if not doc_label:
        return None
    try:
        return int(str(doc_label).split(" – ", 1)[0])
    except ValueError:
        return None


def upload_document(file_path: str | None, token: str):
    """Upload a document to the backend.

    Gradio 5 passes the temp file path as a plain string.
    """
    if not token:
        return "⚠️ Please login first.", gr.update()
    if file_path is None:
        return "⚠️ Please choose a file.", gr.update()

    # Gradio 5: file_path is a str (temp file path)
    filename = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        r = requests.post(
            f"{API_BASE}/api/documents/upload",
            files={"file": (filename, f)},
            headers=auth_headers(token),
            timeout=180,
        )
    if r.status_code != 200:
        try:
            detail = r.json().get("detail", r.text)
        except Exception:
            detail = r.text
        return f"❌ Upload failed: {detail}", fetch_documents(token)

    data = r.json()
    title = data.get("document", {}).get("title", filename)
    return f"✅ Uploaded: {title}", fetch_documents(token)


def send_chat(message: str, history: list, token: str, selected_doc) -> str:
    if not token:
        return "⚠️ Please login first."
    payload = {"message": message, "document_id": parse_doc_id(selected_doc)}
    r = requests.post(
        f"{API_BASE}/api/chat",
        json=payload,
        headers=auth_headers(token),
        timeout=180,
    )
    try:
        data = r.json()
    except Exception:
        return f"❌ Error: {r.text}"
    if r.status_code != 200:
        return f"❌ Error: {data.get('detail', 'Request failed.')}"
    return data["response"]


def compare_docs(doc1, doc2, token: str) -> str:
    if not token:
        return "⚠️ Please login first."
    if not doc1 or not doc2:
        return "⚠️ Please select both documents."
    payload = {"doc1_id": parse_doc_id(doc1), "doc2_id": parse_doc_id(doc2)}
    r = requests.post(
        f"{API_BASE}/api/compare",
        json=payload,
        headers=auth_headers(token),
        timeout=180,
    )
    try:
        data = r.json()
    except Exception:
        return f"❌ Error: {r.text}"
    if r.status_code != 200:
        return f"❌ Error: {data.get('detail', 'Comparison failed.')}"
    return data["comparison_result"]


# ─── UI ──────────────────────────────────────────────────────────────────────

DESCRIPTION = """
# 🔬 AI Academic Research Assistant
**Upload** research papers · **Chat** with them · **Compare** two papers · **Extract** citations
"""

THEME = gr.themes.Soft(primary_hue="indigo", secondary_hue="slate")
CSS = """
.app-header { text-align: center; margin-bottom: 8px; }
.status-box textarea { font-weight: 600; }
"""

with gr.Blocks(
    title="AI Academic Research Assistant",
) as demo:
    token_state = gr.State("")

    gr.Markdown(DESCRIPTION, elem_classes="app-header")

    # ── Auth ──────────────────────────────────────────────────────────────────
    with gr.Tab("🔐 Auth"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Register")
                reg_name     = gr.Textbox(label="Full Name", placeholder="Jane Doe")
                reg_email    = gr.Textbox(label="Email", placeholder="jane@example.com")
                reg_password = gr.Textbox(label="Password", type="password")
                reg_btn      = gr.Button("Register", variant="primary")
                reg_output   = gr.JSON(label="Response")

            with gr.Column():
                gr.Markdown("### Login")
                login_email    = gr.Textbox(label="Email", placeholder="jane@example.com")
                login_password = gr.Textbox(label="Password", type="password")
                login_btn      = gr.Button("Login", variant="primary")
                login_status   = gr.Textbox(
                    label="Login Status",
                    interactive=False,
                    elem_classes="status-box",
                )

        reg_btn.click(
            register,
            inputs=[reg_name, reg_email, reg_password],
            outputs=reg_output,
        )
        login_btn.click(
            login,
            inputs=[login_email, login_password],
            outputs=[token_state, login_status],
        )

    # ── Upload & Documents ────────────────────────────────────────────────────
    with gr.Tab("📄 Upload & Documents"):
        with gr.Row():
            with gr.Column(scale=1):
                file_input   = gr.File(label="Upload PDF / DOCX / TXT / MD")
                upload_btn   = gr.Button("Upload Document", variant="primary")
                upload_status = gr.Textbox(
                    label="Upload Status",
                    interactive=False,
                    elem_classes="status-box",
                )

            with gr.Column(scale=1):
                doc_dropdown     = gr.Dropdown(label="Your Documents", choices=[], interactive=True)
                refresh_docs_btn = gr.Button("🔄 Refresh Documents")

        upload_btn.click(
            upload_document,
            inputs=[file_input, token_state],
            outputs=[upload_status, doc_dropdown],
        )
        refresh_docs_btn.click(
            fetch_documents,
            inputs=[token_state],
            outputs=[doc_dropdown],
        )

    # ── Chat ──────────────────────────────────────────────────────────────────
    with gr.Tab("💬 Chat"):
        with gr.Row():
            chat_doc_dropdown = gr.Dropdown(
                label="Select Document (optional — leave blank for free chat)",
                choices=[],
                interactive=True,
                scale=4,
            )
            refresh_chat_btn = gr.Button("🔄 Refresh", scale=1)

        chatbot   = gr.Chatbot(height=420, label="Conversation")
        msg_input = gr.Textbox(
            placeholder='Type a message — e.g. "Summarize this paper" or "What is the methodology?"',
            label="Your message",
            lines=2,
        )
        with gr.Row():
            send_btn  = gr.Button("Send ▶", variant="primary", scale=3)
            clear_btn = gr.Button("Clear 🗑", scale=1)

        def respond(message, chat_history, token, selected_doc):
            if not message.strip():
                return "", chat_history
            reply = send_chat(message, chat_history, token, selected_doc)
            chat_history.append({"role": "user", "content": message})
            chat_history.append({"role": "assistant", "content": reply})
            return "", chat_history

        send_btn.click(
            respond,
            inputs=[msg_input, chatbot, token_state, chat_doc_dropdown],
            outputs=[msg_input, chatbot],
        )
        msg_input.submit(
            respond,
            inputs=[msg_input, chatbot, token_state, chat_doc_dropdown],
            outputs=[msg_input, chatbot],
        )
        clear_btn.click(lambda: [], outputs=chatbot)
        refresh_chat_btn.click(
            fetch_documents,
            inputs=[token_state],
            outputs=[chat_doc_dropdown],
        )

    # ── Compare ───────────────────────────────────────────────────────────────
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

        compare_refresh.click(
            refresh_both,
            inputs=[token_state],
            outputs=[compare_doc1, compare_doc2],
        )
        compare_btn.click(
            compare_docs,
            inputs=[compare_doc1, compare_doc2, token_state],
            outputs=[compare_output],
        )


if __name__ == "__main__":
    demo.launch(theme=THEME, css=CSS)
