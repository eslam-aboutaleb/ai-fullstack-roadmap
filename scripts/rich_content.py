"""Render authored structured teaching fields as escaped static HTML."""
import html
import json
import re
import xml.etree.ElementTree as ET

E = lambda value: html.escape(str(value), quote=True)


def code_block(source):
    return '<div class="code-panel"><button type="button" class="copy">Copy code</button><pre><code>' + E(source) + '</code></pre></div>'


def figures(items, prefix):
    allowed_tags = {'svg', 'g', 'rect', 'text', 'tspan', 'line', 'path', 'circle', 'polygon', 'polyline', 'defs', 'marker', 'title', 'desc'}
    allowed_attrs = {'id', 'width', 'height', 'viewBox', 'x', 'y', 'x1', 'x2', 'y1', 'y2', 'cx', 'cy', 'r', 'rx', 'ry', 'd', 'points', 'fill', 'stroke', 'stroke-width', 'font-size', 'text-anchor', 'marker-end', 'markerWidth', 'markerHeight', 'refX', 'refY', 'orient', 'dy', 'class'}
    result = []
    for index, item in enumerate(items):
        svg = ET.fromstring(item['svg'])
        for element in svg.iter():
            tag = element.tag.rsplit('}', 1)[-1]
            if tag not in allowed_tags:
                raise ValueError(f'Unsupported instructional SVG tag: {tag}')
            element.tag = tag
            for key, value in list(element.attrib.items()):
                if key not in allowed_attrs or re.search(r'(?:javascript:|https?:|data:|//)', value, re.I):
                    raise ValueError(f'Unsafe instructional SVG attribute: {key}')
                if key == 'id':
                    element.set(key, f'{prefix}-{index}-{value}')
                elif 'url(' in value:
                    if not re.fullmatch(r'url\(#[a-zA-Z0-9_-]+\)', value):
                        raise ValueError('Only local SVG marker references are allowed')
                    element.set(key, value.replace('url(#', f'url(#{prefix}-{index}-'))
        svg.set('role', 'img')
        svg.set('aria-label', item['alt'])
        if 'viewBox' not in svg.attrib:
            svg.set('viewBox', f"0 0 {svg.get('width', '400')} {svg.get('height', '180')}")
        result.append('<figure class="lesson-figure">'+ET.tostring(svg, encoding='unicode')+'<figcaption><strong>'+E(item['alt'])+'</strong>. '+E(item['description'])+'</figcaption></figure>')
    return ''.join(result)


def lesson_content(q, url, writer=None):
    if 'conceptual_narrative' not in q:
        return ''
    from answer_format import prose
    narrative=writer.render(q['conceptual_narrative']) if writer else prose(q['conceptual_narrative'])
    parts = ['<section class="textbook-content">'+('<h3>Mechanism and intuition</h3>'+narrative if narrative else '')]
    parts.append('<h3>Terminology</h3><dl>'+''.join('<dt><strong>'+E(t['term'])+'</strong></dt><dd>'+E(t['definition'])+'</dd>' for t in q['glossary_terms'])+'</dl>')
    for derivation in q.get('mathematical_derivations', []):
        parts.append('<p class="math-block">'+E(derivation)+'</p>')
    parts.append(figures(q.get('visualizations', []), f'lesson-{q["id"]}'))
    for example in q['worked_examples']:
        parts.append('<h3>'+E(example['title'])+'</h3>'+code_block(example['code'])+'<p>'+E(example['explanation'])+'</p>')
    parts.append('<h3>Expected output</h3><pre><code>'+E(q['expected_output'])+'</code></pre>')
    parts.append('<p><a href="'+url('examples/'+q['local_lab'])+'">Download the local lab</a>. '+E(q['review_and_answer_keys']['known_limitations'])+'</p>')
    parts.append('<h3>Independent tasks</h3><ol>'+''.join('<li>'+E(task)+'</li>' for task in q['independent_tasks'])+'</ol>')
    parts.append('<h3>Primary references</h3><ul>'+''.join('<li><a href="'+E(ref)+'">'+E(ref)+'</a></li>' for ref in q['references'])+'</ul></section>')
    return ''.join(parts)


def question_content(q, writer=None):
    if 'execution_timeline' not in q:
        return ''
    from answer_format import AnswerWriter
    writer=writer or AnswerWriter(q)
    parts=[]
    for key,title in [('execution_timeline','Execution sequence'),('production_case','Production case'),('complexity','Complexity and cost')]:
        value=q[key]
        if value.startswith(('State the input and invariant →','Cost must be measured under the stated input size')):
            continue
        parts.append(writer.section(title,value))
    for key,title in [('alternatives','Alternatives'),('pitfalls','Pitfalls')]:
        items=[]
        for value in q[key]:
            from answer_format import normalize
            if normalize(value) in writer.followups:continue
            item=writer.render(value)
            if item:items.append('<li>'+item+'</li>')
        if items:parts.append('<section class="answer-section"><h4>'+title+'</h4><ul>'+''.join(items)+'</ul></section>')
    example=q['example']
    try:
        parsed=json.loads(example['code'])
        reasoning_fixture=isinstance(parsed,dict) and 'case' in parsed and ('decision' in parsed or 'invariant' in parsed)
    except (ValueError,TypeError):reasoning_fixture=False
    if not reasoning_fixture:
        parts.append('<section class="answer-section"><h4>Illustrative implementation</h4><p>May require the surrounding application.</p>'+code_block(example['code'])+writer.render(example['explanation'])+'<pre><code>'+E(example['output'])+'</code></pre></section>')
    return ''.join(parts)
