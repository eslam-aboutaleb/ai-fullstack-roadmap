source = {'id': 'D1', 'active': False}
vector_hits = [{'source': 'D1', 'text': 'stale private rule'}]
visible = [hit for hit in vector_hits if source['active']]
print(visible)
