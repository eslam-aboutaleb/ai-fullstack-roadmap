signal = {'score': 0.95, 'verified': False}
print('review' if signal['score'] > 0.9 and not signal['verified'] else 'continue')
