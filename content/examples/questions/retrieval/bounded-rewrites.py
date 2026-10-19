original = 'SKU17 refund'
proposed = ['SKU17 exchange', 'SKU17 exchange', 'SKU17 return']
variants = list(dict.fromkeys([original] + proposed))[:2]
print(variants)
