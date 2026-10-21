import codecs
raw = "café".encode("utf-8")
assert len(raw) == 5 and len("café") == 4
decoder = codecs.getincrementaldecoder("utf-8")()
first = decoder.decode(raw[:4], final=False)
second = decoder.decode(raw[4:], final=True)
assert first + second == "café"
print(f"characters=4; bytes=5; decoded={first + second}")
