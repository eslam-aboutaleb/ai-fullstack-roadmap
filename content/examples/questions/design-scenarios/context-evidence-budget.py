"""Token-ledger fixture, not a tokenizer or retrieval-quality evaluator."""
def evidence_budget(window, output, instructions, history, margin):
    values = (window, output, instructions, history, margin)
    if any(type(value) is not int or value < 0 for value in values):
        raise ValueError("Token counts must be nonnegative integers")
    remaining = window - output - instructions - history - margin
    if remaining < 0:
        raise ValueError("Fixed request overhead exceeds the window")
    return remaining

budget = evidence_budget(32_000, 4_000, 2_000, 2_000, 2_000)
# Counts include source labels and separators; candidates are already reranked.
candidates = [("rule", 12_000), ("exception", 7_000), ("background", 8_000)]
selected = []
used = 0
for name, tokens in candidates:
    if used + tokens <= budget:
        selected.append(name)
        used += tokens
assert selected == ["rule", "exception"] and used <= budget
try:
    evidence_budget(10, 8, 3, 0, 0)
except ValueError:
    pass
else:
    raise AssertionError("Over-budget fixed overhead must fail")
print(budget, selected, used)
