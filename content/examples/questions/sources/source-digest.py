import hashlib
location = 'object://synthetic/policy'
digest = lambda data: hashlib.sha256(data).hexdigest()
print(digest(b'revision 1') != digest(b'revision 2'))
