import asyncio
from contextvars import ContextVar
principal = ContextVar("principal")
async def scoped(user):
    token = principal.set(user)
    try:
        await asyncio.sleep(0)
        return principal.get()
    finally:
        principal.reset(token)
async def demo():
    assert await asyncio.gather(scoped("a"), scoped("b")) == ["a", "b"]
if __name__ == "__main__": asyncio.run(demo())
