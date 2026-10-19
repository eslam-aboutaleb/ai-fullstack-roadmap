answer = {'text': 'Certainly, refunds are allowed.', 'citation': 'P2:r1'}
review = {'relevant': True, 'supports_claim': False, 'current': False}
can_publish = all(review.values())
print(can_publish)
