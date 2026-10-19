def answer(search):
    try:
        hits = search()
    except TimeoutError:
        return 'unavailable'
    return 'supported' if hits else 'insufficient_evidence'

def offline():
    raise TimeoutError('synthetic outage')

print(answer(lambda: []), answer(offline))
