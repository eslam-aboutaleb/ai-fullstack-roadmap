catalog = {'citation_audit': {'task': 'citations', 'entry': 'audit.md'},
           'invoice_parse': {'task': 'invoices', 'entry': 'invoice.md'}}
selected = [name for name, item in catalog.items() if item['task'] == 'citations']
print(selected)
