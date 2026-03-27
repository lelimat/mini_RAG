"""Answer generation grounded in retrieved Bible passages."""

from __future__ import annotations

import re
from collections import Counter

import requests

from app.config import settings
from app.schemas import RetrievedPassage

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "did",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "was",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "with",
}


def build_answer_prompt(question: str, verses: list[RetrievedPassage], scope_description: str) -> str:
    """Build a grounded prompt for an optional LLM call."""
    context = "\n".join(f"{verse.reference}: {verse.text}" for verse in verses)
    return (
        "You are answering Bible questions strictly from supplied King James Bible passages.\n"
        "Rules:\n"
        "1. Answer only from the provided context.\n"
        "2. Cite verse references that support the answer.\n"
        "3. Respect the selected scope exactly.\n"
        "4. If the answer is not supported by the context or selected scope, say so clearly.\n"
        "5. Do not use outside knowledge or speculation.\n\n"
        f"Selected scope: {scope_description}\n"
        f"Question: {question}\n\n"
        f"Context:\n{context}\n\n"
        "Return a concise answer with references."
    )


def _tokenize(text: str) -> list[str]:
    return [token for token in re.findall(r"[A-Za-z']+", text.lower()) if token not in STOPWORDS]


def _extractive_fallback_answer(question: str, verses: list[RetrievedPassage], scope_description: str) -> str:
    """Create a conservative extractive answer without an LLM."""
    if not verses:
        return (
            f"The selected scope ({scope_description}) did not return any supporting verses, "
            "so the question cannot be answered from the retrieved context."
        )

    question_tokens = _tokenize(question)
    if not question_tokens:
        references = ", ".join(verse.reference for verse in verses[:3])
        return f"The top retrieved verses are {references}, but the question was too broad to summarize safely."

    token_counts = Counter(question_tokens)
    scored: list[tuple[int, RetrievedPassage]] = []
    for verse in verses:
        verse_tokens = set(_tokenize(verse.text))
        overlap = sum(token_counts[token] for token in verse_tokens if token in token_counts)
        scored.append((overlap, verse))

    scored.sort(key=lambda item: (item[0], item[1].score or 0.0), reverse=True)
    best_overlap, best_verse = scored[0]

    if best_overlap == 0:
        return (
            f"The retrieved verses in the selected scope ({scope_description}) do not directly support "
            "a confident answer to this question."
        )

    supporting = [verse.reference for overlap, verse in scored[:3] if overlap > 0]
    support_str = ", ".join(dict.fromkeys(supporting))
    return f"Based on the retrieved passages, {best_verse.text} ({support_str})."


def _llm_answer(prompt: str) -> str:
    """Call an OpenAI-compatible chat endpoint."""
    if not settings.llm_api_key:
        raise RuntimeError("LLM API key is not configured.")

    response = requests.post(
        f"{settings.llm_api_base}/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.llm_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": settings.llm_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
        },
        timeout=settings.llm_timeout_seconds,
    )
    response.raise_for_status()
    payload = response.json()
    return payload["choices"][0]["message"]["content"].strip()


def generate_answer(
    question: str,
    verses: list[RetrievedPassage],
    testament: str,
    books: list[str] | None = None,
    use_llm: bool | None = None,
) -> tuple[str, list[str]]:
    """Generate an answer and list of cited references."""
    scope_description = f"testament={testament}, books={books or 'All'}"
    references = list(dict.fromkeys(verse.reference for verse in verses))

    if not verses:
        return (
            f"No verses were retrieved for the selected scope ({scope_description}), so the question "
            "is not supported by the available context.",
            [],
        )

    if use_llm is None:
        use_llm = bool(settings.llm_api_key)

    if use_llm:
        prompt = build_answer_prompt(question=question, verses=verses, scope_description=scope_description)
        try:
            return _llm_answer(prompt), references
        except requests.RequestException:
            pass

    return _extractive_fallback_answer(question, verses, scope_description), references
