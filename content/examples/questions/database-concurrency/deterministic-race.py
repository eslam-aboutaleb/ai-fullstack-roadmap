from threading import Barrier, Thread
barrier, state = Barrier(2), {'count': 0}
def unsafe_increment():
    old = state['count']
    barrier.wait()
    state['count'] = old + 1
threads = [Thread(target=unsafe_increment) for _ in range(2)]
for thread in threads: thread.start()
for thread in threads: thread.join()
print(state['count'])
