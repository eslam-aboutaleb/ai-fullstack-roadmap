"""Generate an evidence-based inventory and an accessible prerequisite graph."""
from pathlib import Path
from collections import defaultdict
import html
import json

ROOT=Path(__file__).resolve().parent.parent
E=lambda value:html.escape(str(value),quote=True)


def graph(chapters,curriculum,url):
    depths={};active=set()
    def depth(slug):
        if slug in active:raise ValueError('Cyclic prerequisite graph')
        if slug not in depths:
            active.add(slug)
            depths[slug]=max((depth(dep)+1 for dep in curriculum['chapters'][slug]['prerequisites']),default=0)
            active.remove(slug)
        return depths[slug]
    groups=defaultdict(list)
    for chapter in chapters:groups[depth(chapter['slug'])].append(chapter)
    positions={c['slug']:(d*240+15,i*95+15) for d,group in groups.items() for i,c in enumerate(group)}
    width=(max(groups)+1)*240;height=max(len(group) for group in groups.values())*95+20
    lines=[];nodes=[]
    for chapter in chapters:
        x,y=positions[chapter['slug']]
        for dep in curriculum['chapters'][chapter['slug']]['prerequisites']:
            dx,dy=positions[dep]
            lines.append(f'<path d="M {dx+210} {dy+32} C {dx+235} {dy+32}, {x-20} {y+32}, {x} {y+32}" fill="none" stroke="var(--muted)" marker-end="url(#prerequisite-arrow)"/>')
        title=chapter['title'];words=title.split();first='';second=''
        for word in words:
            if len(first)+len(word)<24 and not second:first+=((' ' if first else '')+word)
            else:second+=((' ' if second else '')+word)
        nodes.append(f'<a href="{url(chapter["slug"]+".html")}"><title>{E(title)}</title><rect x="{x}" y="{y}" width="210" height="65" rx="10" fill="var(--panel)" stroke="var(--line)"/><text x="{x+10}" y="{y+25}" fill="var(--text)" font-size="13">{E(first)}</text><text x="{x+10}" y="{y+46}" fill="var(--text)" font-size="12">{E(second[:29])}</text></a>')
    return f'<div class="prerequisite-map" role="region" aria-label="Scrollable prerequisite graph; use links or read the table below" tabindex="0"><svg width="{width}" height="{height}" role="group" aria-labelledby="prerequisite-title"><title id="prerequisite-title">Prerequisite graph for all {len(chapters)} chapters. Arrows point from prerequisite to dependent chapter; the table below provides every relationship as text.</title><defs><marker id="prerequisite-arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0 0L6 3L0 6" fill="var(--muted)"/></marker></defs>'+''.join(lines+nodes)+'</svg></div>'


