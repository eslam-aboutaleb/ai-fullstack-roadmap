"""Shared paths, constants, URL helpers, and small text utilities."""
from pathlib import Path
import html
import json
import os
import re

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
ROOT = SCRIPTS_DIR.parent
CONTENT = ROOT / 'content'
ASSETS = ROOT / 'assets'
DOCS = ROOT / 'docs'
LABS = ROOT / 'labs'
SITE_OUT = ROOT / '_site'
BUILD_OUT = ROOT / '_build'

BASELINE_ID = 1211  # Historical interview contract adoption baseline (Oct 21, 2026)

BASE_PATH = '/' + os.environ.get('PAGES_BASE_PATH', '').strip('/')
if BASE_PATH != '/':
    BASE_PATH += '/'


def site_url(path: str = '') -> str:
    """Resolve an internal site path honoring PAGES_BASE_PATH."""
    return BASE_PATH + path.lstrip('/')


def asset_url(path: str) -> str:
    """Resolve a static asset path honoring PAGES_BASE_PATH."""
    return site_url('assets/' + path.lstrip('/'))


def escape_html(value: object) -> str:
    """HTML-escape text including quotes for safe attribute/element interpolation."""
    return html.escape(str(value), quote=True)


def slugify(text: str) -> str:
    """Convert headings or titles into deterministic lowercase URL slugs."""
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')[:60]


def reading_minutes(words: int) -> int:
    """Compute a minimum 1-minute reading estimate at 190 WPM."""
    return max(1, (words + 189) // 190)


def chapter_reading_minutes(chapter: dict) -> int:
    """Estimate reading minutes across lessons and questions in a chapter (~180 WPM)."""
    words = sum(
        len(str(q.get(k, '')).split())
        for q in chapter['lessons'] + chapter['questions']
        for k in ('Q', 'explain', 'example', 'takeaway', 'A', 'Why', 'Risk', 'Trade', 'Try')
    )
    return max(1, round(words / 180))


def normalize_question(text: str) -> str:
    """Canonicalize question titles for duplicate and comparison checks."""
    cleaned = re.sub(r'[^\w\s]', '', str(text).lower())
    return re.sub(r'\s+', ' ', cleaned).strip()


def normalize_answer(text: str) -> str:
    """Collapse internal whitespace for answer deduplication."""
    return re.sub(r'\s+', ' ', str(text or '')).strip().lower()


def read_json(path: Path):
    """Read and parse a UTF-8 JSON file."""
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path: Path, data, *, indent: int = 2) -> None:
    """Write deterministic formatted UTF-8 JSON with a trailing newline."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=indent) + '\n', encoding='utf-8')
