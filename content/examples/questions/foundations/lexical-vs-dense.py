query = {'SKU17'}
documents = {'exact-code': {'SKU17'}, 'paraphrase': {'return', 'item'}}
lexical = max(documents, key=lambda key: len(query & documents[key]))
dense_fixture = ['paraphrase', 'exact-code']
print(lexical, dense_fixture[0])
