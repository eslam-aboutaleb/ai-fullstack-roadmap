"""Local deterministic retrieval capstone: scope, relevance, regression and abstention."""
import json
import re

DOCS=[{'id':'sale','owner':'A','text':'Sale items can be exchanged within fourteen days. Sale items are not refundable.'},
      {'id':'delivery','owner':'A','text':'Standard delivery takes three to five days.'},
      {'id':'private','owner':'B','text':'Sale refund exception for owner B only.'}]
CASES=[{'query':'sale items exchange','owner':'A','relevant':{'sale'}},
       {'query':'standard delivery days','owner':'A','relevant':{'delivery'}},
       {'query':'unknown warranty coverage','owner':'A','relevant':set()}]


def retrieve(query,owner,documents=DOCS,broken=False):
    terms=set(re.findall(r'\w+',query.casefold()))
    scored=[]
    for document in documents:
        if document['owner']!=owner:continue
        score=len(terms & set(re.findall(r'\w+',document['text'].casefold())))
        if score:scored.append((score,document['id']))
    scored.sort(key=lambda row:(-row[0],row[1]))
    # Controlled regression: the index accidentally dropped the sale policy.
    return [identity for _,identity in scored if not broken or identity!='sale'][:1]


def evaluate(broken=False):
    results=[]
    for case in CASES:
        ranked=retrieve(case['query'],case['owner'],broken=broken)
        relevant=case['relevant'];hits=len(set(ranked)&relevant)
        results.append({'query':case['query'],'ranked':ranked,
                        'recall':hits/len(relevant) if relevant else None,
                        'correct_abstention':not ranked if not relevant else None})
    scored=[r['recall'] for r in results if r['recall'] is not None]
    return {'mean_recall':sum(scored)/len(scored), 'abstention_cases_pass':all(r['correct_abstention'] for r in results if r['correct_abstention'] is not None), 'cases':results}


def verify():
    baseline=evaluate();regression=evaluate(broken=True)
    assert baseline['mean_recall']==1
    assert regression['mean_recall']==.5
    assert baseline['abstention_cases_pass']
    assert 'private' not in retrieve('sale refund exception','A')
    assert retrieve('sale','B')==['private']
    print(json.dumps({'baseline':baseline,'deliberate_regression':regression},indent=2))


if __name__=='__main__':verify()
