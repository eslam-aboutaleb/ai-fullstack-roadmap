"""StateGraph, Custom Reducers, Parallel Fan-Out/Fan-In, and Conditional Routing.

Demonstrates:
1. What LangGraph Solves:
   - Explicit cyclical graph topology, multi-agent coordination, and declarative channel reducers
     that basic while-loops cannot cleanly model.
2. Channel Reducers for Parallel Fan-In:
   - Message Channel: uses list append reducer (`operator.add`).
   - Document Collection Channel: uses custom deduplicating set reducer to merge concurrent search outputs
     without data loss or duplication.
   - Scalar Route Channel: uses last-write-wins replacement.
3. Conditional Edge Routing:
   - Evaluates state inspection predicates to route conditionally to human review or terminal output.
4. Framework Selection Fit:
   - Compares when to use LangGraph (complex cyclical state machines with parallel branches) vs plain functions/ADK.
"""

from dataclasses import dataclass, field
import operator
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


@dataclass
class SearchDocument:
    doc_id: str
    content: str


def deduplicating_doc_reducer(
    current: List[SearchDocument],
    update: List[SearchDocument]
) -> List[SearchDocument]:
    """Custom reducer for parallel fan-in: merges document lists deduplicating by doc_id."""
    existing_ids = {d.doc_id for d in current}
    merged = list(current)
    for doc in update:
        if doc.doc_id not in existing_ids:
            merged.append(doc)
            existing_ids.add(doc.doc_id)
    return merged


@dataclass
class GraphState:
    query: str
    messages: List[str] = field(default_factory=list)
    documents: List[SearchDocument] = field(default_factory=list)
    needs_review: bool = False
    next_node: str = "start"


class MockStateGraphRuntime:
    """Simulates LangGraph StateGraph engine with reducers and conditional edge routing."""

    def __init__(self):
        self.nodes: Dict[str, Callable[[GraphState], Dict[str, Any]]] = {}
        self.conditional_edges: Dict[str, Callable[[GraphState], str]] = {}

    def add_node(self, name: str, func: Callable[[GraphState], Dict[str, Any]]):
        self.nodes[name] = func

    def add_conditional_edges(self, source_node: str, router_func: Callable[[GraphState], str]):
        self.conditional_edges[source_node] = router_func

    def apply_state_updates(self, state: GraphState, updates: Dict[str, Any]):
        for key, val in updates.items():
            if key == "messages":
                # operator.add reducer: list concatenation
                state.messages = operator.add(state.messages, val)
            elif key == "documents":
                # Custom deduplicating reducer
                state.documents = deduplicating_doc_reducer(state.documents, val)
            elif key == "needs_review":
                state.needs_review = val
            elif key == "next_node":
                state.next_node = val

    def execute_workflow(self, initial_state: GraphState) -> GraphState:
        state = initial_state
        state.next_node = "query_router"

        while state.next_node != "END":
            current_step = state.next_node
            node_fn = self.nodes.get(current_step)
            if not node_fn:
                break

            # Execute node
            updates = node_fn(state)
            self.apply_state_updates(state, updates)

            # Check conditional edge
            if current_step in self.conditional_edges:
                state.next_node = self.conditional_edges[current_step](state)
            else:
                state.next_node = updates.get("next_node", "END")

        return state


# --- Graph Nodes Definition ---
def query_router_node(state: GraphState) -> Dict[str, Any]:
    return {
        "messages": [f"Router: Classified intent for '{state.query}'"],
        "next_node": "parallel_search"
    }


def parallel_dense_search(state: GraphState) -> Dict[str, Any]:
    """Node 1 of parallel branch: returns vector search documents."""
    return {
        "documents": [
            SearchDocument("doc_101", "EU lodging reimbursement allowance is 200 EUR."),
            SearchDocument("doc_102", "Executive approval required for budget overages.")
        ],
        "messages": ["Dense search returned 2 candidates."]
    }


def parallel_sparse_search(state: GraphState) -> Dict[str, Any]:
    """Node 2 of parallel branch: returns lexical keyword documents (shares doc_101!)."""
    return {
        "documents": [
            SearchDocument("doc_101", "EU lodging reimbursement allowance is 200 EUR."),  # Duplicate!
            SearchDocument("doc_103", "Flight booking policy requires coach class for flights <6h.")
        ],
        "messages": ["Sparse search returned 2 candidates."]
    }


def synthesis_node(state: GraphState) -> Dict[str, Any]:
    # Check if high value or overage triggers human review
    has_overage = any("approval required" in d.content.lower() for d in state.documents)
    return {
        "messages": [f"Synthesis complete across {len(state.documents)} unique documents."],
        "needs_review": has_overage
    }


def route_after_synthesis(state: GraphState) -> str:
    """Conditional Edge: routes to human_review or finish based on state inspection."""
    if state.needs_review:
        return "human_review_gate"
    return "END"


def human_review_gate_node(state: GraphState) -> Dict[str, Any]:
    return {
        "messages": ["Human Review Gate: Escalated to manager review."],
        "next_node": "END"
    }


def main():
    runtime = MockStateGraphRuntime()

    # Register nodes
    runtime.add_node("query_router", query_router_node)
    runtime.add_node("synthesis", synthesis_node)
    runtime.add_node("human_review_gate", human_review_gate_node)

    # Register conditional edge
    runtime.add_conditional_edges("synthesis", route_after_synthesis)

    initial_state = GraphState(query="Can I book a luxury hotel suite in Paris?")

    print("1. Running StateGraph with Parallel Fan-Out and Deduplicating Reducer:")
    # Execute query_router
    runtime.apply_state_updates(initial_state, query_router_node(initial_state))

    # Simulate Parallel Fan-Out execution (Dense and Sparse search nodes run concurrently)
    dense_updates = parallel_dense_search(initial_state)
    sparse_updates = parallel_sparse_search(initial_state)

    # Apply fan-in merge using reducers
    runtime.apply_state_updates(initial_state, dense_updates)
    runtime.apply_state_updates(initial_state, sparse_updates)

    print(f"  Messages after parallel merge ({len(initial_state.messages)} items):")
    for msg in initial_state.messages:
        print(f"    - {msg}")

    print(f"\n  Documents after deduplicating reducer ({len(initial_state.documents)} unique docs):")
    for doc in initial_state.documents:
        print(f"    [{doc.doc_id}]: {doc.content}")

    # Assert that doc_101 was deduplicated! 2 + 2 = 3 unique documents!
    assert len(initial_state.documents) == 3
    assert {d.doc_id for d in initial_state.documents} == {"doc_101", "doc_102", "doc_103"}

    # 2. Execute Synthesis and Conditional Edge Routing
    print("\n2. Executing Synthesis and Conditional Edge Routing:")
    synth_updates = synthesis_node(initial_state)
    runtime.apply_state_updates(initial_state, synth_updates)

    next_route = route_after_synthesis(initial_state)
    print(f"  State needs_review: {initial_state.needs_review}")
    print(f"  Conditional Edge Routed To: {next_route}")
    assert next_route == "human_review_gate"

    # Complete human review gate
    review_updates = human_review_gate_node(initial_state)
    runtime.apply_state_updates(initial_state, review_updates)
    assert "Escalated to manager review" in initial_state.messages[-1]

    print("\nStateGraph reducers, parallel fan-in deduplication, and conditional routing verified successfully.")


if __name__ == "__main__":
    main()
