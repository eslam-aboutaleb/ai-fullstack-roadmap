"""Install pinned headless Chromium, with a TLS-verified official CFT fallback.

Playwright's CDN redirects CFT archives to Google's public CFT bucket. A broken
CDN certificate must not lead to disabling TLS or using an unpinned browser.
"""
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
from urllib.request import urlopen
import zipfile


def install():
    result = subprocess.run([sys.executable, '-m', 'playwright', 'install', '--with-deps', '--only-shell', 'chromium'])
    if result.returncode == 0:
        return
    if platform.system() != 'Linux' or platform.machine() not in {'x86_64', 'AMD64'}:
        raise SystemExit('Default browser installation failed; official fallback supports Linux x64 only')
    spec = importlib.util.find_spec('playwright')
    package = Path(spec.origin).parent
    metadata = json.loads((package / 'driver/package/browsers.json').read_text())
    browser = next(row for row in metadata['browsers'] if row['name'] == 'chromium-headless-shell')
    version, revision = browser['browserVersion'], browser['revision']
    # These values come only from the installed pinned SDK, not workflow input.
    if not all(part.isdigit() for part in version.split('.')) or not revision.isdigit():
        raise ValueError('Unexpected pinned browser identity')
    url = 'https://storage.googleapis.com/chrome-for-testing-public/' + version + '/linux64/chrome-headless-shell-linux64.zip'
    registry = subprocess.check_output([
        str(package / 'driver/node'), '-e',
        'const p=require(process.argv[1]);process.stdout.write(p.chromium.executablePath())',
        str(package / 'driver/package')], text=True)
    destination = Path(registry).parent.parent.parent / ('chromium_headless_shell-' + revision)
    # executablePath points to registry/chromium-N/chrome-linux64/chrome.
    with tempfile.TemporaryDirectory() as temporary:
        archive = Path(temporary) / 'browser.zip'
        with urlopen(url, timeout=120) as response, archive.open('wb') as target:
            if not response.geturl().startswith('https://storage.googleapis.com/chrome-for-testing-public/'):
                raise ValueError('Unexpected browser archive redirect')
            shutil.copyfileobj(response, target)
        unpacked = Path(temporary) / 'unpacked'
        unpacked.mkdir()
        with zipfile.ZipFile(archive) as zipped:
            for member in zipped.infolist():
                relative = Path(member.filename)
                if relative.is_absolute() or '..' in relative.parts:
                    raise ValueError('Unsafe browser archive entry')
                target = unpacked / relative
                if member.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with zipped.open(member) as source, target.open('wb') as output:
                        shutil.copyfileobj(source, output)
                    target.chmod((member.external_attr >> 16) & 0o777 or 0o644)
        executable = unpacked / 'chrome-headless-shell-linux64/chrome-headless-shell'
        if not executable.is_file():
            raise ValueError('Pinned browser archive omitted executable')
        destination.parent.mkdir(parents=True, exist_ok=True)
        # Replace only this exact SDK revision, never another browser/profile.
        if destination.exists():
            shutil.rmtree(destination)
        shutil.move(str(unpacked), destination)
        (destination / 'INSTALLATION_COMPLETE').touch()
        print(json.dumps({'official_cft_fallback': version, 'revision': revision,
                          'archive_sha256_observed': sha256(archive.read_bytes()).hexdigest(),
                          'tls_verification': 'enabled'}))
    # Startup is the contract the tests require; never silently skip them.
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        instance = p.chromium.launch()
        instance.close()


if __name__ == '__main__':
    install()
