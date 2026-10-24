from queue import Queue, Full
data, control = Queue(maxsize=1), Queue(maxsize=1)
data.put_nowait('work1')
try:
    data.put_nowait('work2')
except Full:
    status = 'rejected'
control.put_nowait('cancel')
print(status, control.get_nowait())
