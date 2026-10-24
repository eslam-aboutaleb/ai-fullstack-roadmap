"""Narrow URL comparison policy and a bounded readable key."""
from hashlib import sha256
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

def canonical(url):
    p = urlsplit(url)
    query = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True) if k != 'utm_source']
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path, urlencode(query), ''))

def bounded(text, limit=40):
    if len(text) <= limit:
        return text
    suffix = '-' + sha256(text.encode()).hexdigest()[:12]
    if limit <= len(suffix):
        raise ValueError('insufficient key budget')
    return text[:limit-len(suffix)] + suffix
assert canonical('https://EXAMPLE.test/Doc?id=1&utm_source=x') == 'https://example.test/Doc?id=1'
assert canonical('https://example.test/Doc?id=1') != canonical('https://example.test/Doc?id=2')
assert len(bounded('x' * 100)) == 40
print('tracking removed; identity preserved; suffix fits key budget')
