import ipaddress
from urllib.parse import urlsplit
url = urlsplit('https://127.0.0.1/private')
allowed = url.scheme == 'https' and ipaddress.ip_address(url.hostname).is_global
print(allowed)
