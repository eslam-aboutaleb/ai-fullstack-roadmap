"""Validate synthetic model output against labels and permitted evidence."""
import json
allowed = {'billing','access','delivery','unknown'}
def validate(raw,source_ids):
    result = json.loads(raw)
    if result.get('label') not in allowed: raise ValueError('unsupported label')
    if not set(result.get('evidence',[])) <= set(source_ids): raise ValueError('unsupported evidence')
    return result
assert validate('{"label":"billing","evidence":["s1"]}', ['s1'])['label'] == 'billing'
for raw in ('{"label":"admin","evidence":[]}', '{"label":"billing","evidence":["invented"]}'):
    try: validate(raw,['s1'])
    except ValueError: pass
    else: raise AssertionError('invalid output accepted')
print('allowed shape accepted; unsupported label and evidence rejected')
