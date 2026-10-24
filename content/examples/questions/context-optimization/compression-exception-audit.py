"""Demonstrate prompt compression audits: proving extractive compaction preserves decisive exceptions."""

def extract_essential_constraints(text):
    """Detect presence of critical legal modifiers, exceptions, and negations."""
    negation_signals = ["except", "unless", "excluding", "not allowed", "non-refundable", "must"]
    found = [sig for sig in negation_signals if sig in text.lower()]
    return set(found)

def naive_extractive_compress(text, compression_ratio=0.5):
    """
    FLAWED COMPRESSION:
    Compresses text by naive sentence truncation or aggressive perplexity pruning,
    accidentally removing subordinate qualification clauses.
    """
    sentences = text.split(". ")
    # Keeps only the first 50% of sentences, discarding the trailing exception clause:
    cutoff = max(1, int(len(sentences) * compression_ratio))
    return ". ".join(sentences[:cutoff]) + "."

def audited_safe_compress(text, required_exceptions):
    """
    AUDITED SAFE COMPRESSION:
    Enforces a pre-flight / post-flight regression check ensuring all required
    statutory exceptions and negation qualifiers survive the compression pipeline.
    """
    # Verify input text contains the exceptions:
    input_signals = extract_essential_constraints(text)
    for exp in required_exceptions:
        if exp not in input_signals:
            raise ValueError(f"Input text missing mandatory exception: {exp}")

    # Compression with constraint preservation:
    sentences = text.split(". ")
    kept = []
    for s in sentences:
        # Always retain sentences carrying exception signals:
        if any(sig in s.lower() for sig in required_exceptions):
            kept.append(s)
        elif len(kept) < 2:
            kept.append(s)

    compressed = ". ".join(kept)
    
    # Audit invariant: All required exception signals MUST be present in output:
    output_signals = extract_essential_constraints(compressed)
    missing = set(required_exceptions) - output_signals
    if missing:
        raise AssertionError(f"Regression detected! Decisive exception pruned: {missing}")

    return compressed

source_policy = (
    "Annual enterprise subscriptions renew automatically on December 31. "
    "Payments are processed through corporate invoice billing. "
    "Refunds are strictly non-refundable unless cancellation is submitted within 14 days of renewal."
)

required_negations = ["non-refundable", "unless"]

# 1. Flawed compression test (prunes trailing exception):
flawed_result = naive_extractive_compress(source_policy, 0.6)
assert "non-refundable" not in flawed_result, "Naive compression pruned decisive exception!"

# 2. Audited safe compression preserves the exception:
safe_result = audited_safe_compress(source_policy, required_negations)
assert "non-refundable" in safe_result and "unless" in safe_result

print(f"Compression audit verified: naive_pruned={flawed_result != source_policy}, safe_exception_preserved=True")

