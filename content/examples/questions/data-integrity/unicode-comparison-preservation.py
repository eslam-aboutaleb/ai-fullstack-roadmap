"""Normalize comparison fields without replacing multilingual source text."""
import unicodedata

def comparison(text):
    return unicodedata.normalize('NFC', unicodedata.normalize('NFC', text).casefold())
a, b = 'Café', 'Café'
assert a != b and comparison(a) == comparison(b)
names = ['نور', 'علي']
assert all(name.encode('ascii', 'ignore') == b'' for name in names)
assert len({comparison(name) for name in names}) == 2
assert all(comparison(comparison(name)) == comparison(name) for name in [a, b, *names])
print('equivalent accents compare; distinct non-Latin values survive')
