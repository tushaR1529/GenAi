# app/main.py
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.llm import generate_chat_response
from app.records import get_by_id, load_records
from app.smart_search import SmartSearch

app = FastAPI(
    title="VidyaLoan API",
    description="AI-powered education loan assistance API for Indian government schemes",
    version="0.1.0",
)

QUESTIONS_FILE = Path("data/questions.json")


def get_search_engine() -> SmartSearch:
    return SmartSearch()


class Question(BaseModel):
    question: str


class ChatRequest(BaseModel):
    message: Optional[str] = None
    question: Optional[str] = None
    prompt_version: Optional[str] = "v1"


class ChatResponse(BaseModel):
    answer: str
    confidence: float
    follow_up: str


@app.get("/")
def root():
    return {"message": "VidyaLoan API is running", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok", "records": len(load_records())}


@app.get("/records")
def get_records(limit: int = 10):
    all_recs = load_records()
    if limit <= 0:
        return []
    return all_recs[:limit]


@app.get("/records/{record_id}")
def record_by_id(record_id: int):
    record = get_by_id(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@app.get("/search")
def search(q: str, top_k: int = 5):
    engine = get_search_engine()
    results = engine.search(q, top_k=top_k)
    return {"query": q, "results": results}


@app.post("/questions")
def post_question(item: Question):
    text = item.question.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    saved = []
    if QUESTIONS_FILE.exists():
        try:
            saved = json.loads(QUESTIONS_FILE.read_text(encoding="utf-8"))
        except Exception:
            saved = []

    entry = {
        "id": len(saved) + 1,
        "question": text,
        "time": datetime.now().isoformat(),
    }
    saved.append(entry)
    QUESTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    QUESTIONS_FILE.write_text(
        json.dumps(saved, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return entry


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    query = (req.message or req.question or "").strip()
    if not query:
        raise HTTPException(status_code=400, detail="Message or question cannot be empty")

    version = req.prompt_version if req.prompt_version in ("v1", "v2") else "v1"
    response = generate_chat_response(query, prompt_version=version)
    return response
