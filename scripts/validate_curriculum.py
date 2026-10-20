"""Validate the curriculum manifest: track coverage, prerequisite DAG, references."""
from pathlib import Path
import json, sys

REPOSITORY = Path(__file__).resolve().parent.parent
CONTENT = REPOSITORY / 'content'

def load():
    course = json.loads((CONTENT / 'course.json').read_text())
    curriculum = json.loads((CONTENT / 'curriculum.json').read_text())
    return course, curriculum

def chapter_slugs(course):
    slugs = set()
    for _, _, _, stage_slugs in course['stages']:
        slugs.update(stage_slugs)
    return slugs

def validate(course=None, curriculum=None):
    if course is None or curriculum is None:
        course, curriculum = load()
    actual = chapter_slugs(course)
    tracks = curriculum['tracks']
    chapters = curriculum['chapters']

    # Every track must have chapters that exist.
    seen_in_tracks = set()
    track_ids = [track['id'] for track in tracks]
    if len(set(track_ids)) != len(track_ids):
        raise ValueError('Duplicate track IDs')
    for track in tracks:
        if not __import__('re').fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', track['id']):
            raise ValueError('Invalid track route ID')
        if track['entry_point'] not in track['chapters']:
            raise ValueError('Track entry point must belong to that track')
    for track in tracks:
        for slug in track['chapters']:
            if slug not in actual:
                raise ValueError(f"Track {track['id']} references unknown chapter: {slug}")
            if slug in seen_in_tracks:
                raise ValueError(f'Chapter appears in multiple tracks: {slug}')
            if chapters.get(slug, {}).get('track') != track['id']:
                raise ValueError(f'Chapter track disagrees with membership: {slug}')
            seen_in_tracks.add(slug)

    # Every chapter in course.json must appear in exactly one track.
    missing = actual - seen_in_tracks
    extra = seen_in_tracks - actual
    if missing:
        raise ValueError(f"Chapters missing from curriculum tracks: {sorted(missing)}")
    if extra:
        raise ValueError(f"Curriculum tracks contain unknown chapters: {sorted(extra)}")

    # Chapter entries must match actual chapters.
    chapter_keys = set(chapters)
    missing_entries = actual - chapter_keys
    extra_entries = chapter_keys - actual
    if missing_entries:
        raise ValueError(f"Chapters missing from curriculum chapter entries: {sorted(missing_entries)}")
    if extra_entries:
        raise ValueError(f"Curriculum chapter entries for unknown chapters: {sorted(extra_entries)}")

    # Prerequisite DAG: no dangling references, no self-loops, acyclic.
    prereq = {slug: set(entry['prerequisites']) for slug, entry in chapters.items()}
    for slug, deps in prereq.items():
        if slug in deps:
            raise ValueError(f"Self-loop prerequisite: {slug}")
        for dep in deps:
            if dep not in chapters:
                raise ValueError(f"Dangling prerequisite {dep} for {slug}")
    # Cycle detection via DFS.
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {slug: WHITE for slug in chapters}
    def visit(slug, path):
        color[slug] = GRAY
        path.append(slug)
        for dep in prereq[slug]:
            if color[dep] == GRAY:
                cycle = ' -> '.join(path[path.index(dep):] + [dep])
                raise ValueError(f"Cyclic prerequisite: {cycle}")
            if color[dep] == WHITE:
                visit(dep, path)
        path.pop()
        color[slug] = BLACK
    for slug in chapters:
        if color[slug] == WHITE:
            visit(slug, [])

    # Track entry points must exist.
    for track in tracks:
        if track['entry_point'] not in chapters:
            raise ValueError(f"Track {track['id']} entry point {track['entry_point']} not a chapter")

    # Version must be semver.
    version = curriculum.get('version', '')
    import re as _re
    if not _re.match(r'^\d+\.\d+\.\d+$', version):
        raise ValueError(f'Curriculum version must be semver: {version}')

    # Coverage manifest must reference existing tracks/chapters.
    coverage = curriculum.get('coverage_manifest', {})
    if coverage.get('total_chapters') != len(chapters):
        raise ValueError(f'Coverage total_chapters {coverage.get("total_chapters")} != actual {len(chapters)}')
    if coverage.get('tracks_mapped') != len(tracks):
        raise ValueError(f'Coverage tracks_mapped {coverage.get("tracks_mapped")} != actual {len(tracks)}')

    question_rows = [q for path in (CONTENT/'chapters').glob('*/questions*.json') for q in json.loads(path.read_text())]
    lesson_rows = [q for path in (CONTENT/'chapters').glob('*/lessons.json') for q in json.loads(path.read_text())]
    for key, expected in [('questions_with_spoken_answer', sum('spoken' in q for q in question_rows)),
                          ('total_questions', len(question_rows) + len(lesson_rows))]:
        if coverage.get(key) != expected:
            raise ValueError(f'Coverage {key} does not match authored source: {expected}')

    # Migration map targets must exist (sources are old slugs that may no longer exist).
    migration = curriculum.get('migration_map', {})
    for old_slug, new_slug in migration.items():
        if old_slug == 'notes' or not isinstance(new_slug, str):
            continue
        if new_slug not in chapters:
            raise ValueError(f'Migration target {new_slug} not a chapter')

    # Sample syllabi chapters must exist.
    for syllabus in curriculum.get('sample_syllabi', []):
        for slug in syllabus.get('chapters', []):
            if slug not in chapters:
                raise ValueError(f'Sample syllabus {syllabus.get("id")} references unknown chapter: {slug}')

    # Every chapter must have effort, competency, artifacts.
    for slug, entry in chapters.items():
        for field in ('track', 'prerequisites', 'effort_hours', 'competency', 'artifacts'):
            if field not in entry:
                raise ValueError(f"Chapter {slug} missing curriculum field: {field}")
        if not isinstance(entry['prerequisites'], list):
            raise ValueError(f"Chapter {slug} prerequisites must be a list")
        if isinstance(entry['effort_hours'], bool) or not isinstance(entry['effort_hours'], (int, float)) or not __import__('math').isfinite(entry['effort_hours']) or entry['effort_hours'] <= 0:
            raise ValueError(f"Chapter {slug} effort_hours must be a positive number")

    print(json.dumps({
        'tracks': len(tracks),
        'chapters': len(chapters),
        'prerequisite_edges': sum(len(d) for d in prereq.values()),
        'dag_acyclic': True,
        'unique_chapters': True,
        'no_dangling_references': True,
        'all_fields_present': True,
    }, indent=2))

if __name__ == '__main__':
    validate()
