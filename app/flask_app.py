"""Minimal Flask web UI for Bible RAG."""

from __future__ import annotations

from flask import Flask, render_template, request

from app.bible_books import books_grouped_by_testament
from app.config import settings
from app.schemas import AskRequest
from app.service import ask_bible_question

flask_app = Flask(__name__, template_folder="templates")


@flask_app.get("/")
def index():
    grouped_books = books_grouped_by_testament()
    return render_template(
        "index.html",
        grouped_books=grouped_books,
        default_top_k=settings.default_top_k,
        result=None,
        form_data={
            "question": "",
            "testament": "Both",
            "books": [],
            "top_k": settings.default_top_k,
        },
        error=None,
    )


@flask_app.post("/")
def ask():
    grouped_books = books_grouped_by_testament()

    question = request.form.get("question", "").strip()
    testament = request.form.get("testament", "Both")
    books = request.form.getlist("books")
    top_k_raw = request.form.get("top_k", str(settings.default_top_k))

    form_data = {
        "question": question,
        "testament": testament,
        "books": books,
        "top_k": top_k_raw,
    }

    try:
        validated = AskRequest(
            question=question,
            testament=testament,
            books=books or None,
            top_k=int(top_k_raw),
        )
        result = ask_bible_question(
            question=validated.question,
            testament=validated.testament,
            books=validated.books,
            top_k=validated.top_k,
        )
        return render_template(
            "index.html",
            grouped_books=grouped_books,
            default_top_k=settings.default_top_k,
            result=result.model_dump(),
            form_data={
                "question": validated.question,
                "testament": validated.testament,
                "books": validated.books or [],
                "top_k": validated.top_k,
            },
            error=None,
        )
    except Exception as exc:
        return render_template(
            "index.html",
            grouped_books=grouped_books,
            default_top_k=settings.default_top_k,
            result=None,
            form_data=form_data,
            error=str(exc),
        )


if __name__ == "__main__":
    flask_app.run(debug=True)
