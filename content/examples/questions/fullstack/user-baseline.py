baseline = {'seconds': 40, 'support_rate': 1.0}
ai_variant = {'seconds': 20, 'support_rate': 0.7}
accept = ai_variant['seconds'] < baseline['seconds'] and ai_variant['support_rate'] >= 0.95
print(accept)