def build(out,write,chapters,curriculum,url):
    from collections import Counter
    states=Counter(q.get('reviewer_status', {}).get('status', 'legacy unreviewed')
                   for chapter in chapters for q in chapter['questions'])
    report={'version':1,'question_review_states':dict(states),
            'automated_checks':'Schemas, source fidelity, local executable fixtures, links, duplicates and browser behavior are checked in CI. These do not establish factual accuracy.',
            'limitations':['Legacy unreviewed records remain itemized', 'External reference freshness is not exhaustively checked', 'Near-duplicate matching is lexical, not a semantic correctness proof'],
            'review_policy':'Reviewed/approved question labels require a matching reviewer, date, notes and SHA-256 content attestation. Drafts remain visibly marked.'}
    (out/'questions/editorial-report.json').write_text(json.dumps(report,indent=2)+'\n')
    write('editorial-report.html','Editorial evidence and review state',
          '<h1>Editorial evidence and review state</h1><p>Counts below come from source records. A draft label identifies material awaiting independent technical review.</p><ul>'+
          ''.join('<li>'+E(state)+': '+str(count)+'</li>' for state,count in sorted(states.items()))+
          '</ul><h2>What automation establishes</h2><p>'+E(report['automated_checks'])+'</p><h2>Review policy</h2><p>'+E(report['review_policy'])+'</p><h2>Remaining review</h2><ul>'+
          ''.join('<li>'+E(item)+'</li>' for item in report['limitations'] if item != 'Independent technical review pending')+'</ul><p><a href="'+url('questions/editorial-report.json')+'">Download the report</a> · <a href="'+url('curriculum-map.html')+'">Chapter inventory</a></p>')
    inventory=[];by={c['slug']:c for c in chapters}
    for chapter in chapters:
        entry=curriculum['chapters'][chapter['slug']]
        records=chapter['lessons']+chapter['questions']
        inventory.append({'chapter':chapter['slug'],'title':chapter['title'],'track':entry['track'],'prerequisites':entry['prerequisites'],
                          'effort_hours':entry['effort_hours'],'competency':entry['competency'],'artifacts':entry['artifacts'],
                          'lesson_ids':[q['id'] for q in chapter['lessons']],'question_ids':[q['id'] for q in chapter['questions']],
                          'enriched_lessons':sum('conceptual_narrative' in q for q in chapter['lessons']),
                          'enriched_questions':sum('spoken' in q or q.get('answer_format')=='conceptual' for q in chapter['questions']),
                          'legacy_lessons_needing_depth_review':[q['id'] for q in chapter['lessons'] if len(q['explain'].split())<120 and 'conceptual_narrative' not in q],
                          'references':chapter['review']['references'],'technical_review':'independent review pending'})
    (out/'questions/curriculum-audit.json').write_text(json.dumps({'version':1,'chapters':inventory,'notes':'Counts and metadata are automatic. Word count flags prioritize review; they do not prove factual accuracy or depth.'},indent=2)+'\n')
    rows=''.join('<tr><th scope="row"><a href="'+url(c['chapter']+'.html')+'">'+E(c['title'])+'</a></th><td>'+E(c['track'])+'</td><td>'+(' · '.join('<a href="'+url(dep+'.html')+'">'+E(by[dep]['title'])+'</a>' for dep in c['prerequisites']) or 'Entry point')+'</td><td>'+str(len(c['lesson_ids']))+' lessons / '+str(len(c['question_ids']))+' questions</td><td>'+str(c['enriched_lessons'])+' / '+str(c['enriched_questions'])+'</td><td>'+str(len(c['legacy_lessons_needing_depth_review']))+'</td></tr>' for c in inventory)
    write('curriculum-map.html','Curriculum map and migration audit','<p class="eyebrow">PREREQUISITES · OUTCOMES · OBSERVED COVERAGE</p><h1>Choose a path and see its dependencies.</h1><p>All chapter relationships come from the versioned curriculum manifest. Entry points are optional starting routes; chapters remain directly accessible. The graph is scrollable and keyboard linked; the complete table below is its text equivalent.</p>'+graph(chapters,curriculum,url)+'<div class="table-scroll"><table><caption>Actual source coverage and prerequisite relationships. Enriched counts mean schema fields exist, not independent approval.</caption><thead><tr><th>Chapter</th><th>Track</th><th>Prerequisites</th><th>Actual content</th><th>Enriched lessons/questions</th><th>Short legacy lessons to review</th></tr></thead><tbody>'+rows+'</tbody></table></div>')

    # A source-derived coverage ledger exposes subjects and defenses without a question quota.
    coverage=[]
    for position,chapter in enumerate(chapters,1):
        coverage.append({'position':position,'chapter':chapter['slug'],'title':chapter['title'],'stage':chapter['stage'],
            'prerequisites':curriculum['chapters'][chapter['slug']]['prerequisites'],
            'defined_terms':[term for term,_ in chapter['terms']],
            'lessons':[{'id':q['id'],'title':q['Q']} for q in chapter['lessons']],
            'interview_topics':[{'id':q['id'],'question':q['Q'],'answered_followups':len(q.get('follow_ups',[])),
                                'source_linked':bool(q.get('citations') or q.get('reference'))} for q in chapter['questions']],
            'companion_units':curriculum['chapters'][chapter['slug']].get('course_units',[]),
            'same_page_answers':len(chapter['lessons'])+len(chapter['questions']),
            'conceptual_worked_cases':sum(q.get('answer_format')=='conceptual' for q in chapter['questions']),
            'review_state':'See per-record digest-backed editorial evidence'})
    if any(not row['lessons'] or not row['interview_topics'] or not any(q['answered_followups'] for q in row['interview_topics']) for row in coverage):
        raise ValueError('Every chapter needs teaching, interview questions and an answered boundary defense')
    payload={'version':1,'question_count_limit':None,'full_answers_per_chapter':None,'question_data_shard_size':40,
             'scope':'Topic and artifact inventory, not certification of semantic completeness or independent approval',
             'chapters':coverage}
    from editorial_evidence import evidence_report
    evidence = evidence_report(chapters)
    (out/'questions/editorial-evidence.json').write_text(
        json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
    (out/'questions/topic-coverage.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
