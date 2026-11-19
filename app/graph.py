# app/graph.py
"""
LangGraph implementation of the VidyaLoan AI Agent with:
1. Multi-step state graph (Planner -> Approval Gate -> Tool Execution -> Synthesizer)
2. In-memory checkpointer (MemorySaver) for session conversation state
3. Human-in-the-loop approval step for loan calculation commitments
"""
from typing import Any, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from app.agent_loop import VidyaLoanAgent
from app.tools import execute_tool


class AgentGraphState(TypedDict):
    """State schema for the VidyaLoan LangGraph agent."""
    session_id: str
    messages: list[dict[str, str]]
    current_input: str
    tool_to_call: str | None
    tool_args: dict[str, Any] | None
    tool_output: dict[str, Any] | None
    requires_approval: bool
    approved: bool | None
    final_output: str
    status: str  # "completed", "awaiting_approval", "action_rejected"


# Helper agent instance for parameter extraction
_extractor_agent = VidyaLoanAgent()


def planner_node(state: AgentGraphState) -> dict[str, Any]:
    """Analyze input, decide which tool to call, and determine if human approval is needed."""
    user_query = state.get("current_input", "").strip()
    calc_params = _extractor_agent._extract_calculator_params(user_query)

    wants_calc = any(
        kw in user_query.lower()
        for kw in ["calculate", "cost", "emi", "interest", "how much", "subsidy", "lakh"]
    )

    if wants_calc and calc_params:
        # Sensitive financial calculation requires user approval if loan amount >= 5 Lakh
        amount = calc_params.get("loan_amount", 0.0)
        needs_approval = (amount >= 500000.0)

        # If already approved in state, do not re-request approval
        if state.get("approved") is True:
            needs_approval = False

        return {
            "tool_to_call": "education_loan_cost_calculator",
            "tool_args": calc_params,
            "requires_approval": needs_approval,
            "status": "awaiting_approval" if needs_approval else "planned",
        }

    # Policy / guideline queries -> RAG Search (no approval needed)
    return {
        "tool_to_call": "vidyaloan_rag_search",
        "tool_args": {"query": user_query, "top_k": 3},
        "requires_approval": False,
        "status": "planned",
    }


def approval_node(state: AgentGraphState) -> dict[str, Any]:
    """Human-in-the-loop approval gate for financial computations."""
    approved = state.get("approved")
    tool_args = state.get("tool_args") or {}
    loan_amt = tool_args.get("loan_amount", 0.0)
    rate = tool_args.get("interest_rate", 9.5)

    if approved is True:
        return {"status": "approved"}

    if approved is False:
        return {
            "status": "action_rejected",
            "final_output": (
                "Loan calculation action was cancelled as requested. "
                "You can ask any other questions about PM-Vidyalaxmi or PM-USP CSIS guidelines."
            ),
        }

    # Otherwise, waiting for human approval
    prompt_msg = (
        f"CONFIRMATION REQUIRED: You requested a loan cost & subsidy projection for Rs. {loan_amt:,.2f} "
        f"at {rate:.2f}% interest. Proceed with the official scheme calculation and credit guarantee assessment? "
        f"(Please confirm with approve: true/false)."
    )
    return {
        "status": "awaiting_approval",
        "final_output": prompt_msg,
    }


def tool_execution_node(state: AgentGraphState) -> dict[str, Any]:
    """Execute the chosen tool."""
    tool_name = state.get("tool_to_call")
    tool_args = state.get("tool_args") or {}

    if not tool_name:
        return {"tool_output": None}

    output = execute_tool(tool_name, tool_args)
    return {"tool_output": output, "status": "tool_executed"}


def rejection_node(state: AgentGraphState) -> dict[str, Any]:
    """Handle rejected action state."""
    return {
        "status": "action_rejected",
        "final_output": (
            "The proposed calculation was declined. "
            "Let me know if you would like information on eligible institutions or application documents instead."
        ),
    }


def synthesizer_node(state: AgentGraphState) -> dict[str, Any]:
    """Synthesize tool outputs into final structured response."""
    tool_name = state.get("tool_to_call")
    tool_out = state.get("tool_output") or {}

    if tool_name == "education_loan_cost_calculator":
        summary = tool_out.get("summary", "")
        scheme = tool_out.get("scheme_applied", "")
        govt_share = tool_out.get("government_share", 0.0)
        emi = tool_out.get("monthly_emi", 0.0)
        tenure = tool_out.get("repayment_years", 15.0)
        guarantee = tool_out.get("credit_guarantee", "")

        final_text = (
            f"### Verified Education Loan Calculation\n\n"
            f"{summary}\n\n"
            f"**Advisory Summary:**\n"
            f"- **Scheme:** {scheme}\n"
            f"- **Government Subsidy:** Rs. {govt_share:,.2f} covered during the moratorium.\n"
            f"- **Repayment EMI:** Rs. {emi:,.2f}/month over {tenure:.0f} years.\n"
            f"- **Security:** {guarantee}"
        )
    elif tool_name == "vidyaloan_rag_search":
        ans = tool_out.get("answer", "")
        cits = tool_out.get("citations", [])
        cit_text = ""
        if cits:
            cit_items = [f"{c.get('source', '')} (Page {c.get('page', '')})" for c in cits]
            cit_text = f"\n\n**Sources:** {', '.join(cit_items)}"
        final_text = f"{ans}{cit_text}"
    else:
        final_text = "I am ready to help you explore PM-Vidyalaxmi and PM-USP CSIS education loan schemes."

    # Update conversation history
    messages = list(state.get("messages", []))
    messages.append({"role": "user", "content": state.get("current_input", "")})
    messages.append({"role": "assistant", "content": final_text})

    return {
        "final_output": final_text,
        "messages": messages,
        "status": "completed",
    }


