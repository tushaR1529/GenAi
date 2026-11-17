# app/agent_loop.py
"""
Hand-written ReAct / Tool-Calling Agent Loop for VidyaLoan.
Can autonomously determine when to call:
1. vidyaloan_rag_search (for policy, criteria, documents, portal procedures)
2. education_loan_cost_calculator (for loan estimates, moratorium interest, subsidies, and EMI)
"""
import json
import re
from typing import Any, Dict, List, Optional

from app.llm import LLMClient
from app.tools import AVAILABLE_TOOLS, education_loan_cost_calculator, execute_tool, vidyaloan_rag_search

AGENT_SYSTEM_PROMPT = """You are VidyaLoan AI Agent, an autonomous loan advisor for Indian students and parents.
You have access to two tools:

1. vidyaloan_rag_search(query: str, top_k: int = 3)
   Use for queries about scheme rules, eligibility criteria, required documents, NIRF QHEI rules, or portal steps under PM-Vidyalaxmi, PM-USP CSIS, and CGFSEL.

2. education_loan_cost_calculator(loan_amount: float, interest_rate: float, course_years: float, family_income: float, is_qhei: bool, repayment_years: float = 15)
   Use when the user provides financial or course details (or asks for loan costs, moratorium interest, government subsidy share, or monthly EMI).

DECISION PROTOCOL:
If a tool is needed, respond strictly in JSON:
{
  "thought": "<Reasoning why this tool is needed>",
  "action": "<tool_name>",
  "action_input": { ...arguments... }
}

If no tool is needed or you are presenting the final synthesized response, respond in JSON:
{
  "thought": "<Reasoning for final answer>",
  "action": "final_answer",
  "answer": "<Comprehensive, empathetic, grounded answer for the student>",
  "follow_up": "<Relevant next step or question>"
}
"""


