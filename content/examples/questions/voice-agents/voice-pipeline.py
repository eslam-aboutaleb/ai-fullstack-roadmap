recognize = lambda audio: 'Refund on sale items?'
agent = lambda transcript: 'Exchange only'
synthesize = lambda text: ('audio:' + text).encode('utf-8')
print(synthesize(agent(recognize(b'synthetic-input'))))
