ranked, relevant = ['B', 'A', 'D'], {'A', 'C'}
hits = [rank for rank, item in enumerate(ranked, 1) if item in relevant]
precision, recall = len(hits)/len(ranked), len(hits)/len(relevant)
reciprocal_rank = 1/hits[0] if hits else 0
print(round(precision, 6), recall, reciprocal_rank)
