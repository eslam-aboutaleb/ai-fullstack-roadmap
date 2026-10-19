pending, commands = {}, []
for revision in [1, 2, 3]:
    pending['D1'] = {'revision': revision}
commands.extend(['op1', 'op2'])
print(pending['D1']['revision'], len(commands))
