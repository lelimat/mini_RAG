"""Canonical Bible book metadata and normalization helpers."""

from __future__ import annotations

import re
from collections import defaultdict

OLD_TESTAMENT_BOOKS = [
    "Genesis",
    "Exodus",
    "Leviticus",
    "Numbers",
    "Deuteronomy",
    "Joshua",
    "Judges",
    "Ruth",
    "1 Samuel",
    "2 Samuel",
    "1 Kings",
    "2 Kings",
    "1 Chronicles",
    "2 Chronicles",
    "Ezra",
    "Nehemiah",
    "Esther",
    "Job",
    "Psalms",
    "Proverbs",
    "Ecclesiastes",
    "Song of Solomon",
    "Isaiah",
    "Jeremiah",
    "Lamentations",
    "Ezekiel",
    "Daniel",
    "Hosea",
    "Joel",
    "Amos",
    "Obadiah",
    "Jonah",
    "Micah",
    "Nahum",
    "Habakkuk",
    "Zephaniah",
    "Haggai",
    "Zechariah",
    "Malachi",
]

NEW_TESTAMENT_BOOKS = [
    "Matthew",
    "Mark",
    "Luke",
    "John",
    "Acts",
    "Romans",
    "1 Corinthians",
    "2 Corinthians",
    "Galatians",
    "Ephesians",
    "Philippians",
    "Colossians",
    "1 Thessalonians",
    "2 Thessalonians",
    "1 Timothy",
    "2 Timothy",
    "Titus",
    "Philemon",
    "Hebrews",
    "James",
    "1 Peter",
    "2 Peter",
    "1 John",
    "2 John",
    "3 John",
    "Jude",
    "Revelation",
]

ALL_BOOKS = OLD_TESTAMENT_BOOKS + NEW_TESTAMENT_BOOKS
BOOK_TO_TESTAMENT = {book: "Old" for book in OLD_TESTAMENT_BOOKS} | {
    book: "New" for book in NEW_TESTAMENT_BOOKS
}


def _normalize_book_key(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"\s+", " ", value)
    return value


BOOK_ALIASES = {
    "song of songs": "Song of Solomon",
    "songs": "Song of Solomon",
    "psalm": "Psalms",
}

CANONICAL_BOOK_LOOKUP = {
    _normalize_book_key(book): book for book in ALL_BOOKS
} | {_normalize_book_key(alias): canonical for alias, canonical in BOOK_ALIASES.items()}


def canonicalize_book_name(book: str) -> str:
    """Return a canonical book name or raise a ValueError."""
    normalized = _normalize_book_key(book)
    try:
        return CANONICAL_BOOK_LOOKUP[normalized]
    except KeyError as exc:
        raise ValueError(f"Unknown Bible book: {book}") from exc


def get_testament(book: str) -> str:
    """Return the testament for a canonical book name."""
    canonical = canonicalize_book_name(book)
    return BOOK_TO_TESTAMENT[canonical]


def books_grouped_by_testament() -> dict[str, list[str]]:
    """Return all canonical books grouped by testament."""
    grouped: defaultdict[str, list[str]] = defaultdict(list)
    for book in ALL_BOOKS:
        grouped[BOOK_TO_TESTAMENT[book]].append(book)
    return dict(grouped)


BOOK_MATCH_PATTERN = re.compile(
    r"^(?P<book>"
    + "|".join(re.escape(book) for book in sorted(ALL_BOOKS, key=len, reverse=True))
    + r")\s+(?P<chapter>\d+):(?P<verse>\d+)\s+(?P<text>.+)$"
)
