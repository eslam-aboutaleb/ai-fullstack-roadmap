"""Async API failure boundaries: bounded workers, deadlines and idempotent commits.

Only standard-library Python; this is a local teaching model, not FastAPI or
a distributed worker deployment. It tests mechanisms the learner should
transfer to a real server and transactional database.
"""
import asyncio
from dataclasses import dataclass
import hashlib
import sqlite3

@dataclass(frozen=True)
class Job:
    owner: str
    operation: str
    payload: str
    delay: float = 0.01

class Processor:
    def __init__(self):
        self.db=sqlite3.connect(":memory:")
        self.db.execute("""CREATE TABLE effects (
            owner TEXT NOT NULL, operation TEXT NOT NULL,
            digest TEXT NOT NULL, result TEXT NOT NULL,
            PRIMARY KEY(owner,operation))""")
        self.active=0
        self.peak=0
        self.effects=0

    async def perform(self, job, *, lose_response=False):
        if not job.owner or not job.operation:
            raise ValueError("a host-authenticated owner and operation required")
        self.active+=1
        self.peak=max(self.peak,self.active)
        try:
            await asyncio.sleep(job.delay)  # simulates cooperative I/O
            digest=hashlib.sha256(job.payload.encode()).hexdigest()
            with self.db:
                existing=self.db.execute("SELECT digest,result FROM effects WHERE owner=? AND operation=?",
                                         (job.owner,job.operation)).fetchone()
                if existing:
                    if existing[0]!=digest:raise ValueError("idempotency conflict")
                    answer=existing[1]
                else:
                    answer="committed:"+job.payload
                    self.db.execute("INSERT INTO effects VALUES (?,?,?,?)",
                                    (job.owner,job.operation,digest,answer))
                    self.effects+=1
            if lose_response:
                raise ConnectionError("response lost AFTER database commit")
            return answer
        finally:
            self.active-=1


async def run_bounded(jobs, processor, *, workers=2, capacity=1):
    if workers<1 or capacity<1:raise ValueError("positive capacity and workers required")
    queue=asyncio.Queue(maxsize=capacity)
    results={}
    peak_queue=0
    sentinel=object()

    async def worker():
        while True:
            item=await queue.get()
            try:
                if item is sentinel:return
                try:results[(item.owner,item.operation)]=await processor.perform(item)
                except (ValueError, ConnectionError) as error:
                    results[(item.owner,item.operation)]=type(error).__name__
            finally:
                queue.task_done()
    async with asyncio.TaskGroup() as tg:
        for _ in range(workers):tg.create_task(worker())
        for item in jobs:
            await queue.put(item)  # bounded backpressure; cannot enqueue unbounded data
            peak_queue=max(peak_queue,queue.qsize())
        await queue.join()
        for _ in range(workers):await queue.put(sentinel)
        await queue.join()
    return results,peak_queue


async def check():
    processor=Processor()
    jobs=[Job("tenant-a",str(i),str(i),delay=0.01) for i in range(9)]
    results,max_queued=await run_bounded(jobs,processor,workers=2,capacity=1)
    assert len(results)==9 and processor.effects==9
    assert 1<=processor.peak<=2 and max_queued<=1
    op=Job("owner-a","pay-1","confirmed")
    try:await processor.perform(op,lose_response=True)
    except ConnectionError:pass
    else:raise AssertionError("missing lost-ack failure")
    assert await processor.perform(op)=="committed:confirmed"
    assert processor.effects==10
    try:await processor.perform(Job("owner-a","pay-1","DIFFERENT"))
    except ValueError:pass
    else:raise AssertionError("different-payload replay must conflict")
    assert await processor.perform(Job("owner-b","pay-1","different"))=="committed:different"
    assert processor.effects==11
    assert processor.active==0
    # Cancellation at an await does not retroactively undo prior commits.
    slow=asyncio.create_task(processor.perform(Job("owner-a","slow","x",delay=2)))
    await asyncio.sleep(0)
    slow.cancel()
    try:await slow
    except asyncio.CancelledError:pass
    else:raise AssertionError("cancel did not propagate")
    assert processor.active==0
    try:await run_bounded([],processor,workers=0)
    except ValueError:pass
    else:raise AssertionError("unbounded/invalid worker count")
    print("Async backend: bounded queue, TaskGroup, lost ack, idempotency, cancellation PASS")


if __name__=="__main__":
    asyncio.run(check())
