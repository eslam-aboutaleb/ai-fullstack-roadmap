from decimal import Decimal

def total(values):
    if any(not isinstance(value,str) for value in values):
        raise ValueError('Expected decimal strings')
    return sum((Decimal(value) for value in values),Decimal('0'))

assert total(['0.10','0.20']) == Decimal('0.30')
print(total(['0.10','0.20']))

