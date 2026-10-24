"""Verify the generated site is base-path safe under PAGES_BASE_PATH."""
from pathlib import Path
import json, os, re, subprocess, sys
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / '_site'
BASE = '/ai-fullstack-roadmap/'


def build_with_base_path():
    env = dict(os.environ, PAGES_BASE_PATH=BASE)
    subprocess.run([sys.executable, '-B', 'scripts/build.py'], cwd=ROOT, check=True, env=env)
    subprocess.run([sys.executable, '-B', 'scripts/package.py'], cwd=ROOT, check=True)


def collect_links_and_assets(directory):
    found = []
    for path in directory.rglob('*'):
        if not path.is_file() or path.suffix != '.html':
            continue
        text = path.read_text(errors='ignore')
        for m in re.finditer(r'(?:href|src)="([^"]+)"', text):
            found.append((path.relative_to(directory).as_posix(), m.group(1)))
    return found


def check():
    build_with_base_path()
    bad = []
    for name, ref in collect_links_and_assets(SITE):
        parsed = urlsplit(ref)
        if parsed.scheme or parsed.netloc:
            continue
        if ref.startswith('#') or ref.startswith('mailto:') or ref.startswith('tel:') or '${' in ref:
            continue
        # Absolute path links must use the base path.
        if ref.startswith('/'):
            if not ref.startswith(BASE):
                bad.append((name, ref))
                continue
            target_path = unquote(parsed.path[len(BASE):])
        else:
            # Relative links resolve against the source file's directory.
            target_path = (Path(name).parent / unquote(parsed.path)).as_posix()
        target = (SITE / target_path).resolve()
        if target.is_dir():
            target = target / 'index.html'
        if not target.exists():
            bad.append((name, ref))

    assert not bad, ('base-path unsafe references', bad[:10])
    print(json.dumps({'base_path': BASE, 'base_path_safe': True, 'checked_pages': len(list(SITE.rglob('*.html')))}, indent=2))


if __name__ == '__main__':
    check()
