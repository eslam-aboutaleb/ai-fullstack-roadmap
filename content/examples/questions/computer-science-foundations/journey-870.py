from collections import deque

queue = deque(['first','second'])
assert queue.popleft() == 'first'
queue.append('third')
assert list(queue) == ['second','third']
print(list(queue))

