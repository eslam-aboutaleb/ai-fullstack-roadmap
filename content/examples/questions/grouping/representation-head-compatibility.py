"""Equal dimension does not prove encoder/head compatibility."""
head = {'model':'encoder-A','revision':'r1','dimension':3,'normalized':True}
incoming = dict(head,model='encoder-B')
def compatible(expected,actual):
    return all(expected[key]==actual.get(key) for key in expected)
assert not compatible(head,incoming)
assert compatible(head,dict(head))
print('same dimension rejected when model identity differs')
