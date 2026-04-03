---
title: AI Academic Research Assistant
emoji: 🔬
colorFrom: indigo
colorTo: blue
sdk: gradio
sdk_version: "5.15.0"
python_version: "3.10"
app_file: main_app.py
pinned: false
---

# 🔬 AI Academic Research Assistant — Comprehensive Technical Overview

This project is a sophisticated AI-driven platform designed to assist researchers in analyzing academic papers. It leverages Large Language Models (LLMs) to perform complex tasks like summarization, comparative analysis, and structured Q&A.

## 🌟 Enhanced Features

- **Multi-Format Extraction**: Supports PDF, DOCX, TXT, and Markdown files.
- **Intelligent Agents**: 
  - **Summarizer**: Condenses long research papers into key takeaways.
  - **Citation Agent**: Extracts references and identifies primary authors.
  - **QA Agent**: Context-aware answering based on specific document content.
  - **Comparison Agent**: Side-by-side analysis of two different research papers.
- **Secure Authentication**: JWT-based user registration and login system.
- **Per-User Isolation**: Documents are securely tied to individual user accounts.
- **Cloud-Ready**: Optimized for deployment on Hugging Face Spaces.

## 🛠️ Technology Stack & Tools

### Core Technologies
- **Python 3.10**: The backbone of the application.
- **Gradio 5.15.0**: Used for the interactive, premium web interface.
- **Google Gemini 3.1 Pro**: The primary LLM engine for all AI operations.
- **SQLite & SQLAlchemy**: Efficient local database storage for users and document metadata.

### Libraries & Frameworks
- **File Processing**: `PyPDF2` (PDFs), `python-docx` (Word files).
- **Security**: `passlib` (BCrypt hashing), `python-jose` (JSON Web Tokens).
- **Backend**: `FastAPI` (available for API extension), `Uvicorn` (ASGI server).
- **Environment**: `python-dotenv` for managing API keys and secrets.

---

## 🧪 Quick Start with Samples

To test the application immediately:
1. Go to the **Upload & Documents** tab.
2. Navigate to the `samples/` directory in this project.
3. You will find several high-quality research papers prepared for you:
   - `Cultural Diversity in Team Performance.pdf`
   - `STEM Education in Underrepresented.pdf`
   - `Sleep Deprivation and Academic Performance.pdf`
   - `Social Media and Mental Health.pdf`
   - `Virtual Reality in Cognitive Rehabilitation.pdf`
   - `sample_ai_ethics.txt` (Text version)
   - `sample_climate_change.txt` (Text version)
4. Upload any of these and use the **Chat** and **Compare** tabs to see the AI in action!

---

## 📂 Project Preparation & Structure

The project is architected using a modular design to ensure scalability and maintainability.

### Workflow involved in Preparation:
1. **DB Schema Design**: Defined SQLAlchemy models for `User` and `Document` to handle relationships.
2. **Agent Orchestration**: Developed specialized scripts in `app/agents/` to handle different AI prompts and logic.
3. **Frontend Implementation**: Built a multi-tabbed Gradio interface in `app/frontend/gradio_ui.py` with custom CSS for a premium feel.
4. **Hugging Face Optimization**: Created `main_app.py` as a lightweight entry point that initializes the DB and launches the UI without needing complex threading.
5. **Security Integration**: Implemented password hashing and JWT token generation to ensure data privacy.

### Key Modules:
- `app/agents/`: Logic for AI personalities (Summarizer, QA, etc.).
- `app/services/`: Core business logic (auth, document processing, Gemini integration).
- `app/db/`: Database initialization and session management.
- `app/frontend/`: The User Interface definitions and theme tokens.

---

## 🚀 Deployment to Hugging Face

To deploy this project successfully, the following steps were taken:
1. **Environment Config**: Created a `requirements.txt` specifically for the HF environment.
2. **Metadata Header**: Included a YAML frontmatter in `README.md` to define the Gradio SDK and Python version.
3. **Database Initialization**: Added `init_db()` in the main entry point to ensure tables are ready upon container startup.
4. **Secret Management**: Configured `GOOGLE_API_KEY` as a Space Secret on Hugging Face.

---

## 📝 Future Scope
- **Vector Database**: Transitioning to ChromaDB or FAISS for handling extremely large document libraries.
- **Collaborative Features**: Allowing researchers to share document libraries for group projects.
- **Real-time Collaboration**: Integration with WebSockets for multi-user chat sessions.

---
*Created for Final Year Project Submission | Academic Research Assistant v1.0*
