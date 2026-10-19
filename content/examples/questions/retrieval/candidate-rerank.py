candidates = ['D1', 'D2', 'D3']
relevance = {'D1': 0.4, 'D2': 0.9, 'D3': 0.2}
final = sorted(candidates, key=lambda item: relevance[item], reverse=True)[:1]
print(final)
