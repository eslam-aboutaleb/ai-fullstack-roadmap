field = {'total': 250, 'confidence': 0.99}
line_items = [100, 100]
needs_review = field['confidence'] < 0.9 or field['total'] != sum(line_items)
print(needs_review)
