"""Demonstrate Lost-in-the-Middle attention bias and U-shaped context reranking."""

def u_shaped_context_rerank(ranked_documents):
    """
    Mitigate Liu et al. 'Lost in the Middle' attention degradation.
    Transformer decoder attention is highest at:
      1. Primacy position (earliest tokens in prompt context).
      2. Recency position (latest tokens immediately preceding generation).
    Attention degrades significantly for information located in the middle (30%-70% depth).
    
    U-Shaped ordering places:
      Rank 1 (Most relevant) -> Top (Position 0)
      Rank 2 (Second most relevant) -> Bottom (Last position)
      Rank 3 -> Position 1
      Rank 4 -> Second to last position
      ... least relevant documents placed in the low-attention center.
    """
    ordered = [None] * len(ranked_documents)
    left = 0
    right = len(ranked_documents) - 1

    for i, doc in enumerate(ranked_documents):
        if i % 2 == 0:
            ordered[left] = doc
            left += 1
        else:
            ordered[right] = doc
            right -= 1

    return ordered

# 5 retrieved documents sorted by relevance score (doc_1 is decisive evidence, doc_5 is marginal)
candidates = ["doc_1_best", "doc_2_high", "doc_3_mid", "doc_4_low", "doc_5_lowest"]

u_shaped = u_shaped_context_rerank(candidates)

# Expected U-shaped distribution:
# Index 0 (Primacy - High Attention): doc_1_best
# Index 4 (Recency - High Attention): doc_2_high
# Index 1: doc_3_mid
# Index 3: doc_4_low
# Index 2 (Center - Low Attention): doc_5_lowest
assert u_shaped[0] == "doc_1_best", "Best document placed at primacy position"
assert u_shaped[-1] == "doc_2_high", "Second best document placed at recency position"
assert u_shaped[2] == "doc_5_lowest", "Lowest scoring document placed in center"

print(f"U-shaped reranking verified: original={candidates} -> u_shaped={u_shaped}")
