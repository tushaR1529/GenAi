# eval/test_agent_day9.py
"""
Automated test and verification script for Day 9 deliverables:
1. app/tools.py: education_loan_cost_calculator & vidyaloan_rag_search
2. app/agent_loop.py: hand-written agent loop
3. app/graph.py: LangGraph agent with MemorySaver and approval step
4. app/main.py: POST /agent endpoint
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient
from app.agent_loop import VidyaLoanAgent
from app.graph import get_graph_service
from app.main import app
from app.tools import education_loan_cost_calculator


def test_calculator_scenarios():
    print("=== Testing Tool: education_loan_cost_calculator ===")

    # Scenario 1: CSIS (Income <= 4.5 Lakh)
    # 7.5L loan, 9.5% interest, 4-year B.Tech (moratorium = 5 yrs), income 4 Lakh -> 100% subsidy
    r1 = education_loan_cost_calculator(
        loan_amount=750000,
        interest_rate=9.5,
        course_years=4,
        family_income=400000,
        is_qhei=True,
    )
    assert r1["moratorium_years"] == 5.0
    assert r1["total_moratorium_interest"] == 356250.0
    assert r1["government_share"] == 356250.0  # 100% covered
    assert r1["student_moratorium_share"] == 0.0
    assert r1["is_collateral_free"] is True
    print("  [PASS] Scenario 1 (CSIS 100% Subsidy): Government pays Rs. 3,56,250")

    # Scenario 2: PM-Vidyalaxmi (Income <= 8 Lakh at QHEI)
    # 10L loan, 9.5% interest, 4-year B.Tech, income 6.5 Lakh, is_qhei=True -> 3% subvention
    r2 = education_loan_cost_calculator(
        loan_amount=1000000,
        interest_rate=9.5,
        course_years=4,
        family_income=650000,
        is_qhei=True,
    )
    assert r2["government_share"] == 150000.0  # 10L * 3% * 5 yrs = 1,50,000
    assert r2["student_moratorium_share"] == 325000.0  # 10L * (9.5% - 3%) * 5 yrs = 3,25,000
    print("  [PASS] Scenario 2 (PM-Vidyalaxmi 3% Subvention): Government pays Rs. 1,50,000")

    # Scenario 3: Above 8 Lakh (No Subsidy)
    r3 = education_loan_cost_calculator(
        loan_amount=800000,
        interest_rate=9.5,
        course_years=4,
        family_income=900000,
        is_qhei=True,
    )
    assert r3["government_share"] == 0.0
    assert r3["student_moratorium_share"] == 380000.0
    print("  [PASS] Scenario 3 (Above 8L - Standard Loan): Government pays Rs. 0")


def test_handwritten_agent():
    print("\n=== Testing Hand-written Agent Loop (app/agent_loop.py) ===")
    agent = VidyaLoanAgent()

    # Query with calculation intent
    q_calc = "Calculate EMI and subsidy for 8 lakh loan at 9.5% for 4 year B.Tech with income 4 lakh"
    res1 = agent.run(q_calc)
    assert "education_loan_cost_calculator" in res1["tools_used"]
    assert "PM-USP CSIS" in res1["final_answer"]
    print(f"  [PASS] Financial calculation query triggered calculator tool: {res1['tools_used']}")

    # Procedural query
    q_policy = "What are the mandatory documents on the PM-Vidyalaxmi portal?"
    res2 = agent.run(q_policy)
    assert "vidyaloan_rag_search" in res2["tools_used"]
    assert "marksheet" in res2["final_answer"].lower()
    print(f"  [PASS] Procedural policy query triggered RAG tool: {res2['tools_used']}")


def test_langgraph_and_api():
    print("\n=== Testing LangGraph Agent Service & POST /agent ===")
    client = TestClient(app)

    # 1. Informational query through POST /agent (direct execution, no approval needed)
    resp1 = client.post("/agent", json={"message": "What is the moratorium period definition?"})
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["status"] == "completed"
    assert data1["needs_approval"] is False
    print("  [PASS] Informational query completed without approval.")

    # 2. High-value calculation query through POST /agent (triggers approval gate)
    sess_id = "eval_session_day9"
    resp2 = client.post("/agent", json={
        "message": "Calculate 7.5 lakh loan at 9.5% for 4 year course with family income 4 lakh",
        "session_id": sess_id,
    })
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["status"] == "awaiting_approval"
    assert data2["needs_approval"] is True
    assert "CONFIRMATION REQUIRED" in data2["response"]
    print("  [PASS] High-value calculation halted at approval gate (needs_approval=True).")

    # 3. Provide approval via POST /agent (resumes from memory checkpoint)
    resp3 = client.post("/agent", json={
        "session_id": sess_id,
        "approve": True,
    })
    assert resp3.status_code == 200
    data3 = resp3.json()
    assert data3["status"] == "completed"
    assert data3["needs_approval"] is False
    assert "Verified Education Loan Calculation" in data3["response"]
    print("  [PASS] Approval granted; LangGraph resumed from MemorySaver and executed calculation.")


if __name__ == "__main__":
    test_calculator_scenarios()
    test_handwritten_agent()
    test_langgraph_and_api()
    print("\nALL DAY 9 VERIFICATION CHECKS PASSED SUCCESSFULLY!")
