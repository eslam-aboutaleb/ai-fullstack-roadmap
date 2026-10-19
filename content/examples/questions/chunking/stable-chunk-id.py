identity = lambda profile: f'D1:r2:{profile}:chunk0'
print(identity('paragraph-v1') != identity('section-v2'))
