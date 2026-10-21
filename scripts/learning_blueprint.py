"""Generate an honest per-lesson/interview/assessment competency blueprint."""
from collections import defaultdict
from pathlib import Path
import html
import json
import re

ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT/'content/shared/competency-plan.json'
E = lambda value: html.escape(str(value), quote=True)
VALID_STATUS = {'planned', 'in-progress', 'independently-reviewed'}


def validate_plan(plan=None, curriculum=None):
    if plan is None:
        plan = json.loads(PLAN.read_text())
    if curriculum is None:
        curriculum = json.loads((ROOT/'content/curriculum.json').read_text())
    chapters = set(curriculum['chapters'])
    modules = plan.get('modules')
    if not isinstance(modules, list) or len(modules) < 12:
        raise ValueError('Competency plan must include all planned advanced topic workstreams')
    if len({m['id'] for m in modules}) != len(modules):
        raise ValueError('Duplicate planned competency IDs')
    if len({m['issue'] for m in modules}) != len(modules):
        raise ValueError('Duplicate issue linked to competency')
    for module in modules:
        if not re.fullmatch(r'[a-z]+(?:-[a-z]+)*', module['id']):
            raise ValueError('Invalid competency id')
        if module['status'] not in VALID_STATUS:
            raise ValueError('Unsupported competency status')
        if module['status'] == 'independently-reviewed' and not module.get('review_evidence'):
            raise ValueError('Do not label a competency independently reviewed without review evidence')
        for key in ('title','intro_problem','diagram','assessment'):
            if len(str(module.get(key, '')).strip()) < 15:
                raise ValueError(f"Competency {module['id']}: missing {key}")
        for field in ('source_chapters','prerequisite_chapters'):
            if not module[field] or set(module[field]) - chapters:
                raise ValueError(f"Competency {module['id']}: unknown/empty {field}")
        for field in ('learning_outcomes','interview_questions','local_exercises'):
            if not isinstance(module.get(field), list) or len(module[field]) < 2 or any(len(text.strip()) < 12 for text in module[field]):
                raise ValueError(f"Competency {module['id']}: incomplete {field}")
    return plan


def inventory(chapters, curriculum):
    plan = validate_plan(curriculum=curriculum)
    practices = json.loads((ROOT/'content/assessments.json').read_text())['items']
    browser = json.loads((ROOT/'content/browser-labs.json').read_text())['labs']
    from course_pages import load as load_courses
    courses = load_courses()
    units = {u['id']: {'id':u['id'],'course':course['id'], 'study_id':u['study_id'],
                        'outcomes':u['outcomes'], 'lab':u['lab'],
                        'prerequisites':u['prerequisites']}
             for course in courses for u in course['units']}
    tasks = defaultdict(list)
    for row in practices:
        tasks[row['topic']].append({'kind':row['kind'],'id':row['id'],
                                   'objective':row['objective']})
    for row in browser:
        tasks[row['topic']].append({'kind':'browser-code','id':row['id'],
                                   'objective':row['objective']})
    records = []
    for chapter in chapters:
        slug = chapter['slug']
        entry = curriculum['chapters'][slug]
        guided = [{'study_id':q['id'],'question':q['Q'],'practice':tasks[q['id']],
                   'explanation_length':len(q.get('explain',''))}
                  for q in chapter['lessons']]
        interviews = [{'study_id':q['id'],'question':q['Q'],'difficulty':q.get('difficulty','not-calibrated'),
                       'practice':tasks[q['id']],
                       'answer_length':len(q.get('A','')),
                       'has_answered_followup':any(f.get('A') for f in q.get('follow_ups',[]) if isinstance(f,dict)),
                       'has_question_level_reference':bool(q.get('citations') or q.get('references'))}
                      for q in chapter['questions']]
        mapped_units = [units[identity] for identity in entry.get('course_units',[]) if identity in units]
        missing_units = sorted(set(entry.get('course_units',[]))-set(units))
        if missing_units:
            raise ValueError(f'{slug}: missing course units: {missing_units}')
        records.append({
            'chapter':slug,'title':chapter['title'],'track':entry['track'],
            'prerequisites':entry['prerequisites'],'effort_hours':entry['effort_hours'],
            'competency':entry['competency'],'expected_artifacts':entry['artifacts'],
            'introduction':{'goal':chapter['goal'],'intro':chapter['intro'],
                            'terms':[term[0] for term in chapter['terms']]},
            'foundation_lessons':guided,'interview_questions':interviews,
            'linked_course_units':mapped_units,
            'linked_practice_count':sum(len(row['practice']) for row in guided+interviews),
            'evidence_stage':'introduced; some local practice is authored, independent learner mastery not verified',
            'independent_technical_review':'pending',
        })
    return {'version':1,'review_status':'planned-and-source-inventory',
            'no_question_cap':True,
            'disclaimer':'An authored outcome, lab or answered question is not evidence of real learner mastery or independent technical approval.',
            'total_chapters':len(records),'total_planned_modules':len(plan['modules']),
            'chapters':records,'planned_modules':plan['modules']}


def build(out, write, chapters, curriculum, url):
    payload = inventory(chapters, curriculum)
    target=out/'questions/competency-blueprint.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False,indent=2)+'\\n')
    row_html=''.join(
        '<tr><th scope="row">'+E(c['title'])+'</th><td>'+E(c['competency'])+'</td>'
        '<td>'+str(len(c['foundation_lessons']))+'/'+str(len(c['interview_questions']))+'</td>'
        '<td>'+str(c['linked_practice_count'])+'</td>'
        '<td>'+E(c['independent_technical_review'])+'</td></tr>'
        for c in payload['chapters'])
    backlog=''.join('<li><a href="https://github.com/eslam-aboutaleb/ai-fullstack-roadmap/issues/'+str(m['issue'])+'">'
                    +E(m['title'])+'</a> — '+E(m['status'])+'; '+E(m['intro_problem'])+'</li>'
                    for m in payload['planned_modules'])
    write('competency-blueprint.html','Competency blueprint and remaining curriculum work',
          '<h1>What is taught, practiced and still only planned?</h1>'
          '<p>Every chapter begins with an introduction and then foundation/deeper interview questions. '
          'This matrix links every study ID, its evidence and its course-unit/assessment coverage in a machine-readable file. '
          'Neither source counts nor passing authoring tests independently approve technical correctness or learner competency.</p>'
          '<div class="table-scroll"><table><caption>Source-derived competency inventory; no mastery certification.</caption>'
          '<thead><tr><th>Chapter</th><th>Competency</th><th>Guided/deeper topics</th><th>Linked practice</th><th>Independent review</th></tr></thead>'
          '<tbody>'+row_html+'</tbody></table></div>'
          '<h2>Planned deep-dive workstreams</h2><ul>'+backlog+'</ul>'
          '<p><a href="'+url('questions/competency-blueprint.json')+'">Download full chapter/question/unit/assessment blueprint</a></p>')
    return payload
