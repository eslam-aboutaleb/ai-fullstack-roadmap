response = {'status': 429, 'retry_after': 2}
checkpoint = 'page1'
action = 'retry' if response['status'] == 429 else 'process'
print(action, checkpoint)
