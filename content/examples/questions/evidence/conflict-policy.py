sources = [{'id': 'P1', 'rule': 'refund'}, {'id': 'P2', 'rule': 'no_refund'}]
values = {source['rule'] for source in sources}
print('supported' if len(values) == 1 else 'needs_review')
