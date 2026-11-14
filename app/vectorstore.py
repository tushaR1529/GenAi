# app/vectorstore.py
"""
Persistent Chroma vectorstore module for VidyaLoan document chunks.
Supports chunk indexing, similarity search, and metadata retrieval.
"""
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.utils import embedding_functions

from app.chunking import DocumentChunk, chunk_all_documents

DEFAULT_PERSIST_DIR = Path(__file__).resolve().parent.parent / "data" / "chroma_db"
DEFAULT_COLLECTION_NAME = "vidyaloan_docs"


class VidyaLoanVectorStore:
    """Wrapper around persistent ChromaDB collection for VidyaLoan chunks."""

    def __init__(
        self,
        persist_dir: Optional[Path] = None,
        collection_name: str = DEFAULT_COLLECTION_NAME,
    ):
        self.persist_dir = persist_dir or DEFAULT_PERSIST_DIR
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=chromadb.Settings(anonymized_telemetry=False),
        )
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )

    def count(self) -> int:
        """Return the number of indexed chunks."""
        return self.collection.count()

    def index_chunks(
        self,
        chunks: List[DocumentChunk],
        batch_size: int = 50,
        overwrite: bool = False,
    ) -> int:
        """Index a list of DocumentChunks into the Chroma collection using batching."""
        if not chunks:
            return 0

        if overwrite:
            # Delete existing collection and recreate
            try:
                self.client.delete_collection(self.collection_name)
            except Exception:
                pass
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"},
            )

        ids: List[str] = []
        documents: List[str] = []
        metadatas: List[Dict[str, Any]] = []

        for c in chunks:
            ids.append(c.id)
            documents.append(c.text)
            metadatas.append({
                "source": c.source,
                "page": int(c.page),
                "title": c.title,
            })

        # Upsert in batches to handle large documents gracefully
        total = len(ids)
        for i in range(0, total, batch_size):
            end_idx = min(i + batch_size, total)
            self.collection.upsert(
                ids=ids[i:end_idx],
                documents=documents[i:end_idx],
                metadatas=metadatas[i:end_idx],
            )

        return self.collection.count()

    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Query the vectorstore for semantically similar chunks."""
        if not query.strip():
            return []

        current_count = self.collection.count()
        if current_count == 0:
            return []

        limit = min(n_results, current_count)
        kwargs: Dict[str, Any] = {
            "query_texts": [query],
            "n_results": limit,
        }
        if where:
            kwargs["where"] = where

        res = self.collection.query(**kwargs)

        hits: List[Dict[str, Any]] = []
        if not res or not res.get("ids") or not res["ids"][0]:
            return hits

        ids = res["ids"][0]
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        distances = res.get("distances", [[]])[0] if res.get("distances") else [0.0] * len(ids)

        for i, hit_id in enumerate(ids):
            # For cosine distance: distance is 1 - similarity, so similarity = 1 - distance
            dist = distances[i] if i < len(distances) else 0.0
            similarity = max(0.0, min(1.0, 1.0 - dist))
            meta = metas[i] if i < len(metas) else {}
            hits.append({
                "id": hit_id,
                "text": docs[i] if i < len(docs) else "",
                "score": round(similarity, 4),
                "source": meta.get("source", ""),
                "page": meta.get("page", 1),
                "title": meta.get("title", ""),
            })

        return hits


# Global singleton instance
_vectorstore_instance: Optional[VidyaLoanVectorStore] = None


def get_vectorstore(auto_index: bool = True) -> VidyaLoanVectorStore:
    """Return initialized VidyaLoanVectorStore singleton, auto-indexing if empty."""
    global _vectorstore_instance
    if _vectorstore_instance is None:
        _vectorstore_instance = VidyaLoanVectorStore()
        if auto_index and _vectorstore_instance.count() == 0:
            chunks = chunk_all_documents()
            if chunks:
                _vectorstore_instance.index_chunks(chunks)
    return _vectorstore_instance


if __name__ == "__main__":
    vs = get_vectorstore()
    print(f"Initial chunk count in vectorstore: {vs.count()}")
    if vs.count() == 0:
        print("Indexing all chunks from data/raw...")
        chunks = chunk_all_documents()
        indexed_count = vs.index_chunks(chunks)
        print(f"Indexed {indexed_count} chunks.")

    sample_query = "What is the maximum loan limit covered by the 75% credit guarantee?"
    results = vs.search(sample_query, n_results=3)
    print(f"\nTop 3 hits for query '{sample_query}':")
    for r in results:
        print(f"\n- ID: {r['id']} | Score: {r['score']} | {r['source']} (Page {r['page']})")
        print(f"  Title: {r['title']}")
        print(f"  Text: {r['text'][:150]}...")
