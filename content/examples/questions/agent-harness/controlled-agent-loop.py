"""Controlled agent loop state machine, deterministic stop conditions, and execution budgets.

Demonstrates:
1. Five-phase controlled execution loop: Context Assembly -> Model Invocation -> Tool Schema Validation -> Tool Execution -> Termination Evaluation.
2. Hard operational boundaries: Max iteration count, token budgets, and loop/stagnation detection.
3. Explicit terminal state modeling: COMPLETED, BUDGET_EXHAUSTED, LOOP_DETECTED, PERMISSION_DENIED.
"""
from typing import Any, Callable, Dict, List, Optional, Tuple
import json

class AgentExecutionState:
    INITIALIZING = "INITIALIZING"
    INVOKING_MODEL = "INVOKING_MODEL"
    VALIDATING_TOOL = "VALIDATING_TOOL"
    EXECUTING_TOOL = "EXECUTING_TOOL"
    EVALUATING_TERMINATION = "EVALUATING_TERMINATION"
    # Terminal states
    COMPLETED = "COMPLETED"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    LOOP_DETECTED = "LOOP_DETECTED"
    FAILED = "FAILED"

class ControlledAgentHarness:
    def __init__(self, max_iterations: int = 4, max_total_tokens: int = 5000):
        self.max_iterations = max_iterations
        self.max_tokens = max_total_tokens
        self.current_state = AgentExecutionState.INITIALIZING
        self.iterations = 0
        self.consumed_tokens = 0
        self.history: List[Dict[str, Any]] = []
        self._seen_tool_calls: List[str] = []

    def execute_loop(
        self,
        user_query: str,
        mock_model_responses: List[Dict[str, Any]],
        tools_registry: Dict[str, Callable[[Dict[str, Any]], str]]
    ) -> Dict[str, Any]:
        self.history.append({"role": "user", "content": user_query})
        response_idx = 0

        while True:
            # 1. Budget & Iteration Bound Checks
            if self.iterations >= self.max_iterations:
                self.current_state = AgentExecutionState.BUDGET_EXHAUSTED
                return self._finalize_run("Exceeded maximum iteration limit.")

            if self.consumed_tokens >= self.max_tokens:
                self.current_state = AgentExecutionState.BUDGET_EXHAUSTED
                return self._finalize_run("Exceeded maximum token budget.")

            self.iterations += 1
            self.current_state = AgentExecutionState.INVOKING_MODEL

            # 2. Invoke Model (Simulated)
            if response_idx >= len(mock_model_responses):
                self.current_state = AgentExecutionState.FAILED
                return self._finalize_run("Model stopped producing output without terminal answer.")

            model_turn = mock_model_responses[response_idx]
            response_idx += 1
            self.consumed_tokens += model_turn.get("tokens_used", 100)

            # Check if model returned final text
            if "final_answer" in model_turn:
                self.history.append({"role": "assistant", "content": model_turn["final_answer"]})
                self.current_state = AgentExecutionState.COMPLETED
                return self._finalize_run("Goal achieved successfully.")

            # 3. Tool Extraction and Schema Validation
            self.current_state = AgentExecutionState.VALIDATING_TOOL
            tool_call = model_turn.get("tool_call")
            if not tool_call or "name" not in tool_call:
                self.current_state = AgentExecutionState.FAILED
                return self._finalize_run("Model output malformed tool call.")

            tool_name = tool_call["name"]
            tool_args = tool_call.get("arguments", {})

            # 4. Loop & Stagnation Detection
            call_signature = f"{tool_name}:{json.dumps(tool_args, sort_keys=True)}"
            if self._seen_tool_calls.count(call_signature) >= 2:
                # Stagnant loop detected: identical tool call repeated 3 times
                self.current_state = AgentExecutionState.LOOP_DETECTED
                return self._finalize_run(f"Stagnation detected: Repeated tool call '{tool_name}' with identical parameters.")
            self._seen_tool_calls.append(call_signature)

            # 5. Tool Execution
            self.current_state = AgentExecutionState.EXECUTING_TOOL
            if tool_name not in tools_registry:
                # Tool error returned as observation to model context
                observation = f"Error: Tool '{tool_name}' is not in authorized registry."
            else:
                try:
                    observation = tools_registry[tool_name](tool_args)
                except Exception as ex:
                    observation = f"Execution Exception: {str(ex)}"

            # Append assistant proposal and tool observation to history
            self.history.append({"role": "assistant", "tool_call": tool_call})
            self.history.append({"role": "tool", "name": tool_name, "content": observation})

            self.current_state = AgentExecutionState.EVALUATING_TERMINATION

    def _finalize_run(self, explanation: str) -> Dict[str, Any]:
        return {
            "terminal_state": self.current_state,
            "explanation": explanation,
            "total_iterations": self.iterations,
            "total_tokens_consumed": self.consumed_tokens,
            "transcript_turns": len(self.history)
        }

if __name__ == "__main__":
    # Tools
    def search_docs(args):
        return json.dumps([{"title": "Pricing 2026", "content": "Enterprise seat: $40/mo"}])

    tools = {"search_docs": search_docs}

    # Test 1: Successful completion in 2 turns
    harness1 = ControlledAgentHarness(max_iterations=4)
    run1 = harness1.execute_loop(
        user_query="What is enterprise pricing?",
        mock_model_responses=[
            {"tool_call": {"name": "search_docs", "arguments": {"query": "enterprise pricing"}}, "tokens_used": 150},
            {"final_answer": "Enterprise seat pricing is $40 per month.", "tokens_used": 200}
        ],
        tools_registry=tools
    )
    assert run1["terminal_state"] == AgentExecutionState.COMPLETED
    assert run1["total_iterations"] == 2
    assert "Enterprise seat" in harness1.history[-1]["content"]

    # Test 2: Hard iteration limit reached
    harness2 = ControlledAgentHarness(max_iterations=2)
    run2 = harness2.execute_loop(
        user_query="Run forever",
        mock_model_responses=[
            {"tool_call": {"name": "search_docs", "arguments": {"query": "q1"}}, "tokens_used": 100},
            {"tool_call": {"name": "search_docs", "arguments": {"query": "q2"}}, "tokens_used": 100},
            {"tool_call": {"name": "search_docs", "arguments": {"query": "q3"}}, "tokens_used": 100}
        ],
        tools_registry=tools
    )
    assert run2["terminal_state"] == AgentExecutionState.BUDGET_EXHAUSTED
    assert run2["total_iterations"] == 2

    # Test 3: Loop / Stagnation Detection halts run
    harness3 = ControlledAgentHarness(max_iterations=10)
    run3 = harness3.execute_loop(
        user_query="Stuck loop",
        mock_model_responses=[
            {"tool_call": {"name": "search_docs", "arguments": {"query": "stuck"}}},
            {"tool_call": {"name": "search_docs", "arguments": {"query": "stuck"}}},
            {"tool_call": {"name": "search_docs", "arguments": {"query": "stuck"}}}
        ],
        tools_registry=tools
    )
    assert run3["terminal_state"] == AgentExecutionState.LOOP_DETECTED
    assert "Stagnation detected" in run3["explanation"]

    print("Controlled agent loop state machine and termination bounds verified successfully.")
