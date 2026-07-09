from langgraph.graph import StateGraph, START, END

from app.models.state import CodePilotState
from app.nodes.intake_task import intake_task
from app.nodes.planner_agent import planner_agent
from app.nodes.implementer_agent import implementer_agent
from app.nodes.write_files import write_files_node
from app.nodes.finalize import finalize
from app.nodes.review_agent import review_agent
from app.nodes.detect_mode import detect_mode

def route_after_review(state: CodePilotState):
    if state["approved"]:
        return "write_files"

    if state["revision_count"] >= state["max_revisions"]:
        return "write_files"   # or END, depending on your policy

    return "implementer_agent"

def route_after_detect(state: CodePilotState):
    if state["mode"]=="greenfield":
        return "planner_agent"
    return "discover_repo"

def build_graph():
    graph = StateGraph(CodePilotState)

    graph.add_node("intake_task", intake_task)
    graph.add_node("detect_mode", detect_mode)
    graph.add_node("planner_agent", planner_agent)
    graph.add_node("implementer_agent", implementer_agent)
    graph.add_node("review_agent", review_agent)
    graph.add_node("write_files", write_files_node)
    graph.add_node("finalize", finalize)

    graph.add_edge(START, "intake_task")
    graph.add_edge("intake_task", "detect_mode")
    graph.add_conditional_edges(
        "detect_mode",
        route_after_detect,
        {
            "planner_agent": "planner_agent",
            "discover_repo": "discover_repo"
        }

    )
    graph.add_edge("planner_agent", "implementer_agent")
    graph.add_edge("implementer_agent", "review_agent")
    graph.add_conditional_edges(
        "review_agent", 
        route_after_review,
        {
            "write_files":"write_files",
            "implementer_agent": "implementer_agent"
        }
        )
    graph.add_edge("write_files", "finalize")
    graph.add_edge("finalize", END)

    return graph.compile()