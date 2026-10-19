parents = {'P1:r2': 'Returns allowed. Exception: final sale.'}
child = {'text': 'Returns allowed.', 'parent': 'P1:r2'}
print(parents[child['parent']])
