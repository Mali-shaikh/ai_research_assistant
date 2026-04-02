# AI Academic Research Assistant — Complete Production Starter

A complete final-year project starter using:

- Python
- FastAPI
- Gradio
- PostgreSQL
- OpenAI API
- Agent-based routing
- JWT authentication

## Features

- User registration and login
- Upload PDF, TXT, MD, DOCX
- Per-user document ownership
- Summarization
- Question answering
- Citation extraction
- Document comparison
- PostgreSQL persistence
- Gradio frontend
- Sample fine-tuning dataset
- Health check and test starter

## Project Structure

```text
ai_research_assistant_complete/
├── app/
│   ├── agents/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── frontend/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── utils/
├── data/fine_tune/
├── sql/
├── tests/
├── requirements.txt
├── .env.example
└── run.py
```

## Setup

### 1. Create database

```sql
CREATE DATABASE research_db;
```

### 2. Install dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment

Copy `.env.example` to `.env` and set values.

### 4. Run backend

```bash
python run.py
```

### 5. Run Gradio frontend

```bash
python -m app.frontend.gradio_ui
```

## API Endpoints

- `GET /health`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/documents/upload`
- `GET /api/documents`
- `POST /api/chat`
- `POST /api/compare`

## Notes

- Tables are auto-created on startup.
- This is a strong submission-ready starter.
- For live deployment, add HTTPS, background task queue, and stronger rate limiting.

## Fine-Tuning

Sample JSONL is included in `data/fine_tune/training_data.jsonl`.

## Testing

```bash
pytest
```
