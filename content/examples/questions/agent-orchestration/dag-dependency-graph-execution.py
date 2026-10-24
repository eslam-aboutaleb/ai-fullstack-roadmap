"""Directed Acyclic Graph (DAG) workflow engine, dependency topological ordering, and parallel branch execution.

Demonstrates:
1. Dependency graph representation: Mapping node inputs, upstream prerequisite dependencies, and topological ordering.
2. Parallel fan-out execution: Concurrently executing independent nodes whose dependencies are satisfied.
3. Concurrency bounds via Semaphores: Preventing resource exhaustion during large fan-outs.
4. Cycle detection in workflow graphs.
"""
from typing import Any, Callable, Dict, List, Optional, Set
import asyncio
import collections

class WorkflowDagNode:
    def __init__(self, name: str, action: Callable[[Dict[str, Any]], Any], dependencies: Optional[List[str]] = None):
        self.name = name
        self.action = action
        self.dependencies = set(dependencies or [])

class DagOrchestrator:
    def __init__(self, max_concurrency: int = 3):
        self.nodes: Dict[str, WorkflowDagNode] = {}
        self.semaphore = asyncio.Semaphore(max_concurrency)

    def add_node(self, node: WorkflowDagNode):
        self.nodes[node.name] = node

    def _detect_cycles(self) -> None:
        """Kahn's algorithm to detect cycles in the dependency graph."""
        in_degree = {name: len(node.dependencies) for name, node in self.nodes.items()}
        queue = collections.deque([name for name, deg in in_degree.items() if deg == 0])
        visited_count = 0

        # Build reverse dependency graph (upstream -> downstream children)
        downstream = collections.defaultdict(list)
        for name, node in self.nodes.items():
            for dep in node.dependencies:
                downstream[dep].append(name)

        while queue:
            curr = queue.popleft()
            visited_count += 1
            for child in downstream[curr]:
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)

        if visited_count != len(self.nodes):
            raise ValueError("Invalid Workflow: Cycle detected in dependency graph!")

    async def execute_dag(self) -> Dict[str, Any]:
        self._detect_cycles()
        completed_outputs: Dict[str, Any] = {}
        completed_events: Dict[str, asyncio.Event] = {name: asyncio.Event() for name in self.nodes}

        async def run_node(node: WorkflowDagNode):
            # 1. Wait for all upstream dependency events to finish
            for dep_name in node.dependencies:
                if dep_name not in completed_events:
                    raise KeyError(f"Missing dependency '{dep_name}' for node '{node.name}'")
                await completed_events[dep_name].wait()

            # 2. Gather outputs from dependencies as input
            node_inputs = {dep: completed_outputs[dep] for dep in node.dependencies}

            # 3. Execute action within concurrency bounds
            async with self.semaphore:
                result = await asyncio.to_thread(node.action, node_inputs)
                completed_outputs[node.name] = result
                completed_events[node.name].set()

        # Launch all nodes concurrently; dependency events regulate execution order
        tasks = [asyncio.create_task(run_node(node)) for node in self.nodes.values()]
        await asyncio.gather(*tasks)
        return completed_outputs

if __name__ == "__main__":
    orchestrator = DagOrchestrator(max_concurrency=4)

    # 1. Define nodes: fetch_user and fetch_account can run in parallel (fan-out)
    # generate_report depends on BOTH (fan-in)
    orchestrator.add_node(WorkflowDagNode(
        name="fetch_user",
        action=lambda inputs: {"user_id": "usr_42", "name": "Alice"}
    ))

    orchestrator.add_node(WorkflowDagNode(
        name="fetch_account",
        action=lambda inputs: {"account_id": "acc_99", "balance": 1500.0}
    ))

    orchestrator.add_node(WorkflowDagNode(
        name="fetch_compliance_policy",
        action=lambda inputs: {"kyc_verified": True}
    ))

    orchestrator.add_node(WorkflowDagNode(
        name="generate_report",
        action=lambda inputs: {
            "summary": f"{inputs['fetch_user']['name']} has balance ${inputs['fetch_account']['balance']:.2f}",
            "compliant": inputs['fetch_compliance_policy']['kyc_verified']
        },
        dependencies=["fetch_user", "fetch_account", "fetch_compliance_policy"]
    ))

    results = asyncio.run(orchestrator.execute_dag())
    assert "Alice" in results["generate_report"]["summary"]
    assert results["generate_report"]["compliant"] is True

    # 2. Cycle Detection Verification
    cyclic_orch = DagOrchestrator()
    cyclic_orch.add_node(WorkflowDagNode("A", lambda i: "A", dependencies=["B"]))
    cyclic_orch.add_node(WorkflowDagNode("B", lambda i: "B", dependencies=["A"]))
    try:
        asyncio.run(cyclic_orch.execute_dag())
        assert False, "Should have thrown ValueError for cycle"
    except ValueError as ve:
        assert "Cycle detected" in str(ve)

    print("DAG workflow dependency engine and parallel execution verified successfully.")
