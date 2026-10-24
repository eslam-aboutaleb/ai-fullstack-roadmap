"""Group independence is a separate condition from row independence."""
train = [('a1','source-a'), ('b1','source-b')]
test_bad = [('a2','source-a')]
test_good = [('c1','source-c')]
def independent(left,right):
    return not {group for _,group in left}.intersection(group for _,group in right)
assert not independent(train,test_bad)
assert independent(train,test_good)
print('different row IDs can still leak the same source group')
