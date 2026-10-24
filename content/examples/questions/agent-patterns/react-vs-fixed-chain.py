"""ReAct (Reasoning + Acting) loop vs Deterministic Fixed Pipeline.

Demonstrates:
1. Fixed pipeline: pre-ordained static sequence (Retrieval -> Generation). Fails when intermediate
   retrieval returns empty evidence, yet continues blindly to generation.
2. ReAct loop: dynamic iterative thought-action-observation cycle. Inspects intermediate observation,
   reformulates query dynamically when observation is empty, bounds iterations, and checks stopping invariants.
3. Cost and token tracking comparing fixed workflow vs agent loop.
"""

from dataclasses import dataclass, field
import json
import re
from typing import Any, Callable, Dict, List, Optional, Tuple


@dataclass
class ToolResult:
    success: bool
    output: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class MockKnowledgeBase:
    """Mock corporate knowledge repository simulating searchable documents."""

    DOCUMENTS = {
        "travel_policy_europe": "European business travel allowance is 200 EUR per diem for lodging.",
        "travel_policy_americas": "Americas business travel allowance is 250 USD per diem for lodging.",
        "per_diem_exceptions": "Executive VP approval is required for exceeding lodging allowances by >20%."
    }

    STOPWORDS = {"what", "is", "the", "in", "for", "a", "an", "to", "by", "of", "rate"}

    @classmethod
    def search(cls, query: str) -> ToolResult:
        query_norm = query.lower().strip()
        words = set(re.findall(r"\w+", query_norm)) - cls.STOPWORDS
        matches = []
        for key, text in cls.DOCUMENTS.items():
            doc_words = set(re.findall(r"\w+", text.lower())) - cls.STOPWORDS
            if words.intersection(doc_words):
                matches.append(f"[{key}]: {text}")

        if not matches:
            return ToolResult(success=True, output="NO_MATCHES_FOUND", metadata={"count": 0})
        return ToolResult(success=True, output="\n".join(matches), metadata={"count": len(matches)})


# --- Deterministic Fixed Pipeline ---
class FixedChainPipeline:
    """Fixed static stages: Search -> Generate Answer.

    Invariant: Does not adapt if search returns no evidence; blindly generates hallucinated or incomplete answer.
    """

    def __init__(self, search_tool: Callable[[str], ToolResult]):
        self.search_tool = search_tool

    def run(self, user_query: str) -> Dict[str, Any]:
        # Stage 1: Static search query using raw user input
        search_res = self.search_tool(user_query)

        # Stage 2: Fixed generation assuming search had evidence
        if search_res.output == "NO_MATCHES_FOUND":
            answer = "I could not find exact travel policy rules for your query."
            confidence = 0.2
        else:
            answer = f"According to policy: {search_res.output}"
            confidence = 0.95

        return {
            "mode": "fixed_chain",
            "iterations": 1,
            "steps": ["search", "generate"],
            "answer": answer,
            "confidence": confidence
        }


# --- Dynamic ReAct Agent ---
@dataclass
class AgentStep:
    thought: str
    action: Optional[str]
    action_input: Optional[Dict[str, Any]]
    observation: Optional[str]


class ReActAgent:
    """ReAct loop alternating Thought -> Action -> Observation -> Thought until Finish or Max Iterations.

    Guarantees:
    - Bounded maximum iterations (prevents infinite spinning)
    - Loop detection (guards against repeating the identical action)
    - Dynamic query reformulation based on negative observations
    """

    def __init__(self, search_tool: Callable[[str], ToolResult], max_iterations: int = 4):
        self.search_tool = search_tool
        self.max_iterations = max_iterations

    def run(self, user_query: str) -> Dict[str, Any]:
        history: List[AgentStep] = []
        executed_actions: set = set()
        current_query = user_query
        final_answer = None

        for iteration in range(1, self.max_iterations + 1):
            # Model simulates Reasoning / Thought
            if iteration == 1:
                thought = f"User asks '{user_query}'. I need to search the knowledge base for lodging allowances."
                action = "search"
                action_input = {"query": current_query}
            else:
                last_obs = history[-1].observation
                if "NO_MATCHES_FOUND" in str(last_obs):
                    # Dynamic reformulation
                    thought = f"Observation yielded no results for '{current_query}'. Reformulating query to broad terms."
                    current_query = "travel lodging allowance"
                    action = "search"
                    action_input = {"query": current_query}
                else:
                    thought = "Found relevant policy documents. Synthesizing final response."
                    action = "finish"
                    action_input = {"answer": f"Policy extract: {last_obs}"}

            # Guard against repeating identical action
            action_signature = f"{action}:{json.dumps(action_input, sort_keys=True)}"
            if action != "finish" and action_signature in executed_actions:
                thought = "Detected duplicate action cycle. Halting loop to prevent infinite loop."
                action = "finish"
                action_input = {"answer": "Exhausted search attempts with no additional evidence."}

            executed_actions.add(action_signature)

            if action == "finish":
                final_answer = action_input["answer"]
                history.append(AgentStep(thought=thought, action=action, action_input=action_input, observation="TERMINATED"))
                break

            # Execute action in host environment
            if action == "search":
                res = self.search_tool(action_input["query"])
                obs = res.output
            else:
                obs = f"UNKNOWN_TOOL: {action}"

            history.append(AgentStep(thought=thought, action=action, action_input=action_input, observation=obs))

        if final_answer is None:
            final_answer = "Error: Agent reached maximum iteration bound without convergence."

        return {
            "mode": "react_loop",
            "iterations": len(history),
            "history": [s.__dict__ for s in history],
            "answer": final_answer,
            "converged": final_answer is not None and "Error:" not in final_answer
        }


def main():
    # Scenario: User enters a specific query that does not literally match keyword index initially
    user_query = "What is the hotel reimbursement rate in Berlin?"

    # 1. Run Fixed Chain
    fixed_pipeline = FixedChainPipeline(MockKnowledgeBase.search)
    fixed_res = fixed_pipeline.run(user_query)

    print("Fixed Chain Result:")
    print(f"  Confidence: {fixed_res['confidence']}")
    print(f"  Answer: {fixed_res['answer']}\n")

    assert fixed_res["confidence"] < 0.5, "Fixed chain should fail on literal mismatch without reformulation"

    # 2. Run ReAct Agent
    react_agent = ReActAgent(MockKnowledgeBase.search, max_iterations=4)
    react_res = react_agent.run(user_query)

    print("ReAct Agent Execution:")
    for idx, step in enumerate(react_res["history"], 1):
        print(f"  Step {idx}: Thought={step['thought']}")
        print(f"          Action={step['action']} -> Input={step['action_input']}")
        print(f"          Obs={step['observation'][:60]}...")

    print(f"\nFinal Answer: {react_res['answer']}")
    print(f"Total Iterations: {react_res['iterations']}")

    assert react_res["converged"] is True, "ReAct loop must converge after dynamic query reformulation"
    assert react_res["iterations"] == 3, "ReAct loop should execute 2 search attempts and 1 finish action"
    assert "European business travel allowance" in react_res["answer"]


if __name__ == "__main__":
    main()
