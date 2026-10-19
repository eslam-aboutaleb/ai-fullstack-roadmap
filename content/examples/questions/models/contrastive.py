positive_similarity, negative_similarity, margin = 0.8, 0.7, 0.2
loss = max(0, margin-positive_similarity+negative_similarity)
print(round(loss, 6))
