"""Facade for chapter/curriculum loading, schema validation, and study ID registration."""
from pathlib import Path
import argparse
import json

from roadmap.config import CONTENT, ROOT
from roadmap.content import (
    CONCEPTUAL_QUESTION_SCHEMA,
    LESSON_SCHEMA,
    QUESTION_SCHEMA,
    STAGES,
    check_schema as _check_schema,
    load_chapters,
)

REPOSITORY = ROOT


def load(assign_ids=False):
    """Load all stage-ordered chapters using the active CONTENT directory."""
    return load_chapters(assign_ids=assign_ids, content_dir=CONTENT)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Load and verify course chapter data.')
    parser.add_argument('--assign-ids', action='store_true', help='Assign study IDs to new entries')
    args = parser.parse_args()
    chapters = load(assign_ids=args.assign_ids)
    total = sum(len(ch['questions']) + len(ch['lessons']) for ch in chapters)
    print(json.dumps({'chapters': len(chapters), 'questions': total}))
