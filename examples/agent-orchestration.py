import asyncio
async def gather_sources(searchers, query, concurrency=2):
    semaphore = asyncio.Semaphore(concurrency)
    async def one(name, search):
        async with semaphore:
            try:
                return {"source": name, "status": "ok", "items": await search(query)}
            except (TimeoutError, OSError):
                return {"source": name, "status": "unavailable", "items": []}
    return await asyncio.gather(*(one(name, fn) for name, fn in searchers.items()))
async def demo():
    async def local(query): return ["synthetic passage"]
    assert (await gather_sources({"demo": local}, "hours"))[0]["status"] == "ok"
if __name__ == "__main__": asyncio.run(demo())
# Add deadlines, shared quotas, and task persistence around real services.
