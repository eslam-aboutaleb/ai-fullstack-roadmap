hits = [('A1', 'A'), ('A1', 'A'), ('A2', 'A'), ('B1', 'B')]
seen_chunks, seen_sources, selected = set(), set(), []
for chunk, source in hits:
    if chunk not in seen_chunks and source not in seen_sources:
        selected.append(chunk)
        seen_chunks.add(chunk)
        seen_sources.add(source)
print(selected)
