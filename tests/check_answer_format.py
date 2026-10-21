"""Protect literal code, detailed content and safe formatting in answer rendering."""
from pathlib import Path
import html
import json
import sys
from html.parser import HTMLParser
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'scripts'))
from answer_format import AnswerWriter, prose, validate_diagrams, VISUALS
from course_data import load


class Text(HTMLParser):
    def __init__(self,source):
        super().__init__();self.parts=[];self.feed(source)
    def handle_data(self,value):self.parts.append(value)


def check():
    source='**Ownership** keeps `<script>alert(1)</script>` as data.\n\n- Validate the caller\n- Preserve the operation identity'
    result=prose(source)
    assert '<strong>Ownership</strong>' in result
    assert '<script>' not in result and '&lt;script&gt;' in result
    assert '<ul>' in result and result.count('<li>')==2
    code='print("**literal** <value>")'
    result=prose('```python\n'+code+'\n```')
    assert code in ''.join(Text(result).parts)
    assert '<strong>' not in result
    formula='For loss (w*x-y)^2, use 2*(w*x-y)*x and compare w**2 with w2.'
    assert formula in ''.join(Text(prose(formula)).parts)
    table=prose('| Outcome | Action |\n| --- | --- |\n| Missing | Ask |')
    assert table.count('<th scope="col">')==2 and '<td>Missing</td>' in table
    record={'Q':'How is a request accepted?','A':'An accepted operation has a durable identity.\n\nEngineering case: A duplicate request reuses K.',
            'follow_ups':[{'Q':'What if ownership changes?','A':'Reauthorize before accepting the effect.'}]}
    writer=AnswerWriter(record)
    main=writer.render(record['A'],True)
    assert writer.render('An accepted operation has a durable identity.')==''
    assert writer.render('A duplicate request reuses K.')==''
    assert 'Reauthorize' in writer.render('Reauthorize before accepting the effect.')
    assert 'durable identity' in main
    literals=AnswerWriter({'Q':'Do literal strings differ?'})
    assert literals.render('Use `"A  B"` as the value.')
    assert literals.render('Use `"A B"` as the value.')
    assert literals.render('Use `"a b"` as the value.')
    assert literals.render('Use `**literal**` as the value.')
    assert literals.render('Use `literal` as the value.')
    fenced='```python\nx = 1\n\nx = 1\n\nx = 1\n```'
    rendered=AnswerWriter({'Q':'Preserve a complete code block?'}).render(fenced)
    assert ''.join(Text(rendered).parts).count('x = 1')==3
    chapters=load();validate_diagrams(chapters)
    site=Path(__file__).resolve().parent.parent/'_site'
    diagrams=0
    for chapter in chapters:
        page=(site/(chapter['slug']+'.html')).read_text()
        assert 'CONCISE INTERVIEW ANSWER' not in page
        assert '<h4>Deep explanation</h4>' not in page
        assert 'class="spoken-answer"' not in page
        for q in chapter['lessons']+chapter['questions']:
            if str(q['id']) in VISUALS:
                assert f'id="answer-diagram-{q["id"]}"' in page
                diagrams+=1
    assert diagrams==len(VISUALS)
    print(json.dumps({'answer_format':'pass','literal_code':'preserved','raw_html':'escaped','duplicate_prose':'suppressed','answer_diagrams':diagrams}))


if __name__=='__main__':check()
