"""Real SDK clients over STDIO and loopback HTTP. No model or real external effect.

Requires requirements-advanced.txt. Tested profiles are asserted, not inferred from
an SDK package name. OAuth and multi-tenant deployment are separate acceptance work.
"""
from contextlib import asynccontextmanager
from importlib.metadata import version
from pathlib import Path
import asyncio
import json
import socket
import sys

import httpx
import uvicorn
from pydantic import BaseModel
from mcp import Client, StdioServerParameters
from mcp.server import MCPServer
from a2a.client import ClientConfig, create_client
from a2a.helpers import new_task_from_user_message, new_text_message, new_text_part
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.types import (AgentCapabilities, AgentCard, AgentInterface, AgentSkill,
                       GetTaskRequest, Role, SendMessageRequest, TaskState)
from starlette.applications import Starlette

MCP_PROFILE = '2026-07-28'
MCP = MCPServer('Evidence contract', version='1.0.0')


class Policy(BaseModel):
    source_id: str
    text: str


@MCP.tool()
def read_policy(source_id: str) -> Policy:
    """Read the single public fixture document; private identities are denied."""
    if source_id != 'public@1':
        raise ValueError('Source is outside this fixture capability')
    return Policy(source_id=source_id, text='Refund window: 14 days.')


@asynccontextmanager
async def serve(app):
    """Bind an ephemeral port before launching, avoiding a free-port race."""
    sock = socket.socket(); sock.bind(('127.0.0.1', 0)); sock.listen(128)
    config = uvicorn.Config(app, log_level='critical', lifespan='on')
    runner = uvicorn.Server(config)
    task = asyncio.create_task(runner.serve(sockets=[sock]))
    try:
        async with asyncio.timeout(10):
            while not runner.started:
                if task.done():
                    await task
                    raise RuntimeError('Server exited before readiness')
                await asyncio.sleep(0.01)
        yield f'http://127.0.0.1:{sock.getsockname()[1]}'
    finally:
        runner.should_exit = True
        try:
            async with asyncio.timeout(5):
                await task
        except TimeoutError:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        sock.close()


async def exercise_mcp(target) -> str:
    async with Client(target, read_timeout_seconds=3) as client:
        profile = client.session.protocol_version
        assert profile == MCP_PROFILE, profile
        listing = await client.list_tools()
        assert any(tool.name == 'read_policy' for tool in listing.tools)
        valid = await client.call_tool('read_policy', {'source_id': 'public@1'})
        assert not valid.is_error and valid.structured_content['source_id'] == 'public@1'
        denied = await client.call_tool('read_policy', {'source_id': 'private@1'})
        assert denied.is_error, denied
        malformed = await client.call_tool('read_policy', {'source_id': {'not': 'a string'}})
        assert malformed.is_error, malformed
        return profile


class EvidenceAgent(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        # This agent has no authenticated tenants and only returns public fixture text.
        task = context.current_task or new_task_from_user_message(context.message)
        if not context.current_task:
            await event_queue.enqueue_event(task)
        updater = TaskUpdater(event_queue, task.id, task.context_id)
        await updater.update_status(TaskState.TASK_STATE_WORKING)
        await updater.add_artifact([new_text_part(text='public@1: Refund window: 14 days.', media_type='text/plain')], name='Evidence')
        await updater.update_status(TaskState.TASK_STATE_COMPLETED)

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        await updater.update_status(TaskState.TASK_STATE_CANCELED)


def a2a_app():
    # The URL is set to the bound loopback origin by the harness before discovery.
    card = AgentCard(name='Public evidence fixture', description='Read-only public evidence', version='1.0.0',
        default_input_modes=['text/plain'], default_output_modes=['text/plain'],
        capabilities=AgentCapabilities(streaming=True),
        supported_interfaces=[AgentInterface(protocol_binding='JSONRPC', url='http://127.0.0.1', protocol_version='1.0')],
        skills=[AgentSkill(id='public-evidence', name='Public evidence', description='Return a public fixture', tags=['evidence'])])
    handler = DefaultRequestHandler(EvidenceAgent(), InMemoryTaskStore(), card)
    routes = create_agent_card_routes(card) + create_jsonrpc_routes(handler, '/', enable_v0_3_compat=False)
    return Starlette(routes=routes), card


async def exercise_a2a() -> dict:
    app, card = a2a_app()
    async with serve(app) as origin:
        card.supported_interfaces[0].url = origin + '/'
        async with httpx.AsyncClient(timeout=5) as http:
            response = await http.get(origin+'/.well-known/agent-card.json')
            response.raise_for_status()
            # A real discovery request, not an in-memory card passed to the client.
            assert response.json()['supportedInterfaces'][0]['protocolVersion'] == '1.0'
            client = await create_client(origin, client_config=ClientConfig(streaming=True, httpx_client=http))
            try:
                updates = []
                request = SendMessageRequest(message=new_text_message('What is the public policy?', role=Role.ROLE_USER))
                async for event in client.send_message(request):
                    updates.append(event)
                task_ids = [event.task.id for event in updates if event.HasField('task')]
                assert task_ids, 'Stream omitted task identity'
                read = await client.get_task(GetTaskRequest(id=task_ids[0]))
                assert read.status.state == TaskState.TASK_STATE_COMPLETED, read
                assert read.artifacts and 'public@1' in str(read.artifacts)
                assert any(event.HasField('status_update') and event.status_update.status.state == TaskState.TASK_STATE_COMPLETED for event in updates)
                bad_version = await http.post(origin+'/', headers={'A2A-Version':'99.0'}, json={
                    'jsonrpc':'2.0','id':1,'method':'GetTask','params':{'id':read.id}})
                assert bad_version.status_code >= 400 or 'error' in bad_version.json(), bad_version.text
                return {'profile': '1.0', 'transport': 'JSONRPC/SSE', 'discovery': True,
                        'updates': len(updates), 'terminal_state': 'completed', 'task_readback': True,
                        'unsupported_version_rejected': True}
            finally:
                await client.close()


async def verify() -> None:
    assert version('mcp') == '2.3.0' and version('a2a-sdk') == '1.2.3'
    stdio = StdioServerParameters(command=sys.executable, args=[str(Path(__file__).resolve()), '--stdio'])
    local_profile = await exercise_mcp(stdio)
    async with serve(MCP.streamable_http_app(stateless_http=True, json_response=True)) as origin:
        remote_profile = await exercise_mcp(origin+'/mcp')
    a2a = await exercise_a2a()
    print(json.dumps({'mcp_sdk':version('mcp'),'mcp_stdio_profile':local_profile,
                      'mcp_http_profile':remote_profile,'mcp_invalid_input_and_denial':'pass',
                      'a2a_sdk':version('a2a-sdk'),'a2a':a2a}))


if __name__ == '__main__':
    if '--stdio' in sys.argv:
        MCP.run(transport='stdio')
    else:
        asyncio.run(verify())
