#!/usr/bin/env python3
"""Organized CLI for authoring, validating, formatting, and inspecting chapter questions."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

from roadmap.config import BASELINE_ID, CONTENT, read_json, write_json
from roadmap.content import (
    CONCEPTUAL_QUESTION_SCHEMA,
    QUESTION_SCHEMA,
    check_schema,
    load_chapters,
)
from roadmap.editorial import check_interview_contract, validate_new_records
from roadmap.question_markdown import (
    dumps_questions_md,
    loads_questions_md,
    scaffold_question_md,
)


def _chapter_dir(slug: str) -> Path:
    folder = CONTENT / 'chapters' / slug
    if not (folder / 'chapter.json').is_file():
        raise SystemExit(f'Unknown chapter slug: {slug}')
    return folder


def _sync_curriculum_counts() -> dict[str, int]:
    chapters = load_chapters(assign_ids=False)
    total_questions = sum(len(ch['questions']) + len(ch['lessons']) for ch in chapters)
    with_spoken = sum('spoken' in q for ch in chapters for q in ch['questions'])
    cur_path = CONTENT / 'curriculum.json'
    curriculum = read_json(cur_path)
    manifest = curriculum['coverage_manifest']
    manifest['total_questions'] = total_questions
    manifest['questions_with_spoken_answer'] = with_spoken
    manifest['total_chapters'] = len(chapters)
    write_json(cur_path, curriculum, indent=2)
    return {'total_questions': total_questions, 'questions_with_spoken_answer': with_spoken}


def cmd_scaffold(args: argparse.Namespace) -> None:
    folder = _chapter_dir(args.chapter)
    md_path = folder / 'questions.md'
    domain = 'ai-rag'
    if md_path.is_file():
        existing = loads_questions_md(md_path.read_text(encoding='utf-8'), source=str(md_path))
        domains = [q['domain'] for q in existing if 'domain' in q]
        if domains:
            domain = Counter(domains).most_common(1)[0][0]
    template = scaffold_question_md(
        args.title,
        kind=args.kind,
        domain=domain,
        subdomain=args.chapter,
    )
    if args.out:
        out_path = Path(args.out)
        out_path.write_text(template, encoding='utf-8')
        print(f'Wrote {args.kind} question template to {out_path}')
    else:
        sys.stdout.write(template)


def cmd_add(args: argparse.Namespace) -> None:
    folder = _chapter_dir(args.chapter)
    draft_text = Path(args.draft).read_text(encoding='utf-8')
    new_questions = loads_questions_md(draft_text, source=args.draft)
    if not new_questions:
        raise SystemExit(f'No questions found in {args.draft}')

    md_path = folder / 'questions.md'
    existing = (
        loads_questions_md(md_path.read_text(encoding='utf-8'), source=str(md_path))
        if md_path.is_file()
        else []
    )
    existing_titles = {q['Q'] for q in existing}
    for row in new_questions:
        if row['Q'] in existing_titles:
            raise SystemExit(f'Duplicate question in {args.chapter}: {row["Q"]}')
        if row.get('answer_format') == 'conceptual':
            check_schema(row, CONCEPTUAL_QUESTION_SCHEMA, 'questions', args.chapter)
        elif 'spoken' in row or row.get('added'):
            check_schema(row, QUESTION_SCHEMA, 'questions', args.chapter)
        else:
            raise SystemExit(
                f'New question "{row["Q"]}" must use answer_format: conceptual or full enriched schema'
            )

    merged = existing + new_questions
    md_path.write_text(dumps_questions_md(merged, chapter_slug=args.chapter), encoding='utf-8')

    chapters = load_chapters(assign_ids=True)
    validate_new_records(chapters)
    check_interview_contract(chapters)
    counts = _sync_curriculum_counts()
    print(json.dumps({
        'added': len(new_questions),
        'chapter': args.chapter,
        'chapter_questions': len(merged),
        **counts,
    }, indent=2))


def cmd_validate(args: argparse.Namespace) -> None:
    chapters = load_chapters(assign_ids=False)
    if args.chapter:
        chapters = [ch for ch in chapters if ch['slug'] == args.chapter]
        if not chapters:
            raise SystemExit(f'Unknown chapter slug: {args.chapter}')
        check_interview_contract(chapters)
        validate_new_records(chapters)
        print(json.dumps({'chapter': args.chapter, 'questions': len(chapters[0]['questions']), 'status': 'ok'}))
        return
    validate_new_records(chapters)
    summary = check_interview_contract(chapters)
    print(json.dumps(summary, indent=2))


def cmd_format(args: argparse.Namespace) -> None:
    targets = [args.chapter] if args.chapter else sorted(
        p.parent.name for p in (CONTENT / 'chapters').glob('*/questions.md')
    )
    formatted = 0
    for slug in targets:
        md_path = _chapter_dir(slug) / 'questions.md'
        parsed = loads_questions_md(md_path.read_text(encoding='utf-8'), source=f'{slug}/questions.md')
        md_path.write_text(dumps_questions_md(parsed, chapter_slug=slug), encoding='utf-8')
        formatted += 1
    print(json.dumps({'formatted_chapters': formatted}))


def cmd_stats(_args: argparse.Namespace) -> None:
    chapters = load_chapters(assign_ids=False)
    status_counts: Counter[str] = Counter()
    total_q = 0
    post_baseline = 0
    for ch in chapters:
        for q in ch['questions']:
            total_q += 1
            if q['id'] > BASELINE_ID:
                post_baseline += 1
            status = q.get('reviewer_status', {}).get('status', 'legacy-unlabeled')
            status_counts[status] += 1
    print(json.dumps({
        'chapters': len(chapters),
        'total_questions': total_q,
        'post_baseline_questions': post_baseline,
        'review_status': dict(sorted(status_counts.items())),
    }, indent=2))


def cmd_sync_curriculum(_args: argparse.Namespace) -> None:
    print(json.dumps(_sync_curriculum_counts(), indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    specs = (
        ('scaffold', 'Print or write a compliant question Markdown template', cmd_scaffold, (
            (('--chapter',), {'required': True, 'help': 'Chapter slug'}),
            (('--kind',), {'choices': ('conceptual', 'enriched'), 'default': 'conceptual'}),
            (('--title',), {'default': 'How does <mechanism> behave under <constraint>?'}),
            (('--out',), {'help': 'Optional draft file path'}),
        )),
        ('add', 'Validate and append question(s) from a Markdown draft pack', cmd_add, (
            (('draft',), {'help': 'Markdown file containing one or more "# Question" entries'}),
            (('--chapter',), {'required': True, 'help': 'Target chapter slug'}),
        )),
        ('validate', 'Validate question Markdown packs and contracts', cmd_validate, (
            (('chapter',), {'nargs': '?', 'help': 'Optional single chapter slug'}),
        )),
        ('format', 'Normalize chapter questions.md formatting canonically', cmd_format, (
            (('chapter',), {'nargs': '?', 'help': 'Optional single chapter slug'}),
        )),
        ('stats', 'Print curriculum question coverage statistics', cmd_stats, ()),
        ('sync-curriculum', 'Sync coverage_manifest counts in content/curriculum.json', cmd_sync_curriculum, ()),
    )
    for name, help_text, handler, options in specs:
        subparser = sub.add_parser(name, help=help_text)
        for flags, kwargs in options:
            subparser.add_argument(*flags, **kwargs)
        subparser.set_defaults(func=handler)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
