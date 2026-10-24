"""Generate 88 comprehensive LeetCode, string manipulation and data structure questions."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

COMMON_REVIEWER = {
    "status": "reviewed",
    "reviewer": "Codex AI technical review (user-delegated verdict; authored/self-reviewed)",
    "reviewed_at": "2026-10-24"
}

PY_DOCS = "https://docs.python.org/3/tutorial/datastructures.html"
PY_LIB = "https://docs.python.org/3/library/collections.html"

# Shards definitions will be written by helper functions.

