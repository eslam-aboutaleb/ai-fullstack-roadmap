"""Execute complete optional AEAD examples in the declared dependency environment."""
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent


def check():
    version = importlib.metadata.version('cryptography')
    expected_version = (ROOT / 'requirements-crypto.txt').read_text().split('cryptography==')[1].strip()
    assert version == expected_version, (version, expected_version)
    directory = ROOT / 'content/examples/questions/data-integrity'
    catalog = json.loads((directory / 'catalog.json').read_text())
    examples = [entry for entry in catalog if entry.get('dependencies') == ['cryptography']]
    assert len(examples) == 2
    with tempfile.TemporaryDirectory(prefix='roadmap-aead-') as workspace:
        for example in examples:
            result = subprocess.run([sys.executable, '-I', str(directory / example['filename'])],
                                    cwd=workspace, capture_output=True, text=True, timeout=15, check=True)
            assert result.stdout.strip() == example['expect'], (example['name'], result.stdout)
    print(json.dumps({'optional_crypto_examples':'pass', 'examples':len(examples),
                      'cryptography':version, 'checks':'round trip, tampering, record substitution and direct key rotation'}))


if __name__ == '__main__':
    check()
