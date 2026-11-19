# ui/app.py
"""
VidyaLoan Streamlit Interactive Web Application
Features:
- Streamlit Chat interface connected to /agent and /ask (with local in-process fallback)
- Real-time source citations display (source document, page, and snippet)
- Thumbs up / thumbs down feedback mechanism saved to data/feedback.json
- Signature Feature: Interactive Loan Cost Breakdown Stacked Bar Chart
  (Principal, Moratorium Interest, Govt Subsidy via CSIS/PM-Vidyalaxmi, Family Repayment)
- Human approval step for high-value financial calculations
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import plotly.graph_objects as go
import requests
import streamlit as st

# Add root directory to sys.path for direct service imports
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.graph import get_graph_service
from app.rag import answer_vidyaloan_question
from app.tools import education_loan_cost_calculator

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
FEEDBACK_FILE = ROOT_DIR / "data" / "feedback.json"


def save_feedback(query: str, answer: str, rating: str, comment: str | None = None):
    """Save user thumbs up/down feedback to data/feedback.json."""
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    records = []
    if FEEDBACK_FILE.exists():
        try:
            records = json.loads(FEEDBACK_FILE.read_text(encoding="utf-8"))
        except Exception:
            records = []

    records.append({
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "answer": answer,
        "rating": rating,
        "comment": comment or "",
    })
    FEEDBACK_FILE.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")


def call_backend_agent(message: str, session_id: str, approve: bool | None = None) -> dict[str, Any]:
    """Call POST /agent on FastAPI server with fallback to in-process LangGraph service."""
    try:
        url = f"{API_BASE_URL}/agent"
        payload = {"message": message, "session_id": session_id, "approve": approve}
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass

    # Direct in-process fallback
    service = get_graph_service()
    return service.process_message(message, session_id=session_id, approve=approve)


def build_stacked_cost_chart(calc: dict[str, Any]) -> go.Figure:
    """
    Build the signature stacked bar chart showing:
    - Principal loan amount
    - Interest paid by Government during moratorium (Green)
    - Interest paid by Family during moratorium (Amber)
    - Interest paid by Family during repayment tenure (Orange)
    """
    principal = calc["loan_amount"]
    govt_share = calc["government_share"]
    family_mora = calc["student_moratorium_share"]
    family_repay = calc["total_repayment_interest"]
    scheme = calc["scheme_applied"]

    # Comparative bars:
    # 1. "Without Scheme": Family bears full moratorium interest + repayment interest
    total_mora = calc["total_moratorium_interest"]
    without_scheme_repay = calc["total_repayment_interest"] + (total_mora - family_mora)

    categories = ["Without Government Scheme", "With VidyaLoan Scheme"]

    fig = go.Figure()

    # Principal bar
    fig.add_trace(go.Bar(
        name="Principal Loan Amount",
        x=categories,
        y=[principal, principal],
        marker_color="#2b5c8f",
        text=[f"₹{principal:,.0f}", f"₹{principal:,.0f}"],
        textposition="inside",
    ))

    # Moratorium interest paid by Government (Saved!)
    fig.add_trace(go.Bar(
        name="Govt Subsidy (CSIS / PM-Vidyalaxmi)",
        x=categories,
        y=[0, govt_share],
        marker_color="#28a745",
        text=["₹0", f"₹{govt_share:,.0f}" if govt_share > 0 else "₹0"],
        textposition="inside",
    ))

    # Moratorium interest paid by Family
    fig.add_trace(go.Bar(
        name="Moratorium Interest (Family Share)",
        x=categories,
        y=[total_mora, family_mora],
        marker_color="#dc3545" if total_mora > 0 else "#6c757d",
        text=[f"₹{total_mora:,.0f}", f"₹{family_mora:,.0f}"],
        textposition="inside",
    ))

    # Repayment tenure interest paid by Family
    fig.add_trace(go.Bar(
        name="Repayment Interest (Family Share)",
        x=categories,
        y=[without_scheme_repay, family_repay],
        marker_color="#fd7e14",
        text=[f"₹{without_scheme_repay:,.0f}", f"₹{family_repay:,.0f}"],
        textposition="inside",
    ))

    fig.update_layout(
        barmode="stack",
        title=dict(
            text=f"<b>Total Cost & Government Subsidy Breakdown</b><br><sup>Applied: {scheme}</sup>",
            x=0.05,
            xanchor="left",
        ),
        xaxis_title="Comparison Scenario",
        yaxis_title="Total Financial Commitment (INR ₹)",
        yaxis=dict(tickformat="₹,"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.35,
            xanchor="center",
            x=0.5,
        ),
        margin=dict(l=40, r=40, t=60, b=100),
        height=420,
    )
    return fig


# ---------------- Streamlit App Configuration ----------------
st.set_page_config(
    page_title="VidyaLoan: AI Education Loan Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a365d;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4a5568;
        margin-bottom: 1.5rem;
    }
    .metric-badge {
        background-color: #ebf8ff;
        border: 1px solid #bee3f8;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
    }
    .citation-box {
        background-color: #f7fafc;
        border-left: 4px solid #3182ce;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 0.88rem;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- Session State Initialization ----------------
if "session_id" not in st.session_state:
    st.session_state["session_id"] = f"vidyaloan_sess_{int(datetime.now().timestamp())}"

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": (
                "Namaste! I am your **VidyaLoan AI Assistant**. I can help you check eligibility, "
                "understand interest subsidies under **PM-Vidyalaxmi** and **PM-USP CSIS**, "
                "or calculate your exact moratorium savings and monthly EMI. How can I help you today?"
            ),
            "citations": [],
            "id": 0,
        }
    ]

if "pending_approval" not in st.session_state:
    st.session_state["pending_approval"] = False

if "last_query" not in st.session_state:
    st.session_state["last_query"] = ""


# ---------------- Sidebar: Signature Feature (Loan Calculator) ----------------
with st.sidebar:
    st.markdown("### 📊 Interactive Loan Cost Calculator")
    st.caption("Updates live as you adjust income, loan amount, or institute status.")

    col_inp1, col_inp2 = st.columns(2)
    with col_inp1:
        loan_amt_lakh = st.slider("Loan Amount (₹ Lakh)", min_value=1.0, max_value=25.0, value=7.5, step=0.5)
        loan_amount = loan_amt_lakh * 100000.0
    with col_inp2:
        income_lakh = st.slider("Family Income (₹ Lakh)", min_value=1.0, max_value=15.0, value=4.0, step=0.5)
        family_income = income_lakh * 100000.0

    col_inp3, col_inp4 = st.columns(2)
    with col_inp3:
        course_years = st.number_input("Course Duration (Years)", min_value=1.0, max_value=6.0, value=4.0, step=1.0)
    with col_inp4:
        interest_rate = st.number_input("Interest Rate (% p.a.)", min_value=5.0, max_value=15.0, value=9.5, step=0.25)

    col_inp5, col_inp6 = st.columns(2)
    with col_inp5:
        repayment_years = st.number_input("Repayment Tenure (Yrs)", min_value=5.0, max_value=15.0, value=15.0, step=1.0)
    with col_inp6:
        is_qhei = st.checkbox("NIRF Top 100/200 QHEI Institute", value=True)

    # Perform Live Calculation
    calc_res = education_loan_cost_calculator(
        loan_amount=loan_amount,
        interest_rate=interest_rate,
        course_years=course_years,
        family_income=family_income,
        is_qhei=is_qhei,
        repayment_years=repayment_years,
    )

    st.markdown("---")
    st.markdown("#### 🎯 Calculation Summary")

    m1, m2 = st.columns(2)
    m1.metric("Government Subsidy", f"₹{calc_res['government_share']:,.0f}", delta="Subsidy Saved" if calc_res['government_share'] > 0 else None)
    m2.metric("Monthly EMI", f"₹{calc_res['monthly_emi']:,.0f}")

    st.info(f"**Scheme:** {calc_res['scheme_applied']}")
    if calc_res["is_collateral_free"]:
        st.success("✅ **75% Credit Guarantee via NCGTC** (Zero Collateral & Guarantor Required)")
    else:
        st.warning("⚠️ **Above ₹7.5 Lakh:** Collateral / guarantor requirements subject to bank policy.")

    if st.button("💬 Ask AI about this projection in Chat"):
        prompt_text = (
            f"Calculate loan cost for {loan_amt_lakh} lakh loan at {interest_rate}% for {course_years:.0f} year course, "
            f"family income {income_lakh} lakh{' at a QHEI' if is_qhei else ' at a non-QHEI'}"
        )
        st.session_state["messages"].append({"role": "user", "content": prompt_text, "id": len(st.session_state["messages"])})
        with st.spinner("Processing with VidyaLoan Agent..."):
            ans_res = call_backend_agent(prompt_text, session_id=st.session_state["session_id"])
            st.session_state["messages"].append({
                "role": "assistant",
                "content": ans_res.get("response", ""),
                "citations": [],
                "id": len(st.session_state["messages"]),
            })
            if ans_res.get("needs_approval"):
                st.session_state["pending_approval"] = True
            st.rerun()


# ---------------- Main Chat Area ----------------
st.markdown('<div class="main-header">🎓 VidyaLoan: AI Education Loan Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Grounded guidance on PM-Vidyalaxmi, PM-USP CSIS, and CGFSEL Central Sector Schemes</div>', unsafe_allow_html=True)

# Signature Feature: Render Chart in Expandable Dashboard or Tab
with st.expander("📈 **Live Visualizer: Interactive Loan Cost Breakdown Chart**", expanded=True):
    fig = build_stacked_cost_chart(calc_res)
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)


# Render Chat Messages
for msg in st.session_state["messages"]:
    role = msg["role"]
    content = msg["content"]
    citations = msg.get("citations", [])
    msg_id = msg.get("id", 0)

    with st.chat_message(role, avatar="🧑‍🎓" if role == "user" else "🏛️"):
        st.markdown(content)

        # Show citations if present
        if citations:
            with st.expander(f"📚 Verified Sources & Citations ({len(citations)})", expanded=False):
                for cit in citations:
                    st.markdown(
                        f"- **{cit.get('title', 'Scheme Document')}** | `{cit.get('source', '')}` (Page {cit.get('page', 1)})"
                    )

        # Show Thumbs Up / Down feedback only for assistant responses (skip initial greeting)
        if role == "assistant" and msg_id > 0:
            fb_col1, fb_col2, fb_col3 = st.columns([1, 1, 10])
            with fb_col1:
                if st.button("👍", key=f"up_{msg_id}", help="Accurate and helpful"):
                    save_feedback(
                        query=st.session_state.get("last_query", ""),
                        answer=content,
                        rating="positive",
                    )
                    st.toast("Thank you for your feedback! 👍", icon="✅")
            with fb_col2:
                if st.button("👎", key=f"down_{msg_id}", help="Inaccurate or incomplete"):
                    save_feedback(
                        query=st.session_state.get("last_query", ""),
                        answer=content,
                        rating="negative",
                    )
                    st.toast("Thank you for your feedback. We will improve! 👎", icon="📝")


# Approval Gate Widget if Agent is awaiting confirmation
if st.session_state.get("pending_approval"):
    st.warning("⚠️ **Approval Required:** The agent requires confirmation to finalize this high-value calculation projection.")
    col_app1, col_app2, _ = st.columns([2, 2, 6])
    with col_app1:
        if st.button("✅ Approve Calculation", type="primary"):
            st.session_state["pending_approval"] = False
            with st.spinner("Executing approved financial computation..."):
                res = call_backend_agent("", session_id=st.session_state["session_id"], approve=True)
                st.session_state["messages"].append({
                    "role": "assistant",
                    "content": res.get("response", ""),
                    "citations": [],
                    "id": len(st.session_state["messages"]),
                })
                st.rerun()
    with col_app2:
        if st.button("❌ Decline", type="secondary"):
            st.session_state["pending_approval"] = False
            with st.spinner("Cancelling projection..."):
                res = call_backend_agent("", session_id=st.session_state["session_id"], approve=False)
                st.session_state["messages"].append({
                    "role": "assistant",
                    "content": res.get("response", ""),
                    "citations": [],
                    "id": len(st.session_state["messages"]),
                })
                st.rerun()


# Chat Input Prompt
if user_prompt := st.chat_input("Ask any question about PM-Vidyalaxmi, CSIS, eligibility, or loan calculations..."):
    st.session_state["last_query"] = user_prompt
    st.session_state["messages"].append({
        "role": "user",
        "content": user_prompt,
        "id": len(st.session_state["messages"]),
    })

    with st.spinner("Thinking & retrieving verified scheme facts..."):
        # If user asks specific scheme questions, also extract citations via RAG
        rag_data = answer_vidyaloan_question(user_prompt, top_k=3)
        agent_res = call_backend_agent(user_prompt, session_id=st.session_state["session_id"])

        response_text = agent_res.get("response", "")
        if not response_text:
            response_text = rag_data.get("answer", "")

        citations = rag_data.get("citations", [])

        st.session_state["messages"].append({
            "role": "assistant",
            "content": response_text,
            "citations": citations,
            "id": len(st.session_state["messages"]),
        })

        if agent_res.get("needs_approval"):
            st.session_state["pending_approval"] = True

    st.rerun()
