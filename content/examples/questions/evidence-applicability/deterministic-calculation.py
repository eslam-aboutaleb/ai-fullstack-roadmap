"""Demonstrate deterministic calculations verifying and bounding generated LLM explanations."""
from decimal import Decimal, ROUND_HALF_EVEN

def verify_invoice_explanation(items, tax_rate_str, claimed_total_str):
    """
    Deterministic calculation engine that validates LLM generated claims.
    LLMs frequently suffer from arithmetic hallucination and token drift;
    financial numbers must be computed by deterministic software.
    """
    tax_rate = Decimal(tax_rate_str)
    claimed_total = Decimal(claimed_total_str)
    
    subtotal = Decimal('0.00')
    for item in items:
        unit_price = Decimal(str(item['price']))
        qty = Decimal(str(item['quantity']))
        subtotal += unit_price * qty
        
    tax = (subtotal * tax_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)
    computed_total = subtotal + tax
    
    is_accurate = (computed_total == claimed_total)
    diff = computed_total - claimed_total
    
    return {
        "is_accurate": is_accurate,
        "computed_subtotal": str(subtotal),
        "computed_tax": str(tax),
        "computed_total": str(computed_total),
        "discrepancy": str(diff)
    }

invoice_items = [
    {"desc": "API Compute Units", "price": "149.50", "quantity": 2},
    {"desc": "Storage Retention", "price": "29.99", "quantity": 1}
]

# Scenario: LLM explanation claims total is $355.00
audit = verify_invoice_explanation(invoice_items, "0.0825", "355.00")
assert not audit["is_accurate"], "Deterministic calculation catches LLM calculation error"

# Scenario: Valid computed claim
valid_audit = verify_invoice_explanation(invoice_items, "0.0825", "356.09")
assert valid_audit["is_accurate"]

print(f"Deterministic calculation audit: accurate={valid_audit['is_accurate']} total=${valid_audit['computed_total']}")

