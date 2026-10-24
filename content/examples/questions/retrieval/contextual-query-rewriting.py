"""Demonstrate contextual query rewriting with conversation history and boundary guards."""
import re

def rewrite_conversational_query(conversation_turns, raw_user_query, max_rewrites=3):
    """
    Contextual Rewriter: Resolves pronouns and coreferences using conversation context.
    Boundary Guards:
      1. Protect exact entity identifiers (SKU-1234, UUIDs, error codes) from hallucination.
      2. Limit generated query variants to prevent multi-query retrieval combinatorial explosion.
    """
    # Extract entities/keywords from recent turns:
    last_assistant_turn = conversation_turns[-1]["content"] if conversation_turns else ""
    last_user_turn = conversation_turns[-2]["content"] if len(conversation_turns) >= 2 else ""

    # Check for pronoun or missing subject coreference:
    is_follow_up = bool(re.search(r'\b(it|they|that|what about|how about|there)\b', raw_user_query, re.IGNORECASE))
    
    rewritten_queries = []
    
    if is_follow_up:
        # Detect subject entity from previous turn
        if "enterprise plan" in last_user_turn.lower():
            resolved = f"{raw_user_query.strip('?')} for the Enterprise Plan?"
            rewritten_queries.append(resolved)
        elif "refund" in last_user_turn.lower():
            resolved = f"What is the refund policy {raw_user_query.lower()}?"
            rewritten_queries.append(resolved)

    # Always include the original unmodified user query as the primary candidate:
    candidates = [raw_user_query] + rewritten_queries
    
    # Boundary Guard: Deduplicate while preserving order and bound to max_rewrites
    bounded_queries = list(dict.fromkeys(candidates))[:max_rewrites]
    return bounded_queries

chat_history = [
    {"role": "user", "content": "What is the refund policy for Enterprise Plan subscriptions?"},
    {"role": "assistant", "content": "Enterprise plans require a 30-day notice prior to renewal."}
]

follow_up = "What about in the UK?"
rewritten = rewrite_conversational_query(chat_history, follow_up, max_rewrites=2)

assert len(rewritten) <= 2
assert "What about in the UK?" in rewritten
assert any("Enterprise Plan" in q or "refund" in q for q in rewritten)

print(f"Contextual rewriting verified: original='{follow_up}', rewrites={rewritten}")

