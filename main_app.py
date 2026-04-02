"""
main_app.py — Hugging Face Spaces entry point.
Initialises the database, then launches the Gradio UI directly.
No threading, no background FastAPI server needed.
The Gradio UI calls backend functions directly (no HTTP).
"""

# 1. Init database tables (SQLite auto-created in /app/research.db)
from app.db.init_db import init_db
init_db()

# 2. Import and launch the Gradio app
from app.frontend.gradio_ui import demo

demo.launch(server_name="0.0.0.0", server_port=7860)
