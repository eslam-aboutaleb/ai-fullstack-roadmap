last_id, text = 7, ''
for event in [{'id': 7, 'text': 'a'}, {'id': 8, 'text': 'b'}, {'id': 9, 'text': 'c'}]:
    if event['id'] > last_id:
        text += event['text']
        last_id = event['id']
print(text, last_id)
