"""Benchmark an AI RAG pipeline against a deterministic non-AI baseline to justify ROI and complexity."""

def evaluate_system_roi():
    """
    To justify deploying a complex generative AI system, engineering teams must benchmark
    against a deterministic baseline (e.g. Postgres Full-Text Search + regex rule extractor).
    """
    deterministic_baseline = {
        "name": "Postgres FTS + Keyword Rule Matcher",
        "accuracy": 0.78,                  # Resolves 78% of standard support requests
        "latency_p95_ms": 12,              # 12 milliseconds
        "monthly_infrastructure_cost": 85, # Standard database compute
        "maintenance_overhead": "low"
    }

    ai_rag_system = {
        "name": "Hybrid RAG + LLM Synthesis",
        "accuracy": 0.92,                  # Resolves 92% of queries (14% absolute gain)
        "latency_p95_ms": 840,             # 840 milliseconds (70x slower!)
        "monthly_infrastructure_cost": 1420, # Vector DB + GPU Model API spend
        "maintenance_overhead": "high"
    }

    # Business ROI Calculation:
    # Company receives 50,000 queries/month.
    # An unresolved query requires a human support ticket costing $6.00 to resolve manually.
    monthly_queries = 50_000
    human_ticket_cost = 6.00

    # Baseline cost:
    baseline_unresolved = monthly_queries * (1.0 - deterministic_baseline["accuracy"])
    baseline_total_cost = (baseline_unresolved * human_ticket_cost) + deterministic_baseline["monthly_infrastructure_cost"]

    # AI system cost:
    ai_unresolved = monthly_queries * (1.0 - ai_rag_system["accuracy"])
    ai_total_cost = (ai_unresolved * human_ticket_cost) + ai_rag_system["monthly_infrastructure_cost"]

    monthly_savings = baseline_total_cost - ai_total_cost
    annual_net_roi = monthly_savings * 12

    return {
        "baseline_total_cost": baseline_total_cost,
        "ai_total_cost": ai_total_cost,
        "monthly_net_savings": monthly_savings,
        "annual_net_roi": annual_net_roi,
        "justified": annual_net_roi > 0
    }

roi = evaluate_system_roi()

# Baseline total: (11,000 tickets * $6) + $85 = $66,085/mo
# AI total: (4,000 tickets * $6) + $1,420 = $25,420/mo
# Monthly savings = $40,665/mo ($487,980/year) -> Strong ROI despite 70x higher latency!
assert roi["justified"] is True
assert roi["annual_net_roi"] > 400_000

print(f"Non-AI baseline ROI verified: baseline_cost=${roi['baseline_total_cost']}/mo, ai_cost=${roi['ai_total_cost']}/mo, annual_roi=${roi['annual_net_roi']}")

