"""Safe, structured answer prose and per-answer duplicate suppression.

This is an intentionally small Markdown subset. Raw HTML is always escaped;
code fences and inline code are never rewritten or highlighted as prose.
"""
import html
from hashlib import sha256
import json
import re
from pathlib import Path

E=lambda text:html.escape(str(text),quote=True)
ROOT=Path(__file__).resolve().parent.parent


def normalize(text):
    text=re.sub(r'^(?:Engineering case|Reasoning under a changed assumption|Worked case):\s*','',text,flags=re.I)
    # Literal code is case/whitespace sensitive, even when prose is normalized.
    text=re.sub(r'```[\s\S]*?```|`[^`\n]+`',lambda match:' CODE-'+sha256(match.group().encode()).hexdigest()+' ',text)
    text=re.sub(r'(?<![\w*])\*\*(?=\S)(.+?)(?<=\S)\*\*(?![\w*])',r'\1',text)
    return re.sub(r'\s+',' ',text).strip()


def blocks(text):
    result=[];pending=[];fenced=False
    for line in text.strip().splitlines():
        if line.strip().startswith('```'):fenced=not fenced
        if not line.strip() and not fenced:
            if pending:result.append('\n'.join(pending).strip());pending=[]
        else:pending.append(line)
    if pending:result.append('\n'.join(pending).strip())
    return result


def inline(text,terms=(),seen=None):
    seen=seen if seen is not None else set()
    terms=sorted({term for term in terms if len(term)>1},key=len,reverse=True)
    pattern=re.compile(r'(?<!\w)('+ '|'.join(re.escape(term) for term in terms)+r')(?:s)?(?!\w)',re.I) if terms else None
    def plain(value):
        if not pattern:return E(value)
        out=[];position=0
        for match in pattern.finditer(value):
            out.append(E(value[position:match.start()]))
            key=match.group(1).casefold()
            out.append('<strong class="answer-concept">'+E(match.group())+'</strong>' if key not in seen else E(match.group()))
            seen.add(key);position=match.end()
        out.append(E(value[position:]));return ''.join(out)
    result=[]
    token=r'(`[^`\n]+`|(?<![\w*])\*\*(?=\S)[^*\n]+(?<=\S)\*\*(?![\w*])|(?<![\w*])\*(?=\S)[^*\n]+(?<=\S)\*(?![\w*]))'
    for part in re.split(token,text):
        if not re.fullmatch(token,part):result.append(plain(part))
        elif part.startswith('`'):result.append('<code>'+E(part[1:-1])+'</code>')
        elif part.startswith('**'):result.append('<strong>'+E(part[2:-2])+'</strong>')
        else:result.append('<em>'+E(part[1:-1])+'</em>')
    return ''.join(result)


