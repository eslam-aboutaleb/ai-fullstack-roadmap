required, request = {'purchase_date', 'product'}, {'product': 'shirt'}
missing = sorted(required-request.keys())
print('Ask for:', ', '.join(missing))
