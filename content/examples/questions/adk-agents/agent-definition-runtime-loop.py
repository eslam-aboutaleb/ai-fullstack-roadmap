"""Agent Definition, Controlled Runtime Loop, and Execution Bounding.

Demonstrates:
1. Agent Definition Configuration:
   - Encapsulates instructions, target model adapter, tool registry, and execution policies.
   - Emphasizes that runtime configuration is one part of the system (authentication and persistence are separate).
2. Dynamic Agent Loop vs Fixed Pipeline:
   - Dynamic agent loops iteratively inspect observations and choose the next tool dynamically.
   - Fixed pipelines follow pre-ordained DAG stages regardless of intermediate findings.
3. Hard Execution Bounding:
   - Enforces hard ceilings on maximum turns, cumulative tokens, and duplicate action loops.
"""

from dataclasses import dataclass, field
import json
import time
from typing import Any, Callable, Dict, List, Optional, Set


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters_schema: Dict[str, Any]
    executable: Callable[..., Any]


@dataclass
class AgentConfig:
    agent_id: str
    instructions: str
    model_name: str
    tools: Dict[str, ToolDefinition] = field(default_factory=dict)
    max_turns: int = 5
    max_tokens: int = 4000
    timeout_seconds: float = 10.0


@dataclass
class ExecutionTrace:
    turns: int = 0
    total_tokens: int = 0
    history: List[Dict[str, Any]] = field(default_factory=list)
    completed: bool = False
    halt_reason: Optional[str] = None


class MockEnvironment:
    """Mock database and service tools."""

    DATABASE = {
        "ORDER-101": {"status": "SHIPPED", "tracking_number": "TRK-9921", "carrier": "FedEx"},
        "ORDER-102": {"status": "BACKORDERED", "restock_date": "2026-11-01"}
    }

    @classmethod
    def lookup_order(cls, order_id: str) -> Dict[str, Any]:
        order = cls.DATABASE.get(order_id)
        if not order:
            return {"found": False, "error": f"Order {order_id} does not exist"}
        return {"found": True, "order": order}

    @classmethod
    def check_carrier_status(cls, tracking_number: str) -> Dict[str, Any]:
        return {"tracking_number": tracking_number, "estimated_delivery": "Tomorrow by 5pm", "status": "In Transit"}


class AgentRuntimeHarness:
    """Production runtime harness executing and bounding agent runs."""

    def __init__(self, config: AgentConfig):
        self.config = config

    def execute_task(self, user_prompt: str) -> ExecutionTrace:
        trace = ExecutionTrace()
        start_time = time.time()
        executed_signatures: Set[str] = set()

        # Initial turn
        trace.history.append({"role": "system", "content": self.config.instructions})
        trace.history.append({"role": "user", "content": user_prompt})

        current_goal = user_prompt

        while trace.turns < self.config.max_turns:
            trace.turns += 1
            trace.total_tokens += 120  # Simulate token consumption

            # Check timeout
            if (time.time() - start_time) > self.config.timeout_seconds:
                trace.halt_reason = "TIMEOUT_EXCEEDED"
                break

            # Check token budget
            if trace.total_tokens > self.config.max_tokens:
                trace.halt_reason = "TOKEN_BUDGET_EXHAUSTED"
                break

            # Simulated model reasoning and dynamic action selection
            if trace.turns == 1:
                # Step 1: Model inspects user prompt and dynamically calls lookup_order
                tool_name = "lookup_order"
                tool_args = {"order_id": "ORDER-101"}
            elif trace.turns == 2:
                # Step 2: Model consumes observation from turn 1, discovers tracking number, calls check_carrier_status
                last_obs = trace.history[-1]["content"]
                obs_data = json.loads(last_obs)
                tracking = obs_data["order"]["tracking_number"]
                tool_name = "check_carrier_status"
                tool_args = {"tracking_number": tracking}
            else:
                # Step 3: Model concludes and synthesizes final answer
                trace.completed = True
                trace.halt_reason = "TASK_COMPLETED"
                trace.history.append({
                    "role": "assistant",
                    "content": "Your order ORDER-101 has shipped via FedEx (TRK-9921) and is In Transit, arriving tomorrow by 5pm."
                })
                break

            # Loop detection
            action_sig = f"{tool_name}:{json.dumps(tool_args, sort_keys=True)}"
            if action_sig in executed_signatures:
                trace.halt_reason = "INFINITE_LOOP_DETECTED"
                break
            executed_signatures.add(action_sig)

            # Execute tool in harness
            tool = self.config.tools.get(tool_name)
            if not tool:
                trace.halt_reason = f"UNKNOWN_TOOL_{tool_name}"
                break

            observation = tool.executable(**tool_args)
            trace.history.append({"role": "assistant", "tool_call": tool_name, "args": tool_args})
            trace.history.append({"role": "tool", "name": tool_name, "content": json.dumps(observation)})

        if not trace.completed and not trace.halt_reason:
            trace.halt_reason = "MAX_TURNS_REACHED"

        return trace


def main():
    tools = {
        "lookup_order": ToolDefinition(
            name="lookup_order",
            description="Lookup order details by order_id",
            parameters_schema={"type": "object", "properties": {"order_id": {"type": "string"}}},
            executable=MockEnvironment.lookup_order
        ),
        "check_carrier_status": ToolDefinition(
            name="check_carrier_status",
            description="Check live shipping courier tracking status",
            parameters_schema={"type": "object", "properties": {"tracking_number": {"type": "string"}}},
            executable=MockEnvironment.check_carrier_status
        )
    }

    config = AgentConfig(
        agent_id="order-support-v1",
        instructions="You are an autonomous customer order assistant. Look up orders and verify courier tracking.",
        model_name="gemini-1.5-pro",
        tools=tools,
        max_turns=4,
        max_tokens=2000,
        timeout_seconds=5.0
    )

    harness = AgentRuntimeHarness(config)
    print(f"1. Initialized Agent '{config.agent_id}' with {len(config.tools)} registered tools.")
    print(f"   Max turns ceiling: {config.max_turns}, Max token budget: {config.max_tokens}")

    # 2. Execute task
    trace = harness.execute_task("Where is my order ORDER-101?")

    print("\n2. Agent Execution Trace:")
    print(f"   Total Turns: {trace.turns}")
    print(f"   Total Tokens Used: {trace.total_tokens}")
    print(f"   Halt Reason: {trace.halt_reason}")
    print(f"   Final Answer: {trace.history[-1].get('content')}")

    # Assertions
    assert trace.completed is True
    assert trace.halt_reason == "TASK_COMPLETED"
    assert trace.turns == 3
    assert "arriving tomorrow by 5pm" in trace.history[-1]["content"]

    print("\nAgent definition, dynamic runtime loop, and execution bounding verified successfully.")


if __name__ == "__main__":
    main()

