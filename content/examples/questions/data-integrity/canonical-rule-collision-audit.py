"""Audit a synthetic rule migration; do not mutate stable entity IDs."""
entities = {'e1': 'North Star Labs', 'e2': 'North Star'}
def old_key(name):
    return name.casefold().replace(' ', '-')
def new_key(name):
    return old_key(name).removesuffix('-labs')
new_to_entities = {}
for entity_id, name in entities.items():
    new_to_entities.setdefault(new_key(name), []).append(entity_id)
collisions = {key: ids for key, ids in new_to_entities.items() if len(ids) > 1}
assert collisions == {'north-star': ['e1', 'e2']}
assert set(entities) == {'e1', 'e2'}
print('rule migration collision detected; stable IDs retained')
