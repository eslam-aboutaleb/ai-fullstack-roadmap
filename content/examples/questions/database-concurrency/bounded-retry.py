attempts = 0
for attempt in range(1, 4):
    attempts += 1
    try:
        if attempt < 3:
            raise TimeoutError('synthetic transient failure')
        result = 'completed'
        break
    except TimeoutError:
        if attempt == 3:
            raise
print(result, attempts)
