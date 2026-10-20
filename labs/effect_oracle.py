"""Deterministic fixture oracle; a real system needs a trusted complete ledger."""


def oracle(corrected_id, superseded_id, rows, events):
    ids = [row['id'] for row in rows]
    writes = [index for index, event in enumerate(events) if event['kind'] == 'write']
    checks = {
        'one corrected request': ids == [corrected_id],
        'no superseded request': superseded_id not in ids,
        'one write': len(writes) == 1,
        'authorized trajectory': bool(events) and all(event.get('authorized') is True for event in events),
    }
    before_write = events[:writes[0]] if writes else []
    checks['eligibility before write'] = any(event['kind'] == 'eligibility' and event.get('passed') is True for event in before_write)
    checks['approval before write'] = any(event['kind'] == 'approval' and event.get('passed') is True for event in before_write)
    return all(checks.values()), checks


if __name__ == '__main__':
    rows = [{'id': 'corrected'}]
    events = [{'kind': kind, 'authorized': True, 'passed': True} for kind in ('eligibility', 'approval', 'write')]
    assert oracle('corrected', 'old', rows, events)[0]
    assert not oracle('corrected', 'old', rows, events[1:])[0]
    assert not oracle('corrected', 'old', rows, list(reversed(events)))[0]
    assert not oracle('corrected', 'old', rows * 2, events)[0]
    assert not oracle('corrected', 'old', rows, events + [{'kind': 'read', 'authorized': False}])[0]
    print('Oracle accepts valid state and rejects missing approval, wrong order, duplicates, and unauthorized reads.')
