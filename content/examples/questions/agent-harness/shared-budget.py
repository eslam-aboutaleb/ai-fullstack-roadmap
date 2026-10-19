budget = {'remaining': 2}
def reserve():
    if budget['remaining'] <= 0:
        return False
    budget['remaining'] -= 1
    return True
print(reserve(), reserve(), reserve())
