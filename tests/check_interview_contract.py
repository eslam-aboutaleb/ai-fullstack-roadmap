"""Positive and negative contract tests with independently authored fixtures."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
from interview_contract import inspect, check, BASELINE_ID


def fixture():
    return {'slug':'example', 'intro':'This is an introductory walkthrough of a realistic request and its failure.',
            'terms':[['State','Current behavior']], 'flow':[['start','end']],
            'case':['A request starts','A tool fails','We recover'],
            'lessons':[{'id':BASELINE_ID+1,'Q':'How does a user begin a new process?',
                        'explain':'The reader first needs to know the actual problem and the observed result. '*5,
                        'example':'A client sends a request; the service validates its owner and scope before any action.',
                        'takeaway':'Teach the concrete problem before interviewing.'}],
            'questions':[{'id':BASELINE_ID+2,'Q':'How would you defend this contract in a real service?',
                          'A':('**Direct answer:** Use a checked authoritative boundary for each request, '
                               'and require an identity claim, a scoped database read and an audit trail. '
                               'Demonstrate this using a concrete example of a signed request whose valid identity '
                               'still lacks ownership of the target record. '
                               'Explain the underlying read/write transitions, where the invariant is enforced '
                               'and why a frontend-only filter is insufficient.\n\n'
                               '**Production failure:** A retry after a lost response may duplicate the operation. '
                               'Record an idempotency key, persist the result and return the existing effect. '
                               'Test authorization denial, retry conflicts and committed-but-unacknowledged writes.'),
                          'Why':'A valid session does not authorize access to arbitrary objects or business operations.',
                          'Risk':'A retry can accidentally cause an external operation twice.',
                          'Trade':'Authoritative checks cost additional database work but preserve safety.',
                          'Try':'Implement two callers and verify that only the authorized one can commit.',
                          'worked_case':'A signed request with the wrong owner fails at the database boundary; after one commit, retry returns its result rather than creating another effect.',
                          'answer_format':'conceptual',
                          'citations':['https://owasp.org/API-Security/'],
                          'reviewer_status':{'status':'draft'},
                          'follow_ups':[{'Q':'What changes when the write completes but the response is lost?',
                                         'A':'Look up the persisted result by an idempotency key and the authenticated owner. If the outcome is uncertain, reconcile it instead of blindly repeating a side effect.'}]
                          }]}


def check_fixtures():
    item=fixture()
    assert inspect([item]) == [], inspect([item])
    assert check([item])['new_chapter_topics'] == 2
    broken=fixture()
    broken['questions'][0]['A']='A short answer.'
    broken['questions'][0]['follow_ups']=[]
    broken['questions'][0]['citations']=[]
    messages='\n'.join(inspect([broken]))
    assert 'detailed A' in messages or 'A needs' in messages
    assert 'follow-up' in messages and 'primary reference' in messages
    old=fixture()
    old['questions'][0]={'id':BASELINE_ID, 'Q':'Existing question', 'A':'Historical short answer'}
    old['lessons'][0]={'id':BASELINE_ID-1, 'Q':'Existing foundation'}
    assert not inspect([old]), 'Legacy learning identities must remain compatible'
    # Real published new study identities (not only generated fixtures).
    from course_data import load
    chapters = load()
    identities = {q['id']:q for c in chapters for q in c['questions']}
    for number in (1212,1213,1214):
        assert number in identities, 'Missing registered new interview topic'
        record=identities[number]
        assert record['answer_format']=='conceptual'
        assert len(record['A'])>=350 and record['citations']
        assert record['follow_ups'][0]['A']
    assert check(chapters)['new_chapter_topics'] >= 3
    from answer_format import VISUALS
    assert all(str(number) in VISUALS and len(VISUALS[str(number)]['steps'])>=4 for number in (1212,1213,1214)), 'The new reader questions require explanatory diagrams'
    print('Interview-first authoring contract: positive, negative and legacy cases pass')


if __name__=='__main__':
    check_fixtures()


def check_acceptance_samples():
    import json
    from course_data import load
    from editorial import validate_review
    root = Path(__file__).resolve().parent.parent
    samples = json.loads((root/'content/shared/authoring-acceptance.json').read_text())
    records = {}
    for chapter in load():
        for kind, group in [('lesson', 'lessons'), ('interview', 'questions')]:
            for record in chapter[group]:
                records[f'{kind}/{chapter["slug"]}/{record["Q"]}'] = record
    assert len(samples['lessons']) >= 3 and len(samples['questions']) >= 10
    for sample in samples['lessons'] + samples['questions']:
        record = records[sample['identity']]
        assert record['id'] == sample['study_id']
        assert record.get('reviewer_status', {}).get('status') in ('reviewed', 'approved')
        validate_review(record, sample['identity'])
        if sample['lab']:
            assert (root/sample['lab']).read_text() == record['syntax_highlighted_source']
    print('Three reviewed lessons and ten varied reviewed interview samples: pass')
