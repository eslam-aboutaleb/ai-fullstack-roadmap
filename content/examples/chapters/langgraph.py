from typing import TypedDict
from langgraph.graph import StateGraph, START, END
class State(TypedDict):
    query: str
    status: str

def build_graph():
    def validate(state: State):
        return {"status": "ready" if state["query"].strip() else "clarify"}
    graph = StateGraph(State)
    graph.add_node("validate", validate)
    graph.add_edge(START, "validate")
    graph.add_edge("validate", END)
    return graph.compile()
# Add durable checkpointing and business idempotency before production use.