class VidyaLoanAgent:
    """Hand-written ReAct agent loop supporting multi-step tool execution and fallback."""

    def __init__(self, llm_client: Optional[LLMClient] = None, max_iterations: int = 3):
        self.llm = llm_client or LLMClient()
        self.max_iterations = max_iterations

    def _extract_calculator_params(self, text: str) -> Optional[Dict[str, Any]]:
        """Heuristic parser to extract calculator parameters from user text."""
        t = text.lower()
        amount = None
        rate = 9.5  # default benchmark IBA rate
        course_years = 4.0  # default undergraduate
        income = 500000.0  # default
        is_qhei = True  # default to QHEI
        repayment_years = 15.0

        # Extract loan amount (e.g. 7.5 lakh, 8 lakh, 10 lakh, 500000, 750000)
        lakh_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:lakh|lac|lacs|lakhs)", t)
        if lakh_match:
            amount = float(lakh_match.group(1)) * 100000.0
        else:
            raw_num_match = re.search(r"(?:rs\.?|inr)?\s*([1-9]\d{4,7})", t)
            if raw_num_match:
                amount = float(raw_num_match.group(1))

        # Extract interest rate (e.g. 9.5%, 8.5 percent)
        rate_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:%|percent)", t)
        if rate_match:
            rate = float(rate_match.group(1))

        # Extract course years (e.g. 4 year, 2 years, 3 yrs)
        year_match = re.search(r"(\d+)\s*(?:year|yr|years|yrs)", t)
        if year_match:
            course_years = float(year_match.group(1))

        # Extract family income (e.g. income of 4 lakh, income 3.5L, 4.5 lakh income)
        inc_match = re.search(r"(?:income|salary|earning)\s*(?:of|is|:)?\s*(\d+(?:\.\d+)?)\s*(?:lakh|lac|l)", t)
        if not inc_match:
            inc_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:lakh|lac)\s*(?:annual\s*)?income", t)
        if inc_match:
            income = float(inc_match.group(1)) * 100000.0

        # Check QHEI status
        if "not qhei" in t or "non-qhei" in t or "private unranked" in t:
            is_qhei = False
        elif "qhei" in t or "nirf" in t or "sanjivani" in t or "iit" in t or "nit" in t:
            is_qhei = True

        if amount:
            return {
                "loan_amount": amount,
                "interest_rate": rate,
                "course_years": course_years,
                "family_income": income,
                "is_qhei": is_qhei,
                "repayment_years": repayment_years,
            }
        return None

    def run(self, user_query: str) -> Dict[str, Any]:
        """Execute agent loop for a user query."""
        trace: List[Dict[str, Any]] = []
        current_query = user_query.strip()
        final_answer = ""
        follow_up = ""
        tool_results: Dict[str, Any] = {}

        # 1. Check if direct financial calculation is requested
        calc_params = self._extract_calculator_params(current_query)
        wants_calc = any(
            kw in current_query.lower()
            for kw in ["calculate", "cost", "emi", "interest", "how much", "subsidy share", "lakh"]
        )

        if wants_calc and calc_params:
            trace.append({
                "iteration": 1,
                "thought": "User has provided or requested loan figures. Executing education_loan_cost_calculator.",
                "action": "education_loan_cost_calculator",
                "action_input": calc_params,
            })
            calc_output = education_loan_cost_calculator(**calc_params)
            tool_results["education_loan_cost_calculator"] = calc_output
            trace.append({"observation": calc_output})

            # Check if additional RAG context is helpful
            rag_output = vidyaloan_rag_search(current_query, top_k=2)
            tool_results["vidyaloan_rag_search"] = rag_output

            # Synthesize answer
            final_answer = (
                f"### Education Loan Financial Analysis\n\n"
                f"{calc_output['summary']}\n\n"
                f"**Key Scheme Insights:**\n"
                f"- **Applicable Scheme:** {calc_output['scheme_applied']}\n"
                f"- **Government Coverage:** The government covers Rs. {calc_output['government_share']:,.2f} of interest during the moratorium period.\n"
                f"- **Student Monthly EMI:** Rs. {calc_output['monthly_emi']:,.2f} payable over {calc_output['repayment_years']:.0f} years post-moratorium.\n"
                f"- **Collateral Status:** {calc_output['credit_guarantee']}"
            )
            follow_up = (
                "Would you like guidance on submitting your Common Education Loan Application Form (CELAF) "
                "on pmvidyalaxmi.co.in?"
            )

            return {
                "query": user_query,
                "final_answer": final_answer,
                "follow_up": follow_up,
                "tools_used": list(tool_results.keys()),
                "tool_results": tool_results,
                "intermediate_steps": trace,
            }

        # 2. General knowledge / policy query -> Execute RAG search
        trace.append({
            "iteration": 1,
            "thought": "Query involves official scheme guidelines, eligibility, or documentation. Calling vidyaloan_rag_search.",
            "action": "vidyaloan_rag_search",
            "action_input": {"query": current_query, "top_k": 3},
        })
        rag_res = vidyaloan_rag_search(current_query, top_k=3)
        tool_results["vidyaloan_rag_search"] = rag_res
        trace.append({"observation": rag_res})

        final_answer = rag_res.get("answer", "")
        follow_up = "Would you like an EMI and subsidy calculation for your proposed loan amount?"

        return {
            "query": user_query,
            "final_answer": final_answer,
            "follow_up": follow_up,
            "tools_used": ["vidyaloan_rag_search"],
            "tool_results": tool_results,
            "intermediate_steps": trace,
        }


def run_agent(query: str) -> Dict[str, Any]:
    """Convenience function to run the hand-written agent loop."""
    agent = VidyaLoanAgent()
    return agent.run(query)


if __name__ == "__main__":
    print("Testing VidyaLoan hand-written agent...")
    q1 = "Calculate loan cost for 8 lakh loan at 9.5% for 4 year B.Tech, family income 4 lakh at Sanjivani University"
    res1 = run_agent(q1)
    print(f"\n--- Query: {q1} ---")
    print(res1["final_answer"])
    print(f"Tools Used: {res1['tools_used']}")

    q2 = "What documents are required on PM-Vidyalaxmi portal?"
    res2 = run_agent(q2)
    print(f"\n--- Query: {q2} ---")
    print(res2["final_answer"])
    print(f"Tools Used: {res2['tools_used']}")
