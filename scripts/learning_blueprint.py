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



def verified_assessment_links(index, evidence=None):
    """Validate issue->actual assessment identifiers; these are draft mappings."""
    if evidence is None:
        evidence=json.loads((ROOT/'content/shared/assessment-evidence.json').read_text())
    issues=evidence.get('issues')
    if not isinstance(issues,dict) or not issues:
        raise ValueError('Missing assessment/issue evidence mapping')
    assessment_ids={x['id'] for x in index}
    if len(assessment_ids)!=len(index):
        raise ValueError('Duplicate assessment identifiers')
    for issue,ids in issues.items():
        if not str(issue).isdigit() or not isinstance(ids,list) or not ids or len(ids)!=len(set(ids)):
            raise ValueError('Invalid issue-to-assessment mapping')
        if set(ids)-assessment_ids:
            raise ValueError('Unknown assessment for issue #'+str(issue)+': '+str(sorted(set(ids)-assessment_ids)))
    return {str(k):list(v) for k,v in issues.items()}


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
    assessment_links = verified_assessment_links(practices)
    assessments_by_id = {row['id']:row for row in practices}
    tasks = defaultdict(list)
    for row in practices:
        tasks[row['topic']].append({'kind':row['kind'],'id':row['id'],
                                   'objective':row['objective']})
    for row in browser:
        tasks[row['topic']].append({'kind':'browser-code','id':row['id'],
                                   'objective':row['objective']})
    for unit in units.values():
        unit['practice']=tasks[unit['study_id']]
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
            'linked_practice_count':sum(len(row['practice']) for row in guided+interviews)+sum(len(u['practice']) for u in mapped_units),
            'evidence_stage':'introduced; some local practice is authored, independent learner mastery not verified',
            'independent_technical_review':'pending',
        })
    issue_evidence = [{
        'issue':int(issue),'assessment_ids':ids,
        'items':[{'id':identity,'topic':assessments_by_id[identity]['topic'],
                  'objective':assessments_by_id[identity]['objective'],
                  'kind':assessments_by_id[identity]['kind'],
                  'status':'authored-assessment-only'} for identity in ids],
        'definition_of_done_met':False,
        'external_integration_verified':False,
        'independent_review':'pending'
    } for issue,ids in sorted(assessment_links.items(),key=lambda x:int(x[0]))]
    return {'version':1,'review_status':'planned-and-source-inventory',
            'no_question_cap':True,
            'disclaimer':'An authored outcome, lab or answered question is not evidence of real learner mastery or independent technical approval.',
            'total_chapters':len(records),'total_planned_modules':len(plan['modules']),
            'chapters':records,'planned_modules':plan['modules'],
            'assessment_evidence':issue_evidence,'registered_assessments':len(practices),
            'evidence_scope':'Draft assessment authoring and identity traceability, not subject acceptance or learner mastery'}


def build(out, write, chapters, curriculum, url):
    payload = inventory(chapters, curriculum)
    target=out/'questions/competency-blueprint.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False,indent=2)+'\n')
    # The existing curriculum-map reader is the sole coverage destination.
    # Export structured facts, but do not recreate duplicate navigational hubs.
    return payload
