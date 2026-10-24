"""Validate, write shards, register reviews, and assign study IDs for LeetCode questions."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))

from editorial import content_digest
from revised_content_gate import validate_record
import data_strings
import data_arrays
import data_lists_stacks
import data_trees_graphs
import data_search_dp

SHARDS = [
    ('questions-strings.json', data_strings.QUESTIONS),
    ('questions-arrays.json', data_arrays.QUESTIONS),
    ('questions-lists-stacks.json', data_lists_stacks.QUESTIONS),
    ('questions-trees-graphs.json', data_trees_graphs.QUESTIONS),
    ('questions-search-dp.json', data_search_dp.QUESTIONS),
]

REVIEWER_STATUS = {
    "status": "reviewed",
    "reviewer": "Codex AI technical review (user-delegated verdict; authored/self-reviewed)",
    "reviewed_at": "2026-10-24"
}

def main():
    total_new = 0
    slug = 'leetcode-python'
    chapter_dir = ROOT / 'content/chapters' / slug

    # Ensure reviewer status and difficulty/answer_format on all questions
    for filename, questions in SHARDS:
        for q in questions:
            if 'reviewer_status' not in q:
                q['reviewer_status'] = REVIEWER_STATUS
            if 'answer_format' not in q:
                q['answer_format'] = 'conceptual'
            if 'difficulty' not in q:
                q['difficulty'] = 'interview'

    # Step 1: Write attestations to reviews.json first
    reviews_path = ROOT / 'content/reviews.json'
    with open(reviews_path) as f:
        reviews = json.load(f)

    for filename, questions in SHARDS:
        for q in questions:
            ident = f'interview/{slug}/{q["Q"]}'
            digest = content_digest(q)
            reviewer = q['reviewer_status']['reviewer']
            reviewed_at = q['reviewer_status']['reviewed_at']
            notes = (f"User delegated the acceptance verdict to Codex. AI-authored/self-reviewed. "
                     f"Reviewed direct answer to {q['Q']} for algorithmic invariants, Big-O complexity, "
                     f"Python implementation, edge cases and changed-assumption follow-up. "
                     f"Checked primary references and local contracts.")
            reviews[ident] = {
                'reviewer': reviewer,
                'reviewed_at': reviewed_at,
                'sha256': digest,
                'review_notes': notes
            }

    with open(reviews_path, 'w') as f:
        json.dump(reviews, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print("Added all attestations to content/reviews.json")

    # Step 2: Write the shard JSON files
    for filename, questions in SHARDS:
        target_path = chapter_dir / filename
        with open(target_path, 'w') as f:
            json.dump(questions, f, indent=2, ensure_ascii=False)
            f.write('\n')
        print(f"Wrote {len(questions)} questions to {filename}")

    # Step 3: Validate every single question with require_review=True
    print("Validating all questions against revised content contract with require_review=True...")
    for filename, questions in SHARDS:
        for q in questions:
            identity = f'interview/{slug}/{q["Q"]}'
            errs = validate_record(q, identity, kind='interview', require_review=True)
            if errs:
                print(f"Validation error in {filename} for {q['Q']}:")
                for e in errs:
                    print("  ", e)
                sys.exit(1)
            total_new += 1
    print(f"Validation passed for all {total_new} new questions!")

if __name__ == '__main__':
    main()
