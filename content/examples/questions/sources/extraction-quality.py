ocr_rows = [{'label': 'subtotal', 'value': 250}, {'label': 'amount_due', 'value': 200}]
print(next(row['value'] for row in ocr_rows if row['label'] == 'amount_due'))
