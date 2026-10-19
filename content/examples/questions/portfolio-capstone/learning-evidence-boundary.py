evidence = {'read_course': True, 'implemented_capstone': True, 'operated_release': False}
print([name for name, demonstrated in evidence.items() if not demonstrated])
