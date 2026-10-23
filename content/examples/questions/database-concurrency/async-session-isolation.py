"""Demonstrate why async database frameworks require one session per concurrent task."""
import asyncio

class MockAsyncSession:
    """Simulate an async database session (such as SQLAlchemy AsyncSession)."""
    def __init__(self, session_id):
        self.session_id = session_id
        self.is_busy = False
        self.transaction_depth = 0

    async def execute_query(self, task_name, duration=0.01):
        if self.is_busy:
            raise RuntimeError(
                f"Concurrent execution detected in session {self.session_id}! "
                f"Task '{task_name}' interleaved into an ongoing query."
            )
        self.is_busy = True
        try:
            await asyncio.sleep(duration) # Simulate network database I/O
            return f"Result for {task_name}"
        finally:
            self.is_busy = False

async def unsafe_shared_session():
    """Anti-pattern: Sharing a single session across concurrent tasks raises concurrency corruption."""
    shared = MockAsyncSession("shared_01")
    
    async def worker(name):
        return await shared.execute_query(name)

    # Concurrently launching both tasks using the same session instance causes interleaving conflict:
    results = await asyncio.gather(worker("Task A"), worker("Task B"), return_exceptions=True)
    has_error = any(isinstance(r, RuntimeError) for r in results)
    assert has_error, "Interleaved execution on shared session raised concurrency error"
    return has_error

async def safe_isolated_sessions():
    """Best practice: Each concurrent coroutine/request receives its own dedicated scoped session."""
    async def worker(name, session_id):
        session = MockAsyncSession(session_id) # Scoped session per task
        return await session.execute_query(name)

    results = await asyncio.gather(worker("Task A", "sess_A"), worker("Task B", "sess_B"))
    assert results == ["Result for Task A", "Result for Task B"]
    return results

async def main():
    shared_failed = await unsafe_shared_session()
    isolated_succeeded = await safe_isolated_sessions()
    print(f"Async session isolation: shared_conflict={shared_failed}, isolated_results={len(isolated_succeeded)}")

if __name__ == '__main__':
    asyncio.run(main())