def route_after_planner(state: AgentGraphState) -> str:
    """Routing condition following the planner node."""
    if state.get("requires_approval") and state.get("approved") is not True:
        return "approval_node"
    if state.get("tool_to_call"):
        return "tool_execution_node"
    return "synthesizer_node"


def route_after_approval(state: AgentGraphState) -> str:
    """Routing condition following the approval gate."""
    st = state.get("status")
    if st == "approved":
        return "tool_execution_node"
    if st == "action_rejected":
        return "rejection_node"
    return END


# Build and compile LangGraph
builder = StateGraph(AgentGraphState)

builder.add_node("planner_node", planner_node)
builder.add_node("approval_node", approval_node)
builder.add_node("tool_execution_node", tool_execution_node)
builder.add_node("rejection_node", rejection_node)
builder.add_node("synthesizer_node", synthesizer_node)

builder.add_edge(START, "planner_node")
builder.add_conditional_edges(
    "planner_node",
    route_after_planner,
    {
        "approval_node": "approval_node",
        "tool_execution_node": "tool_execution_node",
        "synthesizer_node": "synthesizer_node",
    },
)

builder.add_conditional_edges(
    "approval_node",
    route_after_approval,
    {
        "tool_execution_node": "tool_execution_node",
        "rejection_node": "rejection_node",
        END: END,
    },
)

builder.add_edge("tool_execution_node", "synthesizer_node")
builder.add_edge("rejection_node", END)
builder.add_edge("synthesizer_node", END)

# In-memory checkpointer for multi-turn conversation memory
memory_checkpointer = MemorySaver()
langgraph_app = builder.compile(checkpointer=memory_checkpointer)


class LangGraphAgentService:
    """Service wrapper for interacting with the LangGraph agent."""

    def __init__(self):
        self.graph = langgraph_app

    def process_message(
        self,
        message: str,
        session_id: str = "default_session",
        approve: bool | None = None,
    ) -> dict[str, Any]:
        """Send message or approval status to the LangGraph agent."""
        config = {"configurable": {"thread_id": session_id}}

        initial_state: AgentGraphState = {
            "session_id": session_id,
            "messages": [],
            "current_input": message,
            "tool_to_call": None,
            "tool_args": None,
            "tool_output": None,
            "requires_approval": False,
            "approved": approve,
            "final_output": "",
            "status": "started",
        }

        # If providing approval for an existing session, restore prior state
        if approve is not None:
            prev_snapshot = self.graph.get_state(config)
            if prev_snapshot and prev_snapshot.values:
                saved = dict(prev_snapshot.values)
                saved["approved"] = approve
                # If message is empty, retain existing current_input
                if not message.strip():
                    initial_state = saved
                else:
                    saved["current_input"] = message
                    initial_state = saved

        result = self.graph.invoke(initial_state, config=config)

        return {
            "session_id": session_id,
            "status": result.get("status", "completed"),
            "response": result.get("final_output", ""),
            "tool_called": result.get("tool_to_call"),
            "tool_result": result.get("tool_output"),
            "needs_approval": (result.get("status") == "awaiting_approval"),
        }


# Singleton service
_graph_service: LangGraphAgentService | None = None


def get_graph_service() -> LangGraphAgentService:
    """Return singleton LangGraphAgentService."""
    global _graph_service
    if _graph_service is None:
        _graph_service = LangGraphAgentService()
    return _graph_service


if __name__ == "__main__":
    service = get_graph_service()
    print("1. Testing LangGraph with RAG search (no approval needed)...")
    r1 = service.process_message("What is the income limit for 3% interest subvention?")
    print(f"Status: {r1['status']}")
    print(f"Response:\n{r1['response']}\n")

    print("2. Testing LangGraph with high-value calculation (requires approval)...")
    r2 = service.process_message(
        "Calculate loan for 7.5 lakh loan at 9.5% for 4 year B.Tech, income 4 lakh",
        session_id="user_session_1",
    )
    print(f"Status: {r2['status']}")
    print(f"Response: {r2['response']}\n")

    print("3. Resuming with approval=True...")
    r3 = service.process_message("", session_id="user_session_1", approve=True)
    print(f"Status: {r3['status']}")
    print(f"Response:\n{r3['response']}\n")
