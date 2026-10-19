"""Optional FastAPI lab. Synthetic output and process-local state; no model calls.
DEMO_API_TOKEN=<local test secret> uvicorn examples.labs.streaming_app:app
Requires compatible fastapi and uvicorn. Not a production authentication/store design.
"""
import asyncio
import json
import os
import secrets
from dataclasses import dataclass, field
from uuid import uuid4
from fastapi import Depends, FastAPI, Header, HTTPException, Request, WebSocket
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

app = FastAPI()


def authenticate(token):
    expected = os.environ.get("DEMO_API_TOKEN")
    return bool(expected) and isinstance(token, str) and secrets.compare_digest(token, expected)


async def principal(authorization: str = Header(default="")):
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not authenticate(token):
        raise HTTPException(401, "Authentication required")
    return "synthetic-user"


class Input(BaseModel):
    message: str = Field(min_length=1, max_length=500)


@dataclass
class Task:
    owner: str
    status: str = "accepted"
    result: str | None = None
    events: list = field(default_factory=list)
    changed: asyncio.Condition = field(default_factory=asyncio.Condition)
    cancelled: asyncio.Event = field(default_factory=asyncio.Event)

    async def emit(self, kind, data):
        async with self.changed:
            event = {"seq": len(self.events) + 1, "type": kind, "data": data}
            self.events.append(event)
            self.changed.notify_all()


tasks: dict[str, Task] = {}
workers: set[asyncio.Task] = set()


def owned(task_id, owner):
    task = tasks.get(task_id)
    if task is None or task.owner != owner:
        raise HTTPException(404, "Task not found")
    return task


async def run(task, message):
    try:
        task.status = "running"
        await task.emit("started", {})
        result = "Synthetic answer: " + message
        for word in result.split():
            if task.cancelled.is_set():
                task.status = "cancelled"
                await task.emit("cancelled", {})
                return
            await task.emit("text_delta", {"text": word + " "})
            await asyncio.sleep(0.08)
        task.result, task.status = result, "complete"
        await task.emit("complete", {"result_available": True})
    except Exception:
        task.status = "failed"
        await task.emit("error", {"category": "internal"})


@app.post("/tasks", status_code=202)
async def create_task(data: Input, owner=Depends(principal)):
    # Bounded local demo capacity. A fleet needs shared admission and retention.
    if len(tasks) >= 100:
        raise HTTPException(503, "Restart this local lab to clear retained tasks")
    task_id = str(uuid4())
    task = tasks[task_id] = Task(owner)
    worker = asyncio.create_task(run(task, data.message))
    workers.add(worker)
    worker.add_done_callback(workers.discard)
    return {"task_id": task_id, "status": "accepted"}


@app.get("/tasks/{task_id}")
async def get_task(task_id: str, owner=Depends(principal)):
    task = owned(task_id, owner)
    return {"task_id": task_id, "status": task.status, "result": task.result}


@app.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str, owner=Depends(principal)):
    task = owned(task_id, owner)
    task.cancelled.set()
    return {"task_id": task_id, "cancel_requested": True, "status": task.status}


@app.get("/tasks/{task_id}/events")
async def stream(task_id: str, request: Request, after: int = 0,
                 last_event_id: str | None = Header(default=None),
                 owner=Depends(principal)):
    task = owned(task_id, owner)
    try:
        cursor = int(last_event_id) if last_event_id is not None else after
    except ValueError:
        raise HTTPException(400, "Invalid event sequence")
    if not 0 <= cursor <= len(task.events):
        raise HTTPException(400, "Sequence unavailable")

    async def events():
        nonlocal cursor
        while not await request.is_disconnected():
            async with task.changed:
                if cursor == len(task.events) and task.status not in {"complete", "cancelled", "failed"}:
                    try:
                        await asyncio.wait_for(task.changed.wait(), timeout=5)
                    except TimeoutError:
                        pass
                batch = list(task.events[cursor:])
            for event in batch:
                cursor = event["seq"]
                yield f'id: {cursor}\nevent: {event["type"]}\ndata: {json.dumps(event)}\n\n'
            if task.status in {"complete", "cancelled", "failed"} and cursor == len(task.events):
                return
            if not batch:
                yield ": heartbeat\n\n"

    return StreamingResponse(events(), media_type="text/event-stream",
        headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"})


@app.websocket("/control")
async def control(socket: WebSocket):
    # First-frame authentication avoids putting credentials in a URL.
    # Use WSS remotely and a reviewed browser origin policy in a real deployment.
    await socket.accept()
    try:
        hello = await asyncio.wait_for(socket.receive_json(), timeout=5)
        if not isinstance(hello, dict) or not authenticate(hello.get("token")):
            await socket.close(code=1008)
            return
        await socket.send_json({"type": "authenticated"})
        for _ in range(20):
            command = await asyncio.wait_for(socket.receive_json(), timeout=20)
            if not isinstance(command, dict) or command.get("type") != "status":
                await socket.send_json({"type": "error", "category": "unsupported"})
                continue
            task_id = command.get("task_id")
            if not isinstance(task_id, str):
                await socket.send_json({"type": "error", "category": "invalid_input"})
                continue
            task = owned(task_id, "synthetic-user")
            await socket.send_json({"type": "status", "task_id": task_id, "status": task.status})
        await socket.close(code=1000)
    except (TimeoutError, ValueError, HTTPException):
        await socket.close(code=1008)
    except Exception:
        # The lab deliberately does not export token-bearing messages.
        return
