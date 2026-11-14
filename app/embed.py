# app/embed.py
"""
Embedding module for VidyaLoan documents.
Provides embedding generation and semantic similarity search using Chroma's ONNX-based MiniLM model.
"""
from typing import Any, Dict, List, Optional
import numpy as np
from chromadb.utils import embedding_functions

from app.chunking import DocumentChunk


class VidyaLoanEmbedder:
    """Wrapper around Chroma's DefaultEmbeddingFunction (all-MiniLM-L6-v2 ONNX)."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._ef = embedding_functions.DefaultEmbeddingFunction()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate normalized vector embeddings for a list of texts."""
        if not texts:
            return []
        raw_embeddings = self._ef(texts)
        # Convert numpy arrays if returned
        return [list(map(float, vec)) for vec in raw_embeddings]

    def embed_query(self, query: str) -> List[float]:
        """Generate embedding vector for a single query."""
        results = self.embed_texts([query])
        return results[0] if results else []


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two float vectors."""
    va = np.array(a, dtype=np.float32)
    vb = np.array(b, dtype=np.float32)
    norm_a = np.linalg.norm(va)
    norm_b = np.linalg.norm(vb)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(va, vb) / (norm_a * norm_b))


def semantic_search_chunks(
    query: str,
    chunks: List[DocumentChunk],
    embedder: Optional[VidyaLoanEmbedder] = None,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """Perform pure in-memory semantic similarity search over a list of DocumentChunks."""
    if not chunks:
        return []

    active_embedder = embedder or VidyaLoanEmbedder()
    chunk_texts = [c.text for c in chunks]
    chunk_embeddings = active_embedder.embed_texts(chunk_texts)
    query_embedding = active_embedder.embed_query(query)

    scored_chunks: List[Dict[str, Any]] = []
    for idx, chunk in enumerate(chunks):
        sim = cosine_similarity(query_embedding, chunk_embeddings[idx])
        scored_chunks.append({
            "id": chunk.id,
            "text": chunk.text,
            "score": round(sim, 4),
            "source": chunk.source,
            "page": chunk.page,
            "title": chunk.title,
        })

    # Sort descending by score
    scored_chunks.sort(key=lambda x: x["score"], reverse=True)
    return scored_chunks[:top_k]


if __name__ == "__main__":
    from app.chunking import chunk_all_documents

    embedder = VidyaLoanEmbedder()
    chunks = chunk_all_documents()
    print(f"Loaded {len(chunks)} chunks.")

    sample_query = "What is the income limit for PM-Vidyalaxmi?"
    hits = semantic_search_chunks(sample_query, chunks, embedder=embedder, top_k=3)
    print(f"\nTop hits for '{sample_query}':")
    for h in hits:
        print(f"[{h['score']}] ({h['source']} p.{h['page']}) {h['text'][:140]}...")

