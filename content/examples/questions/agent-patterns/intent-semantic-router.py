"""Intent Semantic Router Pattern.

Demonstrates:
1. Multi-tier hierarchical routing:
   - Tier 1: Deterministic regex fast-path for structured queries (e.g., ORDER-12345, INV-987).
   - Tier 2: Semantic vector similarity with confidence threshold across domain routes (Billing, TechDocs, HR).
   - Tier 3: Explicit Ambiguity / Fallback routing when confidence is below threshold or margin is too tight.
2. Route-isolated execution: downstream specialists receive only their domain context, preventing prompt
   dilution and tool schema bloat.
3. Testable decision verification: evaluates routing accuracy independently from specialist execution.
"""

from dataclasses import dataclass
import math
import re
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class RouteDecision:
    route_name: str
    tier: str  # "regex_fastpath", "semantic_classifier", "fallback_ambiguity"
    confidence: float
    extracted_params: Dict[str, Any]
    reason: str


class SimpleEmbeddingModel:
    """Lightweight deterministic TF-IDF / term-hash embedding simulator for testing."""

    VOCAB = {
        "invoice": 0, "bill": 1, "payment": 2, "charge": 3, "credit": 4, "refund": 5,
        "api": 6, "endpoint": 7, "token": 8, "auth": 9, "sdk": 10, "error": 11,
        "pto": 12, "vacation": 13, "sick": 14, "health": 15, "benefits": 16, "holiday": 17
    }

    @classmethod
    def embed(cls, text: str) -> List[float]:
        vec = [0.0] * len(cls.VOCAB)
        words = re.findall(r"\w+", text.lower())
        for word in words:
            if word in cls.VOCAB:
                vec[cls.VOCAB[word]] += 1.0

        # L2 normalize
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    dot = sum(a * b for a, b in zip(v1, v2))
    return dot


class HierarchicalIntentRouter:
    """Production-grade intent routing engine with fallback safety."""

    ROUTE_PROTOTYPES = {
        "billing_specialist": "invoice bill payment charge credit card refund transaction statement",
        "technical_support": "api endpoint token auth authentication sdk error status code 500",
        "hr_benefits": "pto vacation sick leave health dental insurance benefits holiday calendar"
    }

    CONFIDENCE_THRESHOLD = 0.45
    AMBIGUITY_MARGIN = 0.08  # If top two routes are within 0.08, mark ambiguous

    def __init__(self):
        # Precompute prototype vectors
        self.route_vectors = {
            route: SimpleEmbeddingModel.embed(prototype)
            for route, prototype in self.ROUTE_PROTOTYPES.items()
        }

    def route(self, user_query: str) -> RouteDecision:
        query_clean = user_query.strip()

        # --- Tier 1: Deterministic Regex Fast-Path ---
        order_match = re.search(r"\b(ORDER|INV)-\d{4,8}\b", query_clean, re.IGNORECASE)
        if order_match:
            return RouteDecision(
                route_name="order_lookup_service",
                tier="regex_fastpath",
                confidence=1.0,
                extracted_params={"reference_id": order_match.group(0).upper()},
                reason="Matched exact transactional reference pattern"
            )

        api_key_match = re.search(r"\b(sk-[a-zA-Z0-9]{16,})\b", query_clean)
        if api_key_match:
            return RouteDecision(
                route_name="security_revocation_service",
                tier="regex_fastpath",
                confidence=1.0,
                extracted_params={"token_prefix": api_key_match.group(0)[:8] + "..."},
                reason="Detected exposed API secret key in prompt"
            )

        # --- Tier 2: Semantic Vector Classifier ---
        query_vec = SimpleEmbeddingModel.embed(query_clean)
        scores: List[Tuple[str, float]] = []
        for route_name, route_vec in self.route_vectors.items():
            sim = cosine_similarity(query_vec, route_vec)
            scores.append((route_name, sim))

        scores.sort(key=lambda x: x[1], reverse=True)
        top_route, top_score = scores[0]
        second_route, second_score = scores[1]

        # Tier 3 Check: Below minimum confidence threshold
        if top_score < self.CONFIDENCE_THRESHOLD:
            return RouteDecision(
                route_name="general_clarification_agent",
                tier="fallback_ambiguity",
                confidence=top_score,
                extracted_params={"scores": dict(scores)},
                reason=f"Top score {top_score:.3f} below acceptance threshold {self.CONFIDENCE_THRESHOLD}"
            )

        # Tier 3 Check: Ambiguous multiclass separation (too close)
        if (top_score - second_score) < self.AMBIGUITY_MARGIN:
            return RouteDecision(
                route_name="general_clarification_agent",
                tier="fallback_ambiguity",
                confidence=top_score,
                extracted_params={"candidates": [top_route, second_route], "scores": dict(scores)},
                reason=f"Ambiguous intent: margin {top_score - second_score:.3f} is less than {self.AMBIGUITY_MARGIN}"
            )

        # High confidence single route
        return RouteDecision(
            route_name=top_route,
            tier="semantic_classifier",
            confidence=top_score,
            extracted_params={"scores": dict(scores)},
            reason="Semantic vector matched dedicated specialist route"
        )


def main():
    router = HierarchicalIntentRouter()

    test_cases = [
        # 1. Deterministic Fast-path
        ("Check tracking status for INV-98421 immediately", "order_lookup_service", "regex_fastpath"),
        # 2. Semantic Billing
        ("Why was my credit card charged twice for last month's invoice?", "billing_specialist", "semantic_classifier"),
        # 3. Semantic Tech Docs
        ("Our API client keeps getting 500 error on the auth token endpoint", "technical_support", "semantic_classifier"),
        # 4. Semantic HR
        ("How many sick days and PTO vacation hours do I have left this year?", "hr_benefits", "semantic_classifier"),
        # 5. Low confidence query -> Clarification fallback
        ("Hello, who made this application?", "general_clarification_agent", "fallback_ambiguity"),
    ]

    print("Intent Router Evaluation:")
    for query, expected_route, expected_tier in test_cases:
        decision = router.route(query)
        print(f"\nQuery: '{query}'")
        print(f"  -> Routed To: {decision.route_name} (Tier: {decision.tier}, Conf: {decision.confidence:.2f})")
        print(f"  -> Reason: {decision.reason}")
        if decision.extracted_params:
            print(f"  -> Params: {decision.extracted_params}")

        assert decision.route_name == expected_route, f"Expected {expected_route}, got {decision.route_name}"
        assert decision.tier == expected_tier, f"Expected tier {expected_tier}, got {decision.tier}"

    print("\nAll routing tiers verified successfully.")


if __name__ == "__main__":
    main()

