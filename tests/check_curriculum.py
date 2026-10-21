"""Validate the curriculum manifest: complete tracks and chapters, acyclic prerequisite DAG."""
from pathlib import Path
import json, subprocess, sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import validate_curriculum


def check():
    validate_curriculum.validate()
    from copy import deepcopy
    course,curriculum=validate_curriculum.load()
    invalid=deepcopy(course)
    # This remains acyclic, but a prerequisite published after its dependent is unusable.
    invalid['stages'][0][3][0],invalid['stages'][0][3][1]=invalid['stages'][0][3][1],invalid['stages'][0][3][0]
    try:validate_curriculum.validate(invalid,curriculum)
    except ValueError:pass
    else:raise AssertionError('Acyclic but prerequisite-inverted journey was accepted')

if __name__ == '__main__':
    check()
