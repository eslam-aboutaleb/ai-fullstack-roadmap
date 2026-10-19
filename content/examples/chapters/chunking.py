def chunks(words, size=8, overlap=2):
    if not 0 <= overlap < size:
        raise ValueError("require 0 <= overlap < size")
    step = size - overlap
    for start in range(0, len(words), step):
        yield words[start:start + size]
        if start + size >= len(words): break
assert list(chunks(list(range(10)))) == [list(range(8)), list(range(6, 10))]
