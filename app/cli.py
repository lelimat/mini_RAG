"""Command line interface for Bible RAG."""

from __future__ import annotations

import argparse
import json

from app.config import settings
from app.ingest import ingest_bible
from app.service import ask_bible_question
from app.vector_store import index_bible


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bible RAG CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="Download and parse the KJV Bible")
    ingest_parser.add_argument(
        "--reuse",
        action="store_true",
        help="Reuse the existing parsed JSONL file if present",
    )

    index_parser = subparsers.add_parser("index", help="Index parsed verses into Chroma")
    index_parser.add_argument("--rebuild", action="store_true", help="Rebuild the Chroma collection")
    index_parser.add_argument(
        "--force-reparse",
        action="store_true",
        help="Redownload and reparse the source text before indexing",
    )

    ask_parser = subparsers.add_parser("ask", help="Ask a Bible question")
    ask_parser.add_argument("--question", required=True, help="The question to ask")
    ask_parser.add_argument(
        "--testament",
        default="Both",
        choices=["Old", "New", "Both"],
        help="Limit retrieval to a testament",
    )
    ask_parser.add_argument("--books", nargs="*", default=None, help="Limit retrieval to specific books")
    ask_parser.add_argument("--top-k", type=int, default=settings.default_top_k, help="Number of passages to retrieve")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "ingest":
        verses = ingest_bible(force_download=not args.reuse)
        print(f"Parsed {len(verses)} verses into {settings.parsed_bible_path}")
        return

    if args.command == "index":
        if args.force_reparse or not settings.parsed_bible_path.exists():
            ingest_bible(force_download=True)
        count = index_bible(rebuild=args.rebuild, force_reparse=args.force_reparse)
        print(f"Indexed {count} verses into collection '{settings.collection_name}'")
        return

    if args.command == "ask":
        result = ask_bible_question(
            question=args.question,
            testament=args.testament,
            books=args.books,
            top_k=args.top_k,
        )
        print(json.dumps(result.model_dump(), indent=2))
        return

    parser.error("Unknown command")


if __name__ == "__main__":
    main()
