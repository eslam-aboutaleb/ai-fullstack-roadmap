"""Demonstrate IEEE 754 binary floating-point drift vs exact Decimal financial arithmetic."""
from decimal import Decimal, ROUND_HALF_EVEN

# 1. Catastrophic Floating-Point Drift:
# Binary floats cannot represent 0.10 exactly (it is an infinite repeating binary fraction: 0.0001100110011...)
float_rate = 0.10
float_sum = 0.0
for _ in range(1000):
    float_sum += float_rate

# In financial ledgers, 1,000 increments of $0.10 MUST equal exactly $100.00.
# Float math accumulates precision errors:
float_drift = abs(float_sum - 100.0)
assert float_drift > 0.0, f"Float drift expected, got {float_drift}"
assert (0.1 + 0.2) != 0.3, "Classic IEEE 754 float representation anomaly"

# 2. Exact Relational Financial Modeling using Decimal:
# In SQL, this maps to NUMERIC(12, 4) or DECIMAL(18, 2)
cents = Decimal('0.01')
unit_price = Decimal('19.99')
tax_rate = Decimal('0.0825')
quantity = Decimal('3')

subtotal = unit_price * quantity
# ROUND_HALF_EVEN (Banker's rounding) prevents statistical rounding bias across millions of transactions
tax = (subtotal * tax_rate).quantize(cents, rounding=ROUND_HALF_EVEN)
total = (subtotal + tax).quantize(cents, rounding=ROUND_HALF_EVEN)

assert total == Decimal('64.92'), f"Unexpected total: {total}"
print(f"Decimal financial precision: subtotal={subtotal}, tax={tax}, total={total} (float_drift was {float_drift:.6f})")

