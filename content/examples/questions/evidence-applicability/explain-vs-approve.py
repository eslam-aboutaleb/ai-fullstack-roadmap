explanation = 'The policy may permit exchange.'
principal_can_approve, current_request_confirmed = False, True
can_write = principal_can_approve and current_request_confirmed
print(can_write)
