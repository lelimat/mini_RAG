# Bible RAG

A minimal, local Retrieval-Augmented Generation (RAG) project for Bible question answering over the King James Version (KJV). It downloads the KJV text, parses it into verse-level records, stores verse embeddings in Chroma, retrieves verses with testament and book filters, and answers questions from retrieved Bible context only.

The project is intentionally simple:

- Python 3.11+
- Chroma for a local persistent vector database
- sentence-transformers for embeddings
- FastAPI for a small local API
- Flask for a simple browser UI
- A CLI for ingestion, indexing, and question answering
- A retrieval-only fallback that works without an LLM API key

## Features

- Downloads the KJV Bible from [openbible.com](https://openbible.com/textfiles/kjv.txt)
- Parses verse-level records with structured metadata
- Stores vectors in a persistent Chroma collection
- Supports retrieval filters for:
  - `Old`
  - `New`
  - `Both`
  - one or more specific books
- Returns:
  - an answer
  - verse references
  - retrieved passages
  - applied filters
- Uses a grounded answer prompt in LLM mode
- Falls back to a local extractive answer mode when no LLM key is configured

## Project Structure

```text
bible_rag/
  README.md
  requirements.txt
  .env.example
  app/
    __init__.py
    config.py
    bible_books.py
    schemas.py
    ingest.py
    vector_store.py
    retrieve.py
    answer.py
    service.py
    main.py
    flask_app.py
    cli.py
    templates/
      index.html
  data/
    .gitkeep
  chroma_db/
    .gitkeep
  tests/
    test_parsing.py
    test_filters.py
    test_retrieval.py
```

## Setup

1. Create and activate a virtual environment:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Optionally create a local environment file:

```bash
cp .env.example .env
```

## Indexing the Bible

First download and parse the Bible:

```bash
python -m app.cli ingest
```

Then build the Chroma index:

```bash
python -m app.cli index
```

To rebuild from scratch:

```bash
python -m app.cli index --rebuild
```

## CLI Usage

Ask a question across the whole Bible:

```bash
python -m app.cli ask --question "Who built the ark?"
```

Ask only in the Old Testament:

```bash
python -m app.cli ask --question "Who built the ark?" --testament Old
```

Ask within specific books:

```bash
python -m app.cli ask --question "What does love suffer long?" --testament New --books "1 Corinthians"
```

Search more than one book:

```bash
python -m app.cli ask --question "What is the greatest commandment?" --books Matthew Mark Luke
```

## Running the API

Start the API locally:

```bash
uvicorn app.main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

List books by testament:

```bash
curl http://127.0.0.1:8000/books
```

Trigger indexing:

```bash
curl -X POST http://127.0.0.1:8000/index \
  -H "Content-Type: application/json" \
  -d '{"rebuild": false}'
```

Ask a question:

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Who built the ark?",
    "testament": "Old",
    "books": ["Genesis"],
    "top_k": 5
  }'
```

## Running the Flask Web UI

Start the browser-based UI:

```bash
flask --app app.flask_app run --debug
```

Then open:

```text
http://127.0.0.1:5000
```

The page lets you:

- enter a Bible question
- choose `Old`, `New`, or `Both`
- select one or more books
- choose `top_k`
- view the answer, references, and retrieved verses on the page

Example response shape:

```json
{
  "answer": "Based on the retrieved passages, Noah built the ark (Genesis 6:14, Genesis 6:22).",
  "references": ["Genesis 6:14", "Genesis 6:22"],
  "retrieved_passages": [
    {
      "reference": "Genesis 6:14",
      "book": "Genesis",
      "chapter": 6,
      "verse": 14,
      "testament": "Old",
      "text": "Make thee an ark of gopher wood; rooms shalt thou make in the ark...",
      "distance": 0.123,
      "score": 0.89
    }
  ],
  "applied_filters": {
    "testament": "Old",
    "books": ["Genesis"],
    "top_k": 5
  }
}
```

## LLM Mode

The project works without any LLM configuration.

If you provide an API key, the answerer can optionally call an OpenAI-compatible chat endpoint:

- `LLM_API_KEY`
- `LLM_MODEL`
- `LLM_API_BASE`

When LLM mode is enabled, the prompt explicitly instructs the model to:

- answer only from retrieved Bible context
- cite references
- say when the answer is not supported by the retrieved context
- respect selected testament and book filters

## Configuration

Environment variables are centralized in [app/config.py](/Users/leandrolima/Dropbox/github_repos/mini_RAG/app/config.py):

- `BIBLE_URL`
- `DATA_DIR`
- `PARSED_BIBLE_PATH`
- `CHROMA_PATH`
- `COLLECTION_NAME`
- `EMBEDDING_MODEL_NAME`
- `DEFAULT_TOP_K`
- `LLM_API_KEY`
- `LLM_MODEL`
- `LLM_API_BASE`
- `LLM_TIMEOUT_SECONDS`

## Tests

Run the lightweight tests with:

```bash
pytest
```

The tests cover:

- verse parsing
- testament and book filter construction
- retrieval result formatting

## Notes and Limitations

- The source text format is assumed to follow the common `Book Chapter:Verse Text` pattern used by the OpenBible KJV text file.
- The fallback answerer is intentionally conservative. It synthesizes directly from retrieved verses rather than attempting open-ended reasoning.
- Retrieval quality depends on embedding quality and the selected `top_k`.
- If filters exclude relevant verses, the system does not reach outside the chosen scope.
- This project is designed for local use and extension, not for production deployment.
