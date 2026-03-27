"""Shared application service helpers."""

from __future__ import annotations

from app.answer import generate_answer
from app.retrieve import retrieve_verses
from app.schemas import AskResponse
from app.vector_store import get_collection


def ask_bible_question(
    question: str,
    testament: str = "Both",
    books: list[str] | None = None,
    top_k: int = 5,
) -> AskResponse:
    """Run retrieval and grounded answering for a Bible question."""
    collection = get_collection()
    passages = retrieve_verses(
        vector_store=collection,
        question=question,
        testament=testament,
        books=books,
        top_k=top_k,
    )
    answer, references = generate_answer(
        question=question,
        verses=passages,
        testament=testament,
        books=books,
    )
    return AskResponse(
        answer=answer,
        references=references,
        retrieved_passages=passages,
        applied_filters={
            "testament": testament,
            "books": books or [],
            "top_k": top_k,
        },
    )
