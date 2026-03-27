"""Download and parse the KJV Bible into verse-level records."""

from __future__ import annotations

import json
from pathlib import Path

import requests

from app.bible_books import BOOK_MATCH_PATTERN, canonicalize_book_name, get_testament
from app.config import settings
from app.schemas import VerseMetadata, VerseRecord


def download_bible_text(url: str | None = None, timeout: float = 60) -> str:
    """Download the raw KJV text file."""
    response = requests.get(url or settings.bible_url, timeout=timeout)
    response.raise_for_status()
    return response.text


def parse_verse_line(line: str) -> VerseRecord:
    """Parse a single verse line into a structured record."""
    stripped = line.strip()
    if not stripped:
        raise ValueError("Cannot parse an empty line.")

    match = BOOK_MATCH_PATTERN.match(stripped)
    if match is None:
        raise ValueError(f"Unrecognized verse line format: {line!r}")

    book = canonicalize_book_name(match.group("book"))
    chapter = int(match.group("chapter"))
    verse = int(match.group("verse"))
    text = match.group("text").strip()
    reference = f"{book} {chapter}:{verse}"

    return VerseRecord(
        id=reference.replace(" ", "_").replace(":", "_"),
        document=text,
        metadata=VerseMetadata(
            reference=reference,
            book=book,
            chapter=chapter,
            verse=verse,
            testament=get_testament(book),
        ),
    )


def parse_bible_text(raw_text: str) -> list[VerseRecord]:
    """Parse the source Bible text into verse records."""
    verses: list[VerseRecord] = []
    for line in raw_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            verse = parse_verse_line(stripped)
        except ValueError:
            # Skip lines that are not verse content, such as headers or blanks.
            continue
        verses.append(verse)

    if not verses:
        raise ValueError("No verses were parsed from the downloaded text.")
    return verses


def save_verses_jsonl(verses: list[VerseRecord], output_path: Path | None = None) -> Path:
    """Persist verse records for later indexing and reuse."""
    path = output_path or settings.parsed_bible_path
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file_obj:
        for verse in verses:
            file_obj.write(verse.model_dump_json())
            file_obj.write("\n")
    return path


def load_verses_jsonl(input_path: Path | None = None) -> list[VerseRecord]:
    """Load cached verse records from disk."""
    path = input_path or settings.parsed_bible_path
    if not path.exists():
        raise FileNotFoundError(f"Parsed Bible file not found: {path}")

    verses: list[VerseRecord] = []
    with path.open("r", encoding="utf-8") as file_obj:
        for line in file_obj:
            if not line.strip():
                continue
            verses.append(VerseRecord.model_validate(json.loads(line)))
    return verses


def ingest_bible(force_download: bool = True) -> list[VerseRecord]:
    """Download, parse, and persist the KJV Bible."""
    settings.ensure_directories()
    if not force_download and settings.parsed_bible_path.exists():
        return load_verses_jsonl()

    raw_text = download_bible_text()
    verses = parse_bible_text(raw_text)
    save_verses_jsonl(verses)
    return verses
