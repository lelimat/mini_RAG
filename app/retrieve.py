"""Filtered verse retrieval helpers."""

from __future__ import annotations

from typing import Any

from app.bible_books import canonicalize_book_name
from app.schemas import RetrievedPassage, Testament


def build_retrieval_filter(
    testament: Testament = "Both", books: list[str] | None = None
) -> dict[str, Any] | None:
    """Build a Chroma metadata filter from testament and book inputs."""
    conditions: list[dict[str, Any]] = []

    if testament in {"Old", "New"}:
        conditions.append({"testament": testament})

    if books:
        canonical_books = [canonicalize_book_name(book) for book in books]
        if len(canonical_books) == 1:
            conditions.append({"book": canonical_books[0]})
        else:
            conditions.append({"book": {"$in": canonical_books}})

    if not conditions:
        return None
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


def format_query_results(results: dict[str, Any]) -> list[RetrievedPassage]:
    """Convert raw Chroma results into a stable response shape."""
    documents = results.get("documents", [[]])
    metadatas = results.get("metadatas", [[]])
    distances = results.get("distances", [[]])

    passages: list[RetrievedPassage] = []
    for index, document in enumerate(documents[0] if documents else []):
        metadata = metadatas[0][index]
        distance = distances[0][index] if distances and distances[0] else None
        score = None if distance is None else 1 / (1 + float(distance))

        passages.append(
            RetrievedPassage(
                reference=metadata["reference"],
                book=metadata["book"],
                chapter=int(metadata["chapter"]),
                verse=int(metadata["verse"]),
                testament=metadata["testament"],
                text=document,
                distance=float(distance) if distance is not None else None,
                score=score,
            )
        )
    return passages


def retrieve_verses(
    vector_store: Any,
    question: str,
    testament: Testament = "Both",
    books: list[str] | None = None,
    top_k: int = 5,
) -> list[RetrievedPassage]:
    """Retrieve the most relevant verses under the requested scope."""
    where = build_retrieval_filter(testament=testament, books=books)
    results = vector_store.query(
        query_texts=[question],
        n_results=top_k,
        where=where,
        include=["documents", "metadatas", "distances"],
    )
    return format_query_results(results)
