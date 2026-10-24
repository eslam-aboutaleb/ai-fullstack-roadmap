"""Validate all authored/revised learning content against a pinned Git base.

Draft previews are allowed. --require-review blocks publication until matching
content-specific review exists. Passing structure never grants it.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
CHAPTER_PATH = re.compile(r'^content/chapters/([a-z0-9-]+)/(questions(?:-[a-z0-9-]+)?|lessons)\.json$')
COURSE_PATH = re.compile(r'^content/courses/[a-z0-9-]+\.json$')
PLACEHOLDERS = ('lorem ipsum', 'todo: write', 'tbd answer', 'as an ai language model')


def _text(value, minimum):
    return isinstance(value, str) and len(value.strip()) >= minimum


def _sources(values):
    return isinstance(values, list) and bool(values) and all(
        isinstance(url, str) and urlsplit(url).scheme == 'https'
        and bool(urlsplit(url).netloc) for url in values)


def validate_record(record, identity, kind='interview', require_review=False):
    problems = []
    if any(marker in json.dumps(record, ensure_ascii=False).casefold() for marker in PLACEHOLDERS):
        problems.append('placeholder text in learning record')
    if kind == 'lesson':
        for key, minimum in (('Q', 12), ('explain', 220), ('example', 60), ('takeaway', 25)):
            if not _text(record.get(key), minimum):
                problems.append(f'lesson {key} needs at least {minimum} characters')
    else:
        answer = record.get('A', '')
        if not _text(answer, 350):
            problems.append('answer is too short (<350 characters)')
        if not isinstance(answer, str) or len(re.split(r'\n\s*\n', answer.strip())) < 2:
            problems.append('answer needs separate explanatory paragraphs')
        for key in ('Why', 'Risk', 'Trade', 'Try'):
            if not _text(record.get(key), 40):
                problems.append(f'{key} needs a substantive explanation or task (>=40 characters)')
        if 'worked_case' in record and not _text(record['worked_case'], 100):
            problems.append('worked_case needs a concrete scenario (>=100 characters)')
        followups = record.get('follow_ups')
        if not isinstance(followups, list) or not followups or any(
            not isinstance(item, dict) or not _text(item.get('Q'), 12)
            or not _text(item.get('A'), 60) for item in followups):
            problems.append('every follow-up needs a specific question and substantive answer')
    if not _sources(record.get('citations') or record.get('references')):
        problems.append('explicit HTTPS primary references required')
    review = record.get('reviewer_status', {})
    if not isinstance(review, dict) or review.get('status') not in {'draft', 'reviewed', 'approved'}:
        problems.append('explicit draft/reviewed/approved status required')
    else:
        from editorial import validate_review
        try:
            validate_review(record, identity)
        except ValueError as exc:
            problems.append(str(exc))
        if require_review and review['status'] not in {'reviewed', 'approved'}:
            problems.append('release blocked: content-specific review pending')
    return [f'{identity}: {problem}' for problem in problems]


def inspect_revisions(before, after, slug, *, require_review=False):
    original = {row.get('id', row['Q']): row for row in before}
    count, failures = 0, []
    for row in after:
        if original.get(row.get('id', row['Q'])) == row:
            continue
        count += 1
        failures += validate_record(row, 'interview/' + slug + '/' + row['Q'], require_review=require_review)
    return count, failures


def _git(*args, check=True):
    return subprocess.run(['git', *args], cwd=ROOT, text=True, capture_output=True, check=check)


def _json_at(revision, path):
    result = _git('show', f'{revision}:{path}', check=False)
    return json.loads(result.stdout) if result.returncode == 0 else None


def snapshot(revision):
    registry = _json_at(revision, 'content/shared/study_ids.json') or {}
    records = {}
    paths = _git('ls-tree', '-r', '--name-only', revision, '--', 'content/chapters', 'content/courses').stdout.splitlines()
    for path in paths:
        match = CHAPTER_PATH.fullmatch(path)
        if match:
            slug, group = match.groups()
            kind = 'lesson' if group == 'lessons' else 'interview'
            for row in _json_at(revision, path):
                identity = f'{kind}/{slug}/{row["Q"]}'
                key = (kind, registry.get(identity, identity))
                if key in records:
                    raise ValueError('duplicate stable learning identity: ' + identity)
                records[key] = (row, identity, kind)
        elif COURSE_PATH.fullmatch(path):
            course = _json_at(revision, path)
            for unit in course['units']:
                identity = f'course/{course["id"]}/{unit["id"]}'
                records[('unit', course['id'], unit['id'])] = (unit, identity, 'unit')
    return records


def validate_unit(unit, identity, require_review=False):
    failures = []
    if any(marker in json.dumps(unit).casefold() for marker in PLACEHOLDERS):
        failures.append(identity + ': placeholder in course unit')
    for interview in unit.get('interviews', []):
        followup = interview.get('follow_up', {})
        if not _text(interview.get('question'), 12) or not _text(interview.get('deep'), 350):
            failures.append(identity + ': course interview needs a substantive complete answer')
        if not _text(followup.get('question'), 12) or not _text(followup.get('answer'), 60):
            failures.append(identity + ': course interview needs an answered follow-up')
        if not isinstance(interview.get('rubric'), list) or len(interview['rubric']) < 2:
            failures.append(identity + ': independent interview rubric required')
    if not _sources(unit.get('references')):
        failures.append(identity + ': course unit needs explicit primary references')
    from editorial import validate_review
    if unit.get('reviewer_status', {}).get('status') in {'reviewed', 'approved'}:
        try:
            validate_review(unit, identity)
        except ValueError as exc:
            failures.append(identity + ': ' + str(exc))
    elif require_review:
        failures.append(identity + ': release blocked: unit review pending')
    return failures


def compare_snapshots(before, after, *, require_review=False):
    count, issues = 0, []
    for key, (record, identity, kind) in after.items():
        if key in before and before[key][0] == record:
            continue
        count += 1
        issues += (validate_unit(record, identity, require_review) if kind == 'unit'
                   else validate_record(record, identity, kind, require_review))
    return count, issues


def validate_changed_git_records(base, require_review=False):
    if not base or base.startswith('-') or not re.fullmatch(r'[A-Za-z0-9_./-]+', base):
        raise ValueError('trusted git base revision required')
    res = _git('rev-parse', '--verify', base + '^{commit}', check=False)
    if res.returncode != 0:
        parent = _git('rev-parse', '--verify', 'HEAD~1^{commit}', check=False)
        if parent.returncode == 0:
            base_sha = parent.stdout.strip()
        else:
            return 0
    else:
        base_sha = res.stdout.strip()
    head_sha = _git('rev-parse', 'HEAD').stdout.strip()
    count, issues = compare_snapshots(snapshot(base_sha), snapshot(head_sha), require_review=require_review)
    if issues:
        raise ValueError('Revised learning-content gate failed:\n' + '\n'.join(issues[:100]))
    return count


def check_fixtures():
    old = {'id': 10, 'Q': 'Why isolate a tenant?', 'A': 'Short answer.'}
    good = {**old, 'A': 'Use the trusted principal to scope selection before ranking. ' * 8 + '\n\nA revoked source must be rejected again when resolving a citation.',
            'Why': 'An identity alone does not authorize every source or operation.',
            'Risk': 'Post-filtered top-k can drop all permitted evidence or expose private IDs.',
            'Trade': 'Authoritative filters add query-planning complexity but preserve scope.',
            'Try': 'Construct forbidden neighbors and verify no private source reaches ranking.',
            'citations': ['https://www.postgresql.org/docs/current/ddl-rowsecurity.html'],
            'follow_ups': [{'Q': 'What if access is revoked after selection?', 'A': 'Revalidate at citation resolution, invalidate the ACL-version cache and reject the now-forbidden record.'}],
            'reviewer_status': {'status': 'draft'}}
    assert inspect_revisions([old], [good], 'security') == (1, [])
    assert inspect_revisions([good], [deepcopy(good)], 'security') == (0, [])
    for field in ('A', 'Why', 'Risk', 'Trade', 'Try', 'worked_case'):
        count, errors = inspect_revisions([good], [{**good, field: 'TODO: write'}], 'security')
        assert count == 1 and errors, field
    assert inspect_revisions([good], [{**good, 'Q': 'How should tenant selection be isolated?', 'A': 'tiny'}], 'security')[1]
    assert inspect_revisions([], [good], 'security', require_review=True)[1]
    assert inspect_revisions([good], [{**good, 'reviewer_status': {'status': 'approved', 'reviewer': 'invented'}}], 'security')[1]
    same = {('interview', 10): (good, 'interview/security/' + good['Q'], 'interview')}
    assert compare_snapshots(same, same) == (0, [])
    assert compare_snapshots({}, {('interview', 2): ({**good, 'A': 'tiny'}, 'interview/security/new', 'interview')})[1]
    unit = {'references': good['citations'], 'interviews': [{'question': good['Q'], 'deep': good['A'],
            'follow_up': {'question': good['follow_ups'][0]['Q'], 'answer': good['follow_ups'][0]['A']},
            'rubric': ['Trusted owner is enforced', 'Revocation is rechecked']}]}
    assert not validate_unit(unit, 'course/security/ownership')
    assert validate_unit(unit, 'course/security/ownership', require_review=True)
    unit['interviews'][0]['deep'] = 'TODO: write'
    assert validate_unit(unit, 'course/security/ownership')
    print('Revised-content gate: complete fields, stable-ID rename/move, additions, companion units and attested release review PASS')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', help='Pinned Git base commit/ref')
    parser.add_argument('--require-review', action='store_true', help='Block publication without content-specific review')
    args = parser.parse_args()
    check_fixtures()
    if args.require_review and not args.base:
        parser.error('--require-review needs --base; do not silently skip release validation')
    if args.base:
        print(json.dumps({'checked_learning_records': validate_changed_git_records(args.base, args.require_review)}))
