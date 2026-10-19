import asyncio
async def main():
    gate, state = asyncio.Semaphore(2), {'active': 0, 'peak': 0}
    async def tool():
        async with gate:
            state['active'] += 1
            state['peak'] = max(state['peak'], state['active'])
            try:
                await asyncio.sleep(0)
            finally:
                state['active'] -= 1
    await asyncio.gather(*(tool() for _ in range(5)))
    return state['peak']
print(asyncio.run(main()))
