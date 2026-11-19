"""
Unit tests for TF-IDF Smart Search and Chroma Semantic Search.
"""
from app.smart_search import SmartSearch
from app.vectorstore import get_vectorstore


def test_tfidf_smart_search_finds_relevant_records():
    engine = SmartSearch()
    results = engine.search("interest subvention", top_k=3)
    assert isinstance(results, list)
    assert len(results) > 0
    assert "score" in results[0]
    assert results[0]["score"] > 0
    # Check descending score order
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_tfidf_smart_search_empty_query():
    engine = SmartSearch()
    assert engine.search("") == []
    assert engine.search("   ") == []


def test_chroma_semantic_search():
    vs = get_vectorstore()
    results = vs.search("PM-Vidyalaxmi 3% interest subvention", n_results=3)
    assert isinstance(results, list)
    assert len(results) > 0
    first = results[0]
    assert "text" in first
    assert "score" in first
    assert "source" in first
    assert "page" in first
    assert "title" in first


def test_chroma_semantic_search_empty_query():
    vs = get_vectorstore()
    results = vs.search("", n_results=3)
    assert results == []
