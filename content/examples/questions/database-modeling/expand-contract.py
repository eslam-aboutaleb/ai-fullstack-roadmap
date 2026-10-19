migration = {'new_field_added': True, 'backfill_complete': False, 'old_readers': 2}
def can_contract(state):
    return state['new_field_added'] and state['backfill_complete'] and state['old_readers'] == 0
print(can_contract(migration), can_contract({**migration, 'backfill_complete': True, 'old_readers': 0}))