def prose(text,terms=()):
    """Render paragraphs, lists, tables and fenced code, preserving literal source."""
    lines=text.strip().splitlines();out=[];index=0;seen=set()
    render=lambda value:inline(value,terms,seen)
    while index<len(lines):
        line=lines[index].strip()
        if not line:index+=1;continue
        if line.startswith('```'):
            language=line[3:].strip();code=[];index+=1
            while index<len(lines) and not lines[index].strip().startswith('```'):
                code.append(lines[index]);index+=1
            out.append('<div class="code-panel"><button type="button" class="copy">Copy code</button><pre tabindex="0"><code class="language-'+E(language)+'">'+E('\n'.join(code))+'</code></pre></div>');index+=1;continue
        if line.startswith('### '):out.append('<h4>'+render(line[4:])+'</h4>');index+=1;continue
        if index+1<len(lines) and '|' in line and re.fullmatch(r'[\s|:\-]+',lines[index+1]) and '-' in lines[index+1]:
            split=lambda row:[cell.strip() for cell in row.strip().strip('|').split('|')]
            headers=split(line);index+=2;rows=[]
            while index<len(lines) and '|' in lines[index] and lines[index].strip():
                cells=split(lines[index]);
                if len(cells)!=len(headers):raise ValueError('Answer table row has a different number of cells')
                rows.append('<tr>'+''.join('<td>'+render(cell)+'</td>' for cell in cells)+'</tr>');index+=1
            out.append('<div class="answer-table table-scroll" role="region" aria-label="Answer comparison" tabindex="0"><table><thead><tr>'+''.join('<th scope="col">'+render(cell)+'</th>' for cell in headers)+'</tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>');continue
        list_match=re.match(r'^(?:([-*])\s+|(\d+)[.)]\s+)(.+)$',line)
        if list_match:
            ordered=bool(list_match.group(2));tag='ol' if ordered else 'ul';items=[]
            while index<len(lines):
                item=re.match(r'^(?:([-*])\s+|(\d+)[.)]\s+)(.+)$',lines[index].strip())
                if not item or bool(item.group(2))!=ordered:break
                items.append('<li>'+render(item.group(3))+'</li>');index+=1
            out.append('<'+tag+'>'+''.join(items)+'</'+tag+'>');continue
        paragraph=[line];index+=1
        while index<len(lines) and lines[index].strip():
            if re.match(r'^(?:```|### |[-*] |\d+[.)] )',lines[index].strip()):break
            paragraph.append(lines[index].strip());index+=1
        value=' '.join(paragraph)
        label=re.match(r'^(Engineering case|Reasoning under a changed assumption|Worked case):\s*(.*)',value,re.S)
        if label:
            title='Worked case' if label.group(1)!='Reasoning under a changed assumption' else 'Changed assumption'
            out.append('<aside class="answer-callout"><h4>'+title+'</h4><p>'+render(label.group(2))+'</p></aside>')
        else:
            # Keep authored paragraphs. Split unusually dense legacy prose at
            # sentence boundaries, without touching fenced or inline code.
            sentences=re.split(r'(?<=[.!?])\s+(?=[A-Z])',value) if '`' not in value else [value]
            out.extend('<p>'+render(' '.join(sentences[i:i+3]))+'</p>' for i in range(0,len(sentences),3))
    return ''.join(out)


class AnswerWriter:
    """Suppress exact repeated prose, while retaining distinct details and code."""
    def __init__(self,record):
        from interview_teaching import answer_acronyms
        self.terms=[d['term'] for d in record.get('definitions',[])]+[key for key,_ in answer_acronyms(record)]
        self.seen=[]
        self.followups={normalize(f['A']) for f in record.get('follow_ups',[])}
    def take(self,text,reserve_followups=False):
        accepted=[]
        for part in blocks(text):
            key=normalize(part)
            if not key:continue
            if reserve_followups and part.startswith('Reasoning under a changed assumption:') and key in self.followups:continue
            if any(key==prior or key in prior for prior in self.seen):continue
            self.seen.append(key);accepted.append(part)
        return '\n\n'.join(accepted)
    def render(self,text,reserve_followups=False):
        return prose(self.take(text,reserve_followups),self.terms)
    def section(self,title,text,kind=''):
        body=self.render(text)
        return '<section class="answer-section '+E(kind)+'"><h4>'+E(title)+'</h4>'+body+'</section>' if body else ''


VISUALS=json.loads((ROOT/'content/shared/answer-diagrams.json').read_text())


def validate_diagrams(chapters):
    known={str(q['id']) for c in chapters for q in c['lessons']+c['questions']}
    if set(VISUALS)-known:raise ValueError('Answer diagram references an unknown study ID')
    for item in VISUALS.values():
        if not item.get('title') or not item.get('description') or len(item.get('steps',[]))<2:
            raise ValueError('Answer diagram needs a title, explanation and connected steps')
        for step in item['steps']:
            if not step.get('title') or not step.get('body') or step.get('kind','normal') not in ('normal','state','decision','warning'):
                raise ValueError('Invalid answer diagram step')


def answer_diagram(record):
    diagram=VISUALS.get(str(record['id']))
    if not diagram:return ''
    title_id='answer-diagram-'+str(record['id'])
    steps=''.join('<li class="diagram-'+E(step.get('kind','normal'))+'"><span class="diagram-step">'+str(i+1).zfill(2)+'</span><strong>'+E(step['title'])+'</strong><p>'+inline(step['body'])+'</p></li>' for i,step in enumerate(diagram['steps']))
    return '<figure class="answer-diagram" aria-labelledby="'+title_id+'"><figcaption id="'+title_id+'"><strong>'+E(diagram['title'])+'</strong><p>'+E(diagram['description'])+'</p></figcaption><ol class="answer-flow">'+steps+'</ol></figure>'
