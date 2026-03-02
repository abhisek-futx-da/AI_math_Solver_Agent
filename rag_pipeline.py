"""RAG: chunk knowledge base, embed, store in ChromaDB, retrieve top-k."""
import os
import re
from pathlib import Path
from typing import List, Tuple
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from config import KNOWLEDGE_BASE_DIR, CHROMA_PERSIST_DIR, RAG_TOP_K

# Custom embedding function (sentence-transformers or other via llm_client)
from llm_client import get_embeddings

COLLECTION_NAME = "math_mentor_kb"
CHUNK_SIZE = 400
CHUNK_OVERLAP = 80


def _chunk_text(text: str, source: str) -> List[Tuple[str, str]]:
    """Split text into overlapping chunks. Returns list of (chunk_text, source)."""
    text = re.sub(r"\n+", "\n", text).strip()
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end]
        if end < len(text):
            last_space = chunk.rfind(" ")
            if last_space > CHUNK_SIZE // 2:
                chunk = chunk[: last_space + 1]
                end = start + last_space + 1
        chunks.append((chunk.strip(), source))
        start = end - CHUNK_OVERLAP
        if start >= len(text):
            break
    return chunks


def _load_knowledge_base() -> List[Tuple[str, str]]:
    """Load all .md/.txt from knowledge_base and return (chunk, source) list."""
    base = Path(KNOWLEDGE_BASE_DIR)
    if not base.exists():
        return []
    all_chunks = []
    for path in base.rglob("*"):
        if path.suffix.lower() in (".md", ".txt") and path.is_file():
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
                source = path.name
                all_chunks.extend(_chunk_text(text, source))
            except Exception:
                continue
    return all_chunks


class GeminiEmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __init__(self):
        pass

    def __call__(self, input: List[str]) -> List[List[float]]:
        return get_embeddings(input)


def get_client():
    return chromadb.PersistentClient(path=CHROMA_PERSIST_DIR, settings=Settings(anonymized_telemetry=False))


def build_index():
    """Build or rebuild Chroma collection from knowledge base."""
    chunks_with_sources = _load_knowledge_base()
    if not chunks_with_sources:
        return
    client = get_client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    coll = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=GeminiEmbeddingFunction(),
        metadata={"description": "Math mentor knowledge base"},
    )
    ids = [f"chunk_{i}" for i in range(len(chunks_with_sources))]
    documents = [c[0] for c in chunks_with_sources]
    metadatas = [{"source": c[1]} for c in chunks_with_sources]
    coll.add(ids=ids, documents=documents, metadatas=metadatas)


def retrieve(query: str, top_k: int = RAG_TOP_K) -> List[dict]:
    """
    Retrieve top_k chunks for query. Returns list of {"text": ..., "source": ...}.
    No hallucinated citations: if retrieval fails or empty, return empty list.
    """
    try:
        client = get_client()
        coll = client.get_collection(name=COLLECTION_NAME, embedding_function=GeminiEmbeddingFunction())
        results = coll.query(query_texts=[query], n_results=min(top_k, 10))
        out = []
        if results and results.get("documents") and results["documents"][0]:
            for doc, meta in zip(
                results["documents"][0],
                (results.get("metadatas") or [[]])[0] if results.get("metadatas") else [],
            ):
                out.append({"text": doc, "source": (meta or {}).get("source", "unknown")})
        return out
    except Exception:
        return []


def ensure_index():
    """Ensure Chroma collection exists; build from knowledge base if not."""
    client = get_client()
    try:
        client.get_collection(COLLECTION_NAME)
    except Exception:
        build_index()
