committed = {'revision': 1}
first_statement = committed.copy()
committed['revision'] = 2
second_statement = committed.copy()
print(first_statement['revision'], second_statement['revision'])
