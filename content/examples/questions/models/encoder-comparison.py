queries, documents = ['refund', 'warranty'], ['D1', 'D2', 'D3']
bi_encoder_calls = len(queries) + len(documents)
cross_encoder_pairs = len(queries) * len(documents)
print(bi_encoder_calls, cross_encoder_pairs)
