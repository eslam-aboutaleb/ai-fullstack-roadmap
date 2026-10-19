import asyncio
async def read(name):
    await asyncio.sleep(0)
    return name
async def main():
    return await asyncio.gather(read('dense'), read('lexical'))
print(asyncio.run(main()))
