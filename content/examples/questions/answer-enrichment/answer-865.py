from queue import Queue, Full
pending = Queue(maxsize=2)
pending.put_nowait("A")
pending.put_nowait("B")
try:
    pending.put_nowait("C")
except Full:
    assert pending.qsize() == 2
    print("accepted=2; third=rejected")
else:
    raise AssertionError("the declared bound was ignored")
