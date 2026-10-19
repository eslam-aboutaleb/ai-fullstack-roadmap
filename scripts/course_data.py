"""Load chapter-local content and preserve stable study identities."""
from pathlib import Path
import argparse
import json

REPOSITORY = Path(__file__).resolve().parent.parent
CONTENT = REPOSITORY / 'content'
STAGES = [tuple(stage) for stage in json.loads((CONTENT / 'course.json').read_text())['stages']]


def load(assign_ids=False):
    references = json.loads((CONTENT / 'shared/references.json').read_text())
    ids_path = CONTENT / 'shared/study_ids.json'
    identities = json.loads(ids_path.read_text())
    if len(set(identities.values())) != len(identities):
        raise ValueError('Study IDs must be unique')
    next_id = max(identities.values(), default=0) + 1
    changed = False
    chapters = {}
    for path in sorted((CONTENT / 'chapters').glob('*/chapter.json')):
        chapter = json.loads(path.read_text())
        slug = path.parent.name
        if chapter['slug'] != slug or slug in chapters:
            raise ValueError('Chapter slug does not match its unique folder: ' + slug)
        for group, namespace in (('questions', 'interview'), ('lessons', 'lesson')):
            rows = json.loads((path.parent / (group + '.json')).read_text())
            if not rows:
                raise ValueError('Missing ' + group + ': ' + slug)
            seen = set()
            for question in rows:
                key = namespace + '/' + slug + '/' + question['Q']
                if key in seen:
                    raise ValueError('Duplicate study question: ' + key)
                seen.add(key)
                if key not in identities:
                    if not assign_ids:
                        raise ValueError('Unregistered question: ' + key +
                                         '. Run python3 scripts/course_data.py --assign-ids first.')
                    identities[key] = next_id
                    next_id += 1
                    changed = True
                question['id'] = identities[key]
            chapter[group] = rows
        review = json.loads((path.parent / 'review.json').read_text())
        review['references'] = [references[key] for key in review['links'].split(',')]
        chapter['review'] = review
        if not chapter['flow'] or len(chapter['case']) != 3:
            raise ValueError('Missing case or flow: ' + slug)
        chapters[slug] = chapter
    ordered, included = [], set()
    for number, (_, level, _, slugs) in enumerate(STAGES, 1):
        for slug in slugs:
            if slug not in chapters or slug in included:
                raise ValueError('Unknown or repeated course chapter: ' + slug)
            included.add(slug)
            chapter = chapters[slug]
            chapter.update(stage=number, level=level)
            ordered.append(chapter)
    if included != set(chapters):
        raise ValueError('Every chapter folder needs a learning stage')
    if changed:
        ids_path.write_text(json.dumps(identities, indent=2, ensure_ascii=False) + '\n')
    return ordered


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assign-ids', action='store_true', help='Append IDs for new question titles; never renumber existing IDs')
    args = parser.parse_args()
    chapters = load(assign_ids=args.assign_ids)
    print(json.dumps({c['slug']: {q['Q']: q['id'] for q in c['lessons'] + c['questions']}
                      for c in chapters}, indent=2, ensure_ascii=False))
