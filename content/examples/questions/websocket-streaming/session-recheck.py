session = {'authenticated_at_handshake': True, 'expires_at': 100}
now = 110
print(session['authenticated_at_handshake'] and now < session['expires_at'])
