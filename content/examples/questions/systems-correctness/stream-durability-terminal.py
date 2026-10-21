"""Typed completion fixture; no network or provider involved."""
def terminal(*, generated, saved_id, domain_ok):
    return dict(type='response_complete', generation='ok' if generated else 'failed',
                persistence='saved' if saved_id else 'failed', message_id=saved_id,
                operation='ok' if domain_ok else 'failed')

unsaved = terminal(generated=True, saved_id=None, domain_ok=True)
assert unsaved['generation'] == 'ok' and unsaved['persistence'] == 'failed'
assert unsaved['message_id'] is None
failed_effect = terminal(generated=True, saved_id='m1', domain_ok=False)
assert failed_effect['persistence'] == 'saved' and failed_effect['operation'] == 'failed'
print('unsaved draft != durable answer; saved answer != successful effect')
