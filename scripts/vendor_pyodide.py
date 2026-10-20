"""Install a pinned, integrity-checked, self-hosted optional browser Python runtime."""
from pathlib import Path
import base64
import hashlib
import io
import json
import tarfile
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent.parent
VERSION = '0.29.2'
URL = f'https://registry.npmjs.org/pyodide/-/pyodide-{VERSION}.tgz'
INTEGRITY = 'q/Fnbmiwlw80GfaG74gTbZ6hXOYHwZ1wCDZzE03+tzQYDP1wKEqrSqmIuLQRSYixFFdNdlGEinoGYcDnulwp5g=='
FILES = ['pyodide.js', 'pyodide.asm.js', 'pyodide.asm.wasm', 'python_stdlib.zip', 'pyodide-lock.json', 'package.json']


def install():
    destination = ROOT/'vendor'/'pyodide'
    marker = destination/'runtime-manifest.json'
    if marker.exists():
        expected = json.loads(marker.read_text())
        if expected.get('version') == VERSION and all((destination/name).exists() and hashlib.sha256((destination/name).read_bytes()).hexdigest() == digest for name, digest in expected.get('files', {}).items()) and set(expected.get('files', {})) == set(FILES):
            print('Pinned Python runtime already verified'); return
    with urlopen(URL, timeout=60) as response:
        payload = response.read(20000000)
    if base64.b64encode(hashlib.sha512(payload).digest()).decode() != INTEGRITY:
        raise ValueError('Pyodide archive integrity mismatch')
    destination.mkdir(parents=True, exist_ok=True)
    hashes = {}
    with tarfile.open(fileobj=io.BytesIO(payload), mode='r:gz') as archive:
        for name in FILES:
            source = archive.extractfile('package/'+name)
            if source is None:
                raise ValueError(f'Missing runtime member: {name}')
            data = source.read()
            (destination/name).write_bytes(data)
            hashes[name] = hashlib.sha256(data).hexdigest()
    marker.write_text(json.dumps({'version': VERSION, 'source':URL, 'sha512':INTEGRITY, 'files':hashes}, indent=2)+'\n')
    print(f'Installed self-hosted Pyodide {VERSION}: {sum((destination/n).stat().st_size for n in FILES):,} bytes')


if __name__ == '__main__':
    install()
