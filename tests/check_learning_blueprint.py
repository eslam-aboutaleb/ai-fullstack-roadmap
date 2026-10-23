"""Validate the machine-readable plan and independently check public output."""
from copy import deepcopy
from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
from learning_blueprint import validate_plan, inventory, PLAN, verified_assessment_links
from course_data import load


def check():
    plan=validate_plan()
    chapters=load()
    curriculum=json.loads((ROOT/'content/curriculum.json').read_text())
    report=inventory(chapters,curriculum)
    assert report['registered_assessments'] >= 50
    assert len(report['assessment_evidence'])>=17
    assert all(not e['definition_of_done_met'] and e['independent_review']=='pending'
               for e in report['assessment_evidence'])
    mapped={entry['issue']:entry['assessment_ids'] for entry in report['assessment_evidence']}
    assert 'serving-ttft-queue-regression' in mapped[38]
    assert 'safety-critical-slice-release' in mapped[43]
    assert 'mutable-default-tenant-state' in mapped[15]
    py_units=[unit for c in report['chapters'] for unit in c['linked_course_units']
              if unit['id']=='python-values']
    assert py_units and any(item['id']=='mutable-default-tenant-state'
                            for item in py_units[0]['practice'])
    indexed=json.loads((ROOT/'content/assessments.json').read_text())['items']
    bad={'issues':{'38':['missing-assessment']}}
    try:verified_assessment_links(indexed,bad)
    except ValueError:pass
    else:raise AssertionError('Unknown issue assessment ID accepted')
    assert report['total_chapters']==len(chapters)
    assert report['total_planned_modules']==len(plan['modules'])
    assert sum(len(ch['foundation_lessons'])+len(ch['interview_questions'])
               for ch in report['chapters']) == curriculum['coverage_manifest']['total_questions']
    assert {m['issue'] for m in plan['modules']} >= set(range(38,50))
    assert (ROOT/'_site/competency-blueprint.html').is_file()
    assert json.loads((ROOT/'_site/questions/competency-blueprint.json').read_text())==report
    for broken in ('dangling', 'false-approval', 'missing-question'):
        candidate=deepcopy(plan)
        row=candidate['modules'][0]
        if broken=='dangling':row['source_chapters']=['nonexistent']
        elif broken=='false-approval':row['status']='independently-reviewed'
        else:row['interview_questions']=[]
        try:validate_plan(candidate,curriculum)
        except ValueError:pass
        else:raise AssertionError('Invalid plan accepted: '+broken)
    print('Competency blueprint validated: chapter IDs, linked evidence, planned topics and regression fixtures')


if __name__=='__main__':
    check()
