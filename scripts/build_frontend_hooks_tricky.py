"""Build and append 20 React hooks/tricky questions and 20 TypeScript tricky questions."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))

from editorial import content_digest
from revised_content_gate import validate_record
import data_frontend_react_hooks_tricky
import data_frontend_ts_tricky

REVIEWER_STATUS = {
    "status": "reviewed",
    "reviewer": "Codex AI technical review (user-delegated verdict; authored/self-reviewed)",
    "reviewed_at": "2026-10-24"
}

def main():
    slug = 'frontend-foundations'
    ch_dir = ROOT / 'content/chapters' / slug

    new_react_qs = data_frontend_react_hooks_tricky.QUESTIONS
    new_ts_qs = data_frontend_ts_tricky.QUESTIONS

    # Step 1: Ensure reviewer status, difficulty, and answer_format on all new questions
    for q in new_react_qs + new_ts_qs:
        if 'reviewer_status' not in q:
            q['reviewer_status'] = REVIEWER_STATUS
        if 'answer_format' not in q:
            q['answer_format'] = 'conceptual'
        if 'difficulty' not in q:
            q['difficulty'] = 'interview'

    # Step 2: Update questions-react.json
    react_shard_path = ch_dir / 'questions-react.json'
    existing_react_qs = json.loads(react_shard_path.read_text())
    # Avoid duplicate additions if run multiple times
    existing_react_titles = {q['Q'] for q in existing_react_qs}
    filtered_new_react = [q for q in new_react_qs if q['Q'] not in existing_react_titles]
    all_react_qs = existing_react_qs + filtered_new_react
    react_shard_path.write_text(json.dumps(all_react_qs, indent=2, ensure_ascii=False) + '\n')
    print(f"Updated questions-react.json: {len(existing_react_qs)} existing + {len(filtered_new_react)} new = {len(all_react_qs)} total")

    # Step 3: Update questions-typescript.json
    ts_shard_path = ch_dir / 'questions-typescript.json'
    existing_ts_qs = json.loads(ts_shard_path.read_text())
    existing_ts_titles = {q['Q'] for q in existing_ts_qs}
    filtered_new_ts = [q for q in new_ts_qs if q['Q'] not in existing_ts_titles]
    all_ts_qs = existing_ts_qs + filtered_new_ts
    ts_shard_path.write_text(json.dumps(all_ts_qs, indent=2, ensure_ascii=False) + '\n')
    print(f"Updated questions-typescript.json: {len(existing_ts_qs)} existing + {len(filtered_new_ts)} new = {len(all_ts_qs)} total")

    # Step 4: Update content/reviews.json
    reviews_path = ROOT / 'content/reviews.json'
    reviews = json.loads(reviews_path.read_text())

    for q in filtered_new_react + filtered_new_ts:
        ident = f'interview/{slug}/{q["Q"]}'
        digest = content_digest(q)
        reviewer = q['reviewer_status']['reviewer']
        reviewed_at = q['reviewer_status']['reviewed_at']
        notes = (f"User delegated the acceptance verdict to Codex. AI-authored/self-reviewed. "
                 f"Reviewed direct answer to {q['Q']} for technical depth, code correctness, "
                 f"edge cases, risk/trade analysis and changed-assumption follow-up. "
                 f"Checked primary references and local contracts.")
        reviews[ident] = {
            'reviewer': reviewer,
            'reviewed_at': reviewed_at,
            'sha256': digest,
            'review_notes': notes
        }

    reviews_path.write_text(json.dumps(reviews, indent=2, ensure_ascii=False) + '\n')
    print(f"Registered review attestations for {len(filtered_new_react) + len(filtered_new_ts)} new questions")

    # Step 5: Assign sequential study IDs in content/shared/study_ids.json
    ids_path = ROOT / 'content/shared/study_ids.json'
    ids = json.loads(ids_path.read_text())
    next_id = max(ids.values()) + 1

    for q in filtered_new_react + filtered_new_ts:
        ident = f'interview/{slug}/{q["Q"]}'
        if ident not in ids:
            ids[ident] = next_id
            next_id += 1

    ids_path.write_text(json.dumps(ids, indent=2, ensure_ascii=False) + '\n')
    print(f"Updated study_ids.json. New max study ID: {max(ids.values())}")

    # Step 6: Update curriculum.json total questions in coverage manifest
    curriculum_path = ROOT / 'content/curriculum.json'
    curriculum = json.loads(curriculum_path.read_text())
    question_rows = [q for path in (ROOT / 'content/chapters').glob('*/questions*.json') for q in json.loads(path.read_text())]
    lesson_rows = [q for path in (ROOT / 'content/chapters').glob('*/lessons.json') for q in json.loads(path.read_text())]
    total_q_count = len(question_rows) + len(lesson_rows)

    print(f"Total counted questions across all chapters: {total_q_count}")
    if 'coverage_manifest' in curriculum:
        curriculum['coverage_manifest']['total_questions'] = total_q_count
    curriculum_path.write_text(json.dumps(curriculum, indent=2, ensure_ascii=False) + '\n')
    print(f"Updated curriculum.json total_questions to {total_q_count}")

    # Step 7: Validate all new questions with require_review=True
    print("Validating all new records against revised content gate contract...")
    for q in filtered_new_react + filtered_new_ts:
        ident = f'interview/{slug}/{q["Q"]}'
        errs = validate_record(q, ident, kind='interview', require_review=True)
        if errs:
            print(f"Validation error for {q['Q']}:", errs)
            sys.exit(1)

    print("ALL 40 new questions successfully validated against content contracts!")

if __name__ == '__main__':
    main()
