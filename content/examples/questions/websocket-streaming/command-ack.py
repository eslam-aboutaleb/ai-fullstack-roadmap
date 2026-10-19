commands = {'cmd1': {'status': 'completed', 'receipt': 'receipt1'}}
reconnect_command = 'cmd1'
print(commands[reconnect_command]['status'], commands[reconnect_command]['receipt'])
