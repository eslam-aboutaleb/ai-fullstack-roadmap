calls = {'remaining': 0}
def invoke(function, argument):
    if calls['remaining'] <= 0:
        return 'budget_exhausted'
    calls['remaining'] -= 1
    return function(argument)
print(invoke(lambda value: 'should not run', 'P1'))
