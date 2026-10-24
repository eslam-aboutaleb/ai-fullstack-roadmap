spans, merged = [(0, 10), (8, 15), (20, 25)], []
for start, end in spans:
    if merged and start <= merged[-1][1]:
        merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
    else:
        merged.append((start, end))
print(merged)
