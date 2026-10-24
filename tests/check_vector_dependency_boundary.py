"""Do not offer installation or execution of the known vulnerable vector adapter."""
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parent.parent

def check():
    spec = importlib.util.spec_from_file_location('vector_engines', ROOT/'labs/vector_engines.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert 'chroma' not in module.ENGINES
    assert not any(line.strip().startswith('chromadb') for line in (ROOT/'requirements-vector-engines.txt').read_text().splitlines())
    try:
        module.run(['chroma'])
    except ValueError as error:
        assert 'disabled' in str(error)
    else:
        raise AssertionError('Vulnerable Chroma adapter was offered for execution')
    print('Unpatched Chroma dependency is excluded; explicit execution fails closed')

if __name__ == '__main__':
    check()
