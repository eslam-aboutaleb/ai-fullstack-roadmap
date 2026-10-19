import asyncio
from contextlib import asynccontextmanager
state = {'db_open': False}
@asynccontextmanager
async def session():
    state['db_open'] = True
    try: yield
    finally: state['db_open'] = False
async def main():
    async with session():
        task_id = 'T1'
    assert not state['db_open']
    await asyncio.sleep(0)
    return 'closed-before-provider'
print(asyncio.run(main()))
