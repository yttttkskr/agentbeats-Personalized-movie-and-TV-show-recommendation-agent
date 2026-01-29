# agentbeats/green/server.py
import argparse
import asyncio
import os

from starlette.responses import JSONResponse
from starlette.routing import Route
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, AgentSkill, AgentCapabilities
from executor import Executor



class DebugRequestHandler(DefaultRequestHandler):
    async def handle_task_create(self, request):
        body = await request.json()
        print("\n Receive new Task")
        print(body)
        return await super().handle_task_create(request)

    async def handle_message_create(self, request, task_id: str):
        body = await request.json()
        print(f"\n Task {task_id} receive Message")
        print(body)
        return await super().handle_message_create(request, task_id)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9009)
    parser.add_argument("--card-url", type=str)
    parser.add_argument("--purple-url", type=str, help="Purple Agent URL")
    args = parser.parse_args()

    skill = AgentSkill(
        id="agentbeats-green-evaluator-v1",
        name="Multi-Agent Performance Evaluator",
        description="Evaluates Purple Agents using personas and multi-criteria scoring.",
        tags=["evaluation", "benchmark"],
        examples=["Evaluate Purple Agent"]
    )

    agent_card = AgentCard(
        name="Multi-Agent Performance Evaluator",
        description="Generates evaluation tasks based on personas and scores purple agents.",
        url=args.card_url or f"http://{args.host}:{args.port}/",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
        preferredTransport="JSONRPC",
        protocolVersion="0.3.0",
    )

    request_handler = DebugRequestHandler(
        agent_executor=Executor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )

    print(f"Starting Green Agent on http://{args.host}:{args.port}")
    print(f"Agent Card: {agent_card.url}.well-known/agent-card.json")
    app = server.build()

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
