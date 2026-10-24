from decimal import Decimal
field = {'raw': '1,250.00', 'page': 2, 'box': (10, 20, 80, 40), 'revision': 3}
field['value'] = Decimal(field['raw'].replace(',', ''))
print(field['value'], field['page'], field['box'])
