"""Chroma vector store integration."""

from __future__ import annotations

from typing import Any

from app.config import settings
from app.ingest import ingest_bible, load_verses_jsonl


class SentenceTransformerEmbeddingFunction:
    """Small adapter around sentence-transformers for Chroma."""

    def __init__(self, model_name: str) -> None:
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name)

    def __call__(self, input: list[str]) -> list[list[float]]:
        return self.embed_documents(input)

    def embed_documents(self, input: list[str]) -> list[list[float]]:
        """Embed documents for storage in Chroma."""
        embeddings = self.model.encode(input, normalize_embeddings=True)
        return embeddings.tolist()

    def embed_query(self, input: str | list[str]) -> list[float] | list[list[float]]:
        """Embed one or more query strings for Chroma retrieval."""
        if isinstance(input, str):
            return self.model.encode(input, normalize_embeddings=True).tolist()
        return self.embed_documents(input)

    def name(self) -> str:
        """Return a stable embedding function name for Chroma internals."""
        return f"sentence_transformer:{settings.embedding_model_name}"


def get_chroma_client() -> Any:
    """Create a persistent Chroma client."""
    import chromadb

    settings.ensure_directories()
    return chromadb.PersistentClient(path=str(settings.chroma_path))


def get_collection() -> Any:
    """Get or create the configured Chroma collection."""
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=settings.collection_name,
        embedding_function=SentenceTransformerEmbeddingFunction(settings.embedding_model_name),
        metadata={"description": "King James Bible verse embeddings"},
    )


def rebuild_collection() -> Any:
    """Drop and recreate the collection."""
    client = get_chroma_client()
    try:
        client.delete_collection(settings.collection_name)
    except Exception:
        pass
    return get_collection()


def index_bible(rebuild: bool = False, force_reparse: bool = False) -> int:
    """Index parsed Bible verses into Chroma."""
    collection = rebuild_collection() if rebuild else get_collection()

    existing_count = collection.count()
    if existing_count > 0 and not rebuild:
        return existing_count

    verses = ingest_bible(force_download=True) if force_reparse else load_verses_jsonl()

    batch_size = 256
    for start in range(0, len(verses), batch_size):
        batch = verses[start : start + batch_size]
        collection.add(
            ids=[verse.id for verse in batch],
            documents=[verse.document for verse in batch],
            metadatas=[verse.metadata.model_dump() for verse in batch],
        )

    return collection.count()
