variants = [{'name': 'baseline', 'quality': 0.95, 'cost': 0.02},
            {'name': 'compressed', 'quality': 0.80, 'cost': 0.01}]
eligible = [variant for variant in variants if variant['quality'] >= 0.9]
print(min(eligible, key=lambda variant: variant['cost'])['name'])
