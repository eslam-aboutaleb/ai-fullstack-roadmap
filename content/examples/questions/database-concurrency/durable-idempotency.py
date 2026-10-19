ledger = {}
def create(key, payload):
    if key in ledger:
        if ledger[key]['payload'] != payload:
            raise ValueError('key reused with different input')
        return ledger[key]['result']
    ledger[key] = {'payload': payload, 'result': 'R1'}
    return 'R1'
print(create('op1', 'I1'), create('op1', 'I1'), len(ledger))
