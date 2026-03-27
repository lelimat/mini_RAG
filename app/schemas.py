"""Shared request and response schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.bible_books import canonicalize_book_name
from app.config import settings

Testament = Literal["Old", "New", "Both"]


class VerseMetadata(BaseModel):
    reference: str
    book: str
    chapter: int
    verse: int
    testament: Literal["Old", "New"]


class VerseRecord(BaseModel):
    id: str
    document: str
    metadata: VerseMetadata


class RetrievedPassage(BaseModel):
    reference: str
    book: str
    chapter: int
    verse: int
    testament: Literal["Old", "New"]
    text: str
    distance: float | None = None
    score: float | None = None


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    testament: Testament = "Both"
    books: list[str] | None = None
    top_k: int = Field(default=settings.default_top_k, ge=1, le=25)

    @field_validator("books")
    @classmethod
    def validate_books(cls, books: list[str] | None) -> list[str] | None:
        if books is None:
            return None
        return [canonicalize_book_name(book) for book in books]


class AskResponse(BaseModel):
    answer: str
    references: list[str]
    retrieved_passages: list[RetrievedPassage]
    applied_filters: dict[str, object]


class IndexRequest(BaseModel):
    rebuild: bool = False
    force_reparse: bool = False


class IndexResponse(BaseModel):
    status: str
    indexed_count: int
    collection_name: str


class HealthResponse(BaseModel):
    status: str


class BooksResponse(BaseModel):
    Old: list[str]
    New: list[str]
