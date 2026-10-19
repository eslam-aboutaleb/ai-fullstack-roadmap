business_ledger = {'op1': 'R1'}
checkpoint = {'next_node': 'create', 'operation': 'op1'}
receipt = business_ledger.setdefault(checkpoint['operation'], 'R2')
print(receipt, len(business_ledger))
