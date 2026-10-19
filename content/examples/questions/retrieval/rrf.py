from collections import defaultdict
scores, k = defaultdict(float), 60
for ranking in [['A', 'B'], ['B', 'C']]:
    for rank, item in enumerate(ranking, 1):
        scores[item] += 1/(k+rank)
print(sorted(scores, key=lambda item: (-scores[item], item)))
