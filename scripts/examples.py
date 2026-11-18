"""Load editable chapter-level teaching examples declared in catalog.json."""
from roadmap.examples import CHAPTER_EXAMPLES_DIR as DIRECTORY, load_chapter_examples

CATALOG, EXAMPLES = load_chapter_examples(DIRECTORY)


def slug(item):
    """Return canonical filename slug for a chapter key."""
    return item


def entry(key):
    """Return catalog metadata for a chapter key."""
    return CATALOG[key]


def filename(key):
    """Return filename for a chapter key."""
    return CATALOG[key]['file']
