def evidence_allowance(window, instructions, history, tools, output_reserve, margin):
    parts = [window, instructions, history, tools, output_reserve, margin]
    if any(x < 0 for x in parts): raise ValueError("negative budget")
    return max(0, window - sum(parts[1:]))
assert evidence_allowance(8000, 700, 1500, 900, 2000, 400) == 2500
# Count the actual rendered request with the compatible model tokenizer.
