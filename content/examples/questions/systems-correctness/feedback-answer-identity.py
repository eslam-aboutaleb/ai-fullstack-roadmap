"""Synthetic ownership and current-rating semantics; not an API."""
messages = {'m1': {'owner': 'u1', 'revision': 2, 'evidence': 'g5'}}
ratings = {}
def rate(user, message_id, value):
    message = messages.get(message_id)
    if message is None or message['owner'] != user:
        raise PermissionError('answer unavailable')
    if type(value) is not int or not 1 <= value <= 5:
        raise ValueError('rating out of range')
    ratings[(user, message_id)] = value
rate('u1', 'm1', 2)
rate('u1', 'm1', 4)
try:
    rate('u2', 'm1', 5)
except PermissionError:
    pass
else:
    raise AssertionError('foreign feedback accepted')
assert ratings == {('u1', 'm1'): 4}
print('one updated rating; foreign answer rejected')
