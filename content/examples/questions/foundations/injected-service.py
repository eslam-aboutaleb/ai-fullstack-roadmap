def explain(query, retrieve):
    hits = retrieve(query)
    return f'found: {hits[0]}' if hits else 'no evidence'

print(explain('sale', lambda query: ['synthetic policy']))
