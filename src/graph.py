from langgraph.graph import StateGraph, START, END
# from langgraph.checkpoint.memory import MemorySaver

from src.state import CallDebriefState
from src.nodes import (
    extract_info,
    update_crm,
    create_task,
    draft_email,
    flag_risks,
    human_review,
    auto_approve,
    build_report,
)


def route_by_risk(state: CallDebriefState) -> str:
    """
    WHY THIS EXISTS:
    This is the conditional edge function. After flag_risks runs,
    the graph calls this function to decide the next node.
    It returns a string that must exactly match a registered node name.
    
    medium/high risk → human must review before anything is finalized
    low risk → auto-approve and proceed directly to build_report
    """
    if state["risk_level"] in ("medium", "high"):
        return "human_review"
    return "auto_approve"


def build_graph():
    """
    WHY THIS IS A FUNCTION:
    Wrapping graph construction in a function means we can call it
    from main.py, from tests, or from a FastAPI endpoint — anywhere.
    It also makes it easy to pass different checkpointers
    (MemorySaver for dev, PostgresSaver for production).
    """

    # Step 1: Create the graph and tell it what state shape to expect
    graph = StateGraph(CallDebriefState)

    # Step 2: Register all nodes
    # WHY: Every node must be registered before edges can reference it.
    # The first argument is the name used in edges and routing functions.
    graph.add_node("extract_info",  extract_info)
    graph.add_node("update_crm",    update_crm)
    graph.add_node("create_task",   create_task)
    graph.add_node("draft_email",   draft_email)
    graph.add_node("flag_risks",    flag_risks)
    graph.add_node("human_review",  human_review)
    graph.add_node("auto_approve",  auto_approve)
    graph.add_node("build_report",  build_report)

    # Step 3: Draw the edges — the main sequential flow
    # WHY: add_edge(A, B) means "always go from A to B".
    # START is a built-in LangGraph constant for the entry point.
    graph.add_edge(START,          "extract_info")
    graph.add_edge("extract_info", "update_crm")
    graph.add_edge("update_crm",   "create_task")
    graph.add_edge("create_task",  "draft_email")
    graph.add_edge("draft_email",  "flag_risks")

    # Step 4: The conditional edge
    # WHY: add_conditional_edges takes:
    #   - the source node (flag_risks)
    #   - the routing function (route_by_risk)
    #   - a dict mapping return values to destination node names
    # After flag_risks completes, route_by_risk is called with
    # the current state. Its return value picks the next node.
    graph.add_conditional_edges(
        "flag_risks",
        route_by_risk,
        {
            "human_review": "human_review",
            "auto_approve": "auto_approve",
        }
    )

    # Step 5: Both paths converge at build_report
    graph.add_edge("human_review", "build_report")
    graph.add_edge("auto_approve", "build_report")
    graph.add_edge("build_report", END)

    # Step 6: Attach the checkpointer and compile
    # WHY CHECKPOINTER IS MANDATORY:
    # interrupt() in human_review node serializes state to this checkpointer.
    # Without it, interrupt() raises an error because it has nowhere to save state.
    # MemorySaver = in-memory (dev only, state lost on restart)
    # In production: replace with PostgresSaver or RedisSaver — one line change here.
    # checkpointer = MemorySaver()

    # compile() validates the graph (checks for disconnected nodes,
    # missing edges, etc.) and returns a runnable object.
    return graph.compile()


# The compiled graph — imported by main.py
app = build_graph()
