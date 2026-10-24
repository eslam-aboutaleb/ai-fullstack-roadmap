def authoritative_empty(scan):
    return scan['complete'] and scan['authoritative'] and scan['items'] == []
print(authoritative_empty({'complete': False, 'authoritative': True, 'items': []}),
      authoritative_empty({'complete': True, 'authoritative': True, 'items': []}))
