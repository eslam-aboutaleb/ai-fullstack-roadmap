"""Calculate dynamic token budgets with guaranteed generation headroom and knapsack evidence packing."""

class ContextBudgetManager:
    def __init__(self, model_context_limit=8192, reserved_output_tokens=2048, safety_buffer=256):
        self.model_context_limit = model_context_limit
        self.reserved_output_tokens = reserved_output_tokens
        self.safety_buffer = safety_buffer
        
        # Fixed input overhead:
        self.max_input_allowance = model_context_limit - reserved_output_tokens - safety_buffer
        if self.max_input_allowance <= 0:
            raise ValueError("Invalid budget: reserved output and safety buffer exceed context limit")

    def allocate_budget(self, system_prompt_tokens, tool_schema_tokens, history_tokens, candidate_passages):
        """
        Dynamically calculate remaining token budget for RAG evidence passages:
        Total Input = System + Tools + History + Evidence <= Max Input Allowance
        """
        fixed_overhead = system_prompt_tokens + tool_schema_tokens + history_tokens
        if fixed_overhead >= self.max_input_allowance:
            raise ValueError(f"Prompt overhead ({fixed_overhead}) exhausted total input budget ({self.max_input_allowance})")

        evidence_budget = self.max_input_allowance - fixed_overhead
        
        # Greedy Knapsack Packing for Evidence Passages (ordered by relevance score)
        admitted_passages = []
        spent_evidence_tokens = 0

        for passage in candidate_passages:
            cost = passage["token_count"]
            if spent_evidence_tokens + cost <= evidence_budget:
                admitted_passages.append(passage["id"])
                spent_evidence_tokens += cost
            else:
                # Discard or truncate remaining lower-ranked evidence
                continue

        total_input_tokens = fixed_overhead + spent_evidence_tokens
        return {
            "total_input_tokens": total_input_tokens,
            "evidence_budget": evidence_budget,
            "spent_evidence_tokens": spent_evidence_tokens,
            "admitted_passages": admitted_passages,
            "guaranteed_generation_headroom": self.reserved_output_tokens
        }

budget_mgr = ContextBudgetManager(model_context_limit=8192, reserved_output_tokens=2048, safety_buffer=256)

candidates = [
    {"id": "doc_1_high_relevance", "token_count": 800},
    {"id": "doc_2_mid_relevance", "token_count": 1200},
    {"id": "doc_3_low_relevance", "token_count": 2500} # Exceeds remaining budget
]

allocation = budget_mgr.allocate_budget(
    system_prompt_tokens=650,
    tool_schema_tokens=850,
    history_tokens=1500,
    candidate_passages=candidates
)

# Max input allowance = 8192 - 2048 - 256 = 5888 tokens
# Fixed overhead = 650 + 850 + 1500 = 3000 tokens
# Evidence budget = 5888 - 3000 = 2888 tokens
# Passages admitted: doc_1 (800) + doc_2 (1200) = 2000 tokens (doc_3 discarded because 2000 + 2500 > 2888)
assert allocation["admitted_passages"] == ["doc_1_high_relevance", "doc_2_mid_relevance"]
assert allocation["total_input_tokens"] <= 5888
assert allocation["guaranteed_generation_headroom"] == 2048

print(f"Dynamic budget allocation verified: input={allocation['total_input_tokens']}/5888, headroom={allocation['guaranteed_generation_headroom']}, admitted={allocation['admitted_passages']}")
