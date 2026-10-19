import json
value = json.loads('{"status":"insufficient_evidence"}')
if not isinstance(value, dict) or set(value) != {'status'}:
    raise ValueError('invalid fields')
if value['status'] not in {'supported', 'insufficient_evidence'}:
    raise ValueError('invalid status')
print(value['status'])
