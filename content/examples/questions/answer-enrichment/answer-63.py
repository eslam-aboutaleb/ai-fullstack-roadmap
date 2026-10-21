def fuse(rankings, offset=60):
    scores = {}
    for ranking in rankings:
        for rank, identifier in enumerate(ranking, 1):
            scores[identifier] = scores.get(identifier, 0) + 1/(offset+rank)
    return sorted(scores, key=lambda identifier: (-scores[identifier], identifier))
result = fuse([["A", "B"], ["B", "C"]])
assert result == ["B", "A", "C"]
print("fused=B,A,C")
