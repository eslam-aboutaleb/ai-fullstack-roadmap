"""
capstone-production-evidence-verifier.py

Production-grade Capstone Engineering Evidence and Threat Model Verification Suite.
Demonstrates the rigorous architectural properties that separate an authentic, production-grade
AI engineering capstone from a shallow tutorial copy:
1. Multi-Tenant Scoped Caching: Ensuring prompt/completion caches are strictly tenant-keyed,
   preventing Tenant B from accessing cached answers derived from Tenant A's private documents.
2. Robust Streaming Protocol Framing: Emitting deterministic terminal frames ([DONE] or typed
   in-band errors) to prevent client UI hangs during mid-stream inference failures.
3. Receiver-Side Idempotent Mutation: Ensuring duplicate event dispatches (e.g., retried webhooks)
   commit exactly once in durable storage.
4. Quantitative Evaluation Auditing: Demanding reproducible, automated regression assertions
   rather than subjective happy-path manual demos.
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
import hashlib


@dataclass
class StreamFrame:
    event_type: str
    data: str
    is_terminal: bool = False


class ProductionCapstoneHarness:
    def __init__(self):
        # 1. Tenant-scoped cache: Key = hash(tenant_id || prompt_hash)
        self.semantic_cache: Dict[str, str] = {}
        # 2. Durable storage with idempotency ledger
        self.committed_mutations: Dict[str, Dict[str, Any]] = {}
        self.processed_idempotency_keys: Set[str] = set()

    def _cache_key(self, tenant_id: str, prompt: str) -> str:
        prompt_digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        return f"{tenant_id}:{prompt_digest}"

    def get_or_set_cached_answer(self, tenant_id: str, prompt: str, generated_answer: str) -> Tuple[str, bool]:
        """
        Retrieves cached response strictly within tenant boundary.
        Returns (answer, is_cache_hit).
        """
        key = self._cache_key(tenant_id, prompt)
        if key in self.semantic_cache:
            return self.semantic_cache[key], True
        self.semantic_cache[key] = generated_answer
        return generated_answer, False

    def simulate_streaming_lifecycle(self, chunks: List[str], inject_error: bool = False) -> List[StreamFrame]:
        """
        Streams response chunks with guaranteed terminal framing ([DONE] or typed error),
        preventing client socket hangs.
        """
        frames: List[StreamFrame] = []
        for i, chunk in enumerate(chunks):
            if inject_error and i == 2:
                # Mid-stream failure: emit typed error frame and close terminal boundary
                frames.append(StreamFrame(event_type="error", data="upstream_provider_timeout", is_terminal=True))
                return frames
            frames.append(StreamFrame(event_type="token", data=chunk, is_terminal=False))

        # Normal completion: emit terminal sentinel
        frames.append(StreamFrame(event_type="done", data="[DONE]", is_terminal=True))
        return frames

    def execute_idempotent_task(self, idempotency_key: str, task_id: str, payload: str) -> Dict[str, Any]:
        """
        Guarantees that duplicate network retries do not duplicate state mutations.
        """
        if idempotency_key in self.processed_idempotency_keys:
            # Replay previous commit without re-executing side-effects
            return {
                "status": "REPLAYED",
                "task_id": task_id,
                "data": self.committed_mutations[task_id]["payload"]
            }

        self.processed_idempotency_keys.add(idempotency_key)
        mutation = {
            "task_id": task_id,
            "payload": payload,
            "idempotency_key": idempotency_key
        }
        self.committed_mutations[task_id] = mutation
        return {"status": "COMMITTED", "task_id": task_id, "data": payload}


def main() -> None:
    print("=== Testing Capstone Production Evidence & Invariant Verifier ===")
    harness = ProductionCapstoneHarness()

    # Invariant 1: Cross-Tenant Cache Isolation
    prompt = "What is the internal reimbursement rate for travel meals?"
    ans_tenant_a = "Tenant A Rate: $75 per day (Executive tier)."

    # Tenant A generates and caches the answer
    _, is_hit_a1 = harness.get_or_set_cached_answer("tenant_alpha", prompt, ans_tenant_a)
    assert is_hit_a1 is False
    _, is_hit_a2 = harness.get_or_set_cached_answer("tenant_alpha", prompt, ans_tenant_a)
    assert is_hit_a2 is True  # Cache hit for Tenant A

    # Tenant B submits the exact same prompt: MUST be a cache miss!
    _, is_hit_b = harness.get_or_set_cached_answer("tenant_beta", prompt, "Tenant B Rate: $45 per day.")
    print("Cross-Tenant Cache Isolation Check:")
    print(f"  Tenant A Cache Hit: {is_hit_a2}")
    print(f"  Tenant B Cache Hit on Same Query: {is_hit_b} (Zero Data Leakage)")
    assert is_hit_b is False, "Tenant B must never hit Tenant A's private cache entry!"

    # Invariant 2: Streaming Protocol Terminal Framing
    normal_stream = harness.simulate_streaming_lifecycle(["Hello", ", ", "world", "!"])
    assert normal_stream[-1].is_terminal is True
    assert normal_stream[-1].data == "[DONE]"

    error_stream = harness.simulate_streaming_lifecycle(["Hello", ", ", "world", "!"], inject_error=True)
    print("\nStreaming Error Boundary Check:")
    print(f"  Mid-stream failure emitted terminal frame: {error_stream[-1].event_type} (is_terminal={error_stream[-1].is_terminal})")
    assert error_stream[-1].is_terminal is True
    assert error_stream[-1].event_type == "error"

    # Invariant 3: Receiver-Side Idempotency
    key = "idem_key_9988"
    run1 = harness.execute_idempotent_task(idempotency_key=key, task_id="task_1", payload="Refund $50")
    run2 = harness.execute_idempotent_task(idempotency_key=key, task_id="task_1", payload="Refund $50")
    print("\nReceiver-Side Idempotency Check:")
    print(f"  Attempt 1 Status: {run1['status']}")
    print(f"  Attempt 2 Status: {run2['status']} (Zero Duplicate Mutations)")
    assert run1["status"] == "COMMITTED"
    assert run2["status"] == "REPLAYED"
    assert len(harness.committed_mutations) == 1

    print("\nAll production capstone architectural invariants verified successfully.")


if __name__ == "__main__":
    main()
