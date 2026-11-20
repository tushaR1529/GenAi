"""
Unit and integration tests for FastAPI endpoints, including /health, /records,
semantic search, agent flow, and /ask with a fake/mocked LLM.
"""
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["records"] > 0


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["records"] > 0


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "VidyaLoan API is running" in data["message"]


def test_get_records():
    response = client.get("/records?limit=3")
    assert response.status_code == 200
    records = response.json()
    assert isinstance(records, list)
    assert len(records) <= 3
    assert len(records) > 0


def test_get_record_by_id():
    response = client.get("/records/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1

    not_found = client.get("/records/99999")
    assert not_found.status_code == 404


def test_semantic_search_endpoint():
    response = client.get("/search/semantic?q=subvention&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "subvention"
    assert data["total_hits"] > 0
    assert len(data["results"]) <= 2


def test_semantic_search_empty_query():
    response = client.get("/search/semantic?q=")
    assert response.status_code == 400


def test_ask_with_fake_llm():
    """
    Test /ask endpoint using a fake/mocked LLM to guarantee offline,
    hermetic test execution while validating grounded answer and citation formats.
    """
    fake_rag_response = {
        "question": "What is the income limit for 3% interest subvention under PM-Vidyalaxmi?",
        "answer": (
            "Under PM-Vidyalaxmi, students with annual gross family income up to Rs. 8 lakh "
            "are eligible for a 3% interest subvention on loans up to Rs. 10 lakh during the "
            "moratorium period [Source: pm_vidyalaxmi_guidelines.pdf, Page 2]."
        ),
        "citations": [
            {
                "source": "pm_vidyalaxmi_guidelines.pdf",
                "page": 2,
                "title": "PM-Vidyalaxmi Scheme Guidelines",
                "score": 0.92,
                "chunk_id": "chunk_pmv_p2",
            }
        ],
        "chunks_used": 1,
        "confidence": 0.96,
    }

    with patch("app.main.answer_vidyaloan_question", return_value=fake_rag_response):
        response = client.post(
            "/ask",
            json={"question": "What is the income limit for 3% interest subvention under PM-Vidyalaxmi?"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["question"] == fake_rag_response["question"]
        assert "3% interest subvention" in data["answer"]
        assert len(data["citations"]) == 1
        assert data["citations"][0]["source"] == "pm_vidyalaxmi_guidelines.pdf"
        assert data["citations"][0]["page"] == 2
        assert data["confidence"] == 0.96
        assert data["chunks_used"] == 1


def test_ask_out_of_scope_guardrail():
    """
    Verify /ask rejects out-of-scope foreign study questions with 'I don't know'
    even without contacting an LLM.
    """
    response = client.post(
        "/ask",
        json={"question": "Can I get a loan to study medicine at Oxford University in the UK under PM-Vidyalaxmi?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "i don't know" in data["answer"].lower()
    assert data["citations"] == []


def test_ask_empty_question():
    response = client.post("/ask", json={"question": "   "})
    assert response.status_code == 400


def test_agent_endpoint_approval_flow():
    """Test POST /agent endpoint handles message or loan calculation."""
    response = client.post(
        "/agent",
        json={
            "message": "Calculate loan 750000 at 9.0 percent for 4 years income 400000",
            "session_id": "test_session_1",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "test_session_1"
    assert "status" in data
    assert "response" in data
