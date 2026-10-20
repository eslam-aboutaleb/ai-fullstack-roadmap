"""Validate the curriculum manifest: 7 tracks, 48 chapters, acyclic prerequisite DAG."""
from pathlib import Path
import json, subprocess, sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import validate_curriculum


def check():
    validate_curriculum.validate()

if __name__ == '__main__':
    check()
