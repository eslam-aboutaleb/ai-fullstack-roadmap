"""Read editable chapter teaching files instead of embedding code in the builder."""
from pathlib import Path
import json

DIRECTORY = Path(__file__).resolve().parent.parent / 'content/examples/chapters'
CATALOG = json.loads((DIRECTORY / 'catalog.json').read_text())
EXAMPLES = {}
for slug, entry in CATALOG.items():
    filename = entry['file']
    if Path(filename).name != filename:
        raise ValueError('Chapter example filename must stay inside its source folder')
    EXAMPLES[slug] = {'scope': entry['scope'], 'language': entry['language'],
                      'code': (DIRECTORY / filename).read_text()}
