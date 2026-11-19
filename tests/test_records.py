"""
Unit tests for record loading, lookup, and keyword search.
"""
from app.records import count_by, get_by_id, load_records, search


def test_load_records_returns_non_empty_list():
    records = load_records()
    assert isinstance(records, list)
    assert len(records) > 0
    first = records[0]
    assert "id" in first
    assert "scheme_name" in first


def test_get_by_id_found():
    record = get_by_id(1)
    assert record is not None
    assert record["id"] == 1
    assert "scheme_name" in record


def test_get_by_id_not_found():
    record = get_by_id(99999)
    assert record is None


def test_keyword_search():
    results = search("PM-Vidyalaxmi")
    assert isinstance(results, list)
    assert len(results) > 0
    assert any("Vidyalaxmi" in str(r.values()) for r in results)


def test_keyword_search_empty():
    results = search("")
    assert results == []


def test_count_by_field():
    counts = count_by("scheme_name")
    assert isinstance(counts, dict)
    assert len(counts) > 0
