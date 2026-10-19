import codecs
raw = 'data: مرحبا\n\n'.encode('utf-8')
for split in range(len(raw)+1):
    decoder = codecs.getincrementaldecoder('utf-8')()
    actual = decoder.decode(raw[:split]) + decoder.decode(raw[split:], final=True)
    assert actual == raw.decode('utf-8')
print('partitions passed')
