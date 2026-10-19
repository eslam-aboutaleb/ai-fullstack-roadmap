state = {'token': 8, 'value': 'old'}
def publish(token, value):
    if token != state['token']:
        return False
    state['value'] = value
    return True
print(publish(7, 'stale'), publish(8, 'current'))
