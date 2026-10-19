policy = {'retain_audio': False, 'retain_transcript': True, 'text_fallback': True}
microphone_allowed = False
channel = 'voice' if microphone_allowed else 'text'
print(policy['retain_audio'], channel)
