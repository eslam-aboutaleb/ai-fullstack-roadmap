def search(question):
    return [{'id': 'P2:r2', 'text': 'Exchange only'}]

def generate(question, evidence):
    return f"{evidence[0]['text']} [{evidence[0]['id']}]"

print(generate('Refund on sale items?', search('sale items')))
