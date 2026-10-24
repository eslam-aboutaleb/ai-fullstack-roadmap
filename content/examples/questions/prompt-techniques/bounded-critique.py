answer, revisions = 'refund allowed', 0
while answer != 'exchange only' and revisions < 1:
    answer = 'exchange only'
    revisions += 1
print(answer, revisions)
