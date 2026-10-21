from urllib.parse import urlsplit
u=urlsplit('https://example.test:8443/items?page=2')
origin=(u.scheme,u.hostname,u.port)
assert origin == ('https','example.test',8443)
print(origin)
