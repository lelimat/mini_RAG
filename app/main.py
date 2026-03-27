"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException

from app.bible_books import books_grouped_by_testament
from app.config import settings
from app.ingest import ingest_bible
from app.schemas import (
    AskRequest,
    AskResponse,
    BooksResponse,
    HealthResponse,
    IndexRequest,
    IndexResponse,
)
from app.service import ask_bible_question
from app.vector_store import index_bible

app = FastAPI(title="Bible RAG", version="0.1.0")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/books", response_model=BooksResponse)
def books() -> BooksResponse:
    grouped = books_grouped_by_testament()
    return BooksResponse(**grouped)


@app.post("/index", response_model=IndexResponse)
def index(request: IndexRequest) -> IndexResponse:
    try:
        if request.force_reparse or not settings.parsed_bible_path.exists():
            ingest_bible(force_download=True)
        indexed_count = index_bible(rebuild=request.rebuild, force_reparse=request.force_reparse)
        return IndexResponse(
            status="indexed",
            indexed_count=indexed_count,
            collection_name=settings.collection_name,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    try:
        return ask_bible_question(
            question=request.question,
            testament=request.testament,
            books=request.books,
            top_k=request.top_k,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
