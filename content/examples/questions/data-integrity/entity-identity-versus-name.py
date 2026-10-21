"""Source identity and matching features are separate synthetic fields."""
rows = [dict(source='s1', source_id='17', name='North Star', registry='R1'),
        dict(source='s2', source_id='91', name='North Star', registry='R2')]
source_records = {(row['source'], row['source_id']): row for row in rows}
assert len({row['name'].casefold() for row in rows}) == 1
assert len(source_records) == 2
assert rows[0]['registry'] != rows[1]['registry']
print('one matching name; two distinct verified identities')
