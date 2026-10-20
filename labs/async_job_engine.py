"""Python 3.11+ bounded async worker pilot: errors, deadlines and cancellation."""
import asyncio


async def run_jobs(jobs, handler, workers=2, capacity=2, deadline=0.1):
    if workers < 1 or capacity < 1 or deadline <= 0:
        raise ValueError('workers, capacity and deadline must be positive')
    queue = asyncio.Queue(maxsize=capacity)
    results = {}

    async def produce():
        for job in jobs:
            await queue.put(job)  # Suspends the producer when the queue is full.
        for _ in range(workers):
            await queue.put(None)

    async def consume():
        while True:
            job = await queue.get()
            try:
                if job is None:
                    return
                try:
                    async with asyncio.timeout(deadline):
                        results[job['id']] = {'status': 'done', 'value': await handler(job)}
                except TimeoutError:
                    results[job['id']] = {'status': 'timeout'}
                except Exception as error:
                    # CancelledError derives from BaseException and is not swallowed.
                    results[job['id']] = {'status': 'failed', 'error': type(error).__name__}
            finally:
                queue.task_done()

    async with asyncio.TaskGroup() as group:
        group.create_task(produce())
        for _ in range(workers):
            group.create_task(consume())
    await queue.join()
    return results


async def verify():
    async def handler(job):
        if job.get('fail'):
            raise ValueError('synthetic failure')
        if job.get('block'):
            await asyncio.Event().wait()
        await asyncio.sleep(0)
        return job['value'] * 2

    result = await run_jobs([{'id':'A','value':2},{'id':'B','fail':True},{'id':'C','block':True}], handler, deadline=0.02)
    assert result['A'] == {'status':'done','value':4}
    assert result['B'] == {'status':'failed','error':'ValueError'}
    assert result['C'] == {'status':'timeout'}
    started = asyncio.Event()
    cleaned = asyncio.Event()

    async def cancellable(job):
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            cleaned.set()

    task = asyncio.create_task(run_jobs([{'id':'X'}], cancellable, deadline=10))
    await started.wait()
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    else:
        raise AssertionError('Caller cancellation was swallowed')
    assert cleaned.is_set()
    assert await run_jobs([], handler) == {}
    print('Async pilot: bounded queue, success, failure, timeout, empty input, and cancellation cleanup passed.')


if __name__ == '__main__':
    asyncio.run(verify())
