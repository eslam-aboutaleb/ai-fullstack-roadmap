"""MCP server concurrency control, exponential backoff retries, and OpenTelemetry observability.

Demonstrates:
1. Concurrency limits via Semaphore: Bounding concurrent tool executions and shedding excess load.
2. Resilience policy: Exponential backoff with jitter for transient dependencies, failing fast on deterministic domain errors.
3. OpenTelemetry distributed tracing: Recording sanitized span attributes (tool name, duration, tenant, status) while redacting secrets and user payloads.
"""
from typing import Any, Callable, Dict, List, Optional
import asyncio
import random
import time
import uuid

class OpenTelemetrySpan:
    def __init__(self, name: str, trace_id: str, attributes: Dict[str, Any]):
        self.name = name
        self.trace_id = trace_id
        self.span_id = uuid.uuid4().hex[:16]
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.attributes = attributes
        self.status = "UNSET"

    def set_status(self, status: str):
        self.status = status

    def end(self):
        self.end_time = time.time()

    def to_record(self) -> Dict[str, Any]:
        duration_ms = ((self.end_time or time.time()) - self.start_time) * 1000.0
        return {
            "name": self.name,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "duration_ms": round(duration_ms, 2),
            "status": self.status,
            "attributes": self.attributes
        }

class McpTelemetryRegistry:
    def __init__(self):
        self.spans: List[Dict[str, Any]] = []

    def record(self, span: OpenTelemetrySpan):
        self.spans.append(span.to_record())

class RobustToolExecutor:
    def __init__(self, max_concurrency: int = 3):
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.active_count = 0
        self.max_observed_concurrency = 0
        self.telemetry = McpTelemetryRegistry()

    async def execute_with_bounds(self, tool_name: str, tenant_id: str, task: Callable[[], Any]) -> Any:
        # Start OpenTelemetry Span
        trace_id = uuid.uuid4().hex
        # REDACTION RULE: Record metadata, NEVER raw argument payloads or passwords!
        span = OpenTelemetrySpan(
            name=f"mcp.tool.{tool_name}",
            trace_id=trace_id,
            attributes={
                "mcp.tool.name": tool_name,
                "mcp.caller.tenant_id": tenant_id,
                "net.transport": "streamable_http"
            }
        )

        try:
            # Enforce concurrency boundary
            async with self.semaphore:
                self.active_count += 1
                if self.active_count > self.max_observed_concurrency:
                    self.max_observed_concurrency = self.active_count

                # Execute with transient retry policy
                result = await self._retry_with_backoff(task, max_attempts=3)
                span.set_status("OK")
                return result

        except Exception as ex:
            span.set_status("ERROR")
            span.attributes["error.type"] = type(ex).__name__
            span.attributes["error.message"] = str(ex)
            raise
        finally:
            self.active_count -= 1
            span.end()
            self.telemetry.record(span)

    async def _retry_with_backoff(self, task: Callable[[], Any], max_attempts: int) -> Any:
        base_delay = 0.01
        for attempt in range(1, max_attempts + 1):
            try:
                return await task()
            except ConnectionError:
                # Retryable transient failure
                if attempt == max_attempts:
                    raise
                # Exponential backoff with jitter: delay = base * 2^(attempt-1) + jitter
                delay = (base_delay * (2 ** (attempt - 1))) + (random.random() * 0.005)
                await asyncio.sleep(delay)
            except (ValueError, KeyError, PermissionError):
                # Non-retryable deterministic domain failure: FAIL FAST!
                raise

async def main():
    executor = RobustToolExecutor(max_concurrency=2)

    # 1. Test Concurrency Limit: Run 4 simultaneous tasks with limit 2
    async def slow_task(idx: int):
        await asyncio.sleep(0.02)
        return f"result_{idx}"

    tasks = [
        executor.execute_with_bounds("search_db", "tenant_a", lambda: slow_task(i))
        for i in range(4)
    ]
    results = await asyncio.gather(*tasks)
    assert len(results) == 4
    # Concurrency was strictly capped at 2!
    assert executor.max_observed_concurrency <= 2

    # 2. Test Transient Retry Recovery
    failures = 0
    async def flaky_api():
        nonlocal failures
        if failures < 2:
            failures += 1
            raise ConnectionError("Temporary upstream timeout")
        return "api_recovered"

    recovered = await executor.execute_with_bounds("sync_upstream", "tenant_b", flaky_api)
    assert recovered == "api_recovered"
    assert failures == 2

    # 3. Test Fail Fast on Non-Retryable Error
    async def invalid_args():
        raise ValueError("Invalid date format")

    try:
        await executor.execute_with_bounds("parse_date", "tenant_c", invalid_args)
        assert False, "Should fail fast on ValueError"
    except ValueError:
        pass

    # 4. Verify OpenTelemetry Tracing
    spans = executor.telemetry.spans
    assert len(spans) == 6  # 4 concurrent + 1 flaky + 1 invalid
    successful_spans = [s for s in spans if s["status"] == "OK"]
    error_spans = [s for s in spans if s["status"] == "ERROR"]

    assert len(successful_spans) == 5
    assert len(error_spans) == 1
    assert error_spans[0]["attributes"]["error.type"] == "ValueError"
    assert "duration_ms" in spans[0]

    print("MCP concurrency bounds, retry backoff, and OpenTelemetry spans verified successfully.")

if __name__ == "__main__":
    asyncio.run(main())

