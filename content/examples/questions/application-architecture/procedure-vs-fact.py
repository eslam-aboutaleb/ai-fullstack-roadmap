fact = {'rule': 'exchange only'}
procedure = {'requires_confirmation': True}
confirmed = False
can_write = confirmed or not procedure['requires_confirmation']
print(fact['rule'], can_write)
