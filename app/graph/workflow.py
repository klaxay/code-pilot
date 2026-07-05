from langgraph.graph import StateGraph, START, END

from app.models.state import CodePilotState
from app.nodes.intake_task import intake_task
from app.nodes.planner_agent import planner_agent
from app.nodes.implementer_agent import implementer_agent
from app.nodes.write_files import write_files_node
from app.nodes.finalize import finalize


def build_graph():
    graph = StateGraph(CodePilotState)

    graph.add_node("intake_task", intake_task)
    graph.add_node("planner_agent", planner_agent)
    graph.add_node("implementer_agent", implementer_agent)
    graph.add_node("write_files", write_files_node)
    graph.add_node("finalize", finalize)

    graph.add_edge(START, "intake_task")
    graph.add_edge("intake_task", "planner_agent")
    graph.add_edge("planner_agent", "implementer_agent")
    graph.add_edge("implementer_agent", "write_files")
    graph.add_edge("write_files", "finalize")
    graph.add_edge("finalize", END)

    return graph.compile()