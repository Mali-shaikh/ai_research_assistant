from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.api.auth_routes import router as auth_router
from app.api.document_routes import router as document_router
from app.api.chat_routes import router as chat_router
from app.core.config import settings
from app.db.init_db import init_db
from app.db.session import engine

init_db()

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(document_router)
app.include_router(chat_router)

@app.get("/")
def root():
    return {"message": settings.APP_NAME, "environment": settings.APP_ENV}

@app.get("/health")
def health():
    db_ok = True
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        db_ok = False
    return {"status": "ok", "database": db_ok}
