from decimal import Decimal
def amount(raw):
    if not isinstance(raw, str): raise TypeError("decimal string required")
    value = Decimal(raw)
    if not value.is_finite() or value <= 0: raise ValueError("invalid amount")
    if value != value.quantize(Decimal("0.01")): raise ValueError("precision")
    return value
assert amount("12.30") + amount("0.70") == Decimal("13.00")
