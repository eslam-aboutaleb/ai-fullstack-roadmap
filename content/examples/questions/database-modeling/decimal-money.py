from decimal import Decimal, ROUND_HALF_UP
price, count = Decimal('0.10'), 3
amount = (price*count).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
print(amount)
