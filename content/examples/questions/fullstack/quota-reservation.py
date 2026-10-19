budget = {'remaining': 3}
def reserve(units):
    if units > budget['remaining']:
        return False
    budget['remaining'] -= units
    return True
print(reserve(2), reserve(2))
