words, size, overlap = 'a b c d e f'.split(), 3, 1
if not 0 <= overlap < size:
    raise ValueError('overlap must be smaller than size')
chunks = [' '.join(words[start:start+size]) for start in range(0, len(words), size-overlap)]
print(chunks)
