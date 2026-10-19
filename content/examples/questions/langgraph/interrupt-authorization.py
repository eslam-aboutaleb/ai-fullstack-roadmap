state = {'paused_for_review': True, 'resume_requested': True, 'approval_valid': False}
print(state['resume_requested'] and state['approval_valid'])
