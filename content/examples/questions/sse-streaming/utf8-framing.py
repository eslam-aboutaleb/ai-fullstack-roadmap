import codecs
raw = 'data: {"text":"مرحبا"}\n\n'.encode('utf-8')
split = raw.index('م'.encode('utf-8')) + 1
decoder = codecs.getincrementaldecoder('utf-8')()
text = decoder.decode(raw[:split]) + decoder.decode(raw[split:], final=True)
print(text == raw.decode('utf-8'), text.endswith('\n\n'))
