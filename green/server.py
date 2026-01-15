# agentbeats/green/server.py
import argparse
import asyncio
from starlette.responses import JSONResponse
from starlette.routing import Route
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, AgentSkill, AgentCapabilities

from agent import GreenA2AAgent

# 初始化 Green Agent
green_agent = GreenA2AAgent()
purple_url = "http://127.0.0.1:9010"  # Purple Agent 地址
output_file="results_general_user1.json"
async def auto_publish_tasks():
    for persona_name in green_agent.personas:
        await green_agent.auto_publish_persona_tasks(persona_name, purple_url)

class DebugRequestHandler(DefaultRequestHandler):
    async def handle_task_create(self, request):
        body = await request.json()
        print("\n🔥🔥 收到新 Task")
        print(body)
        return await super().handle_task_create(request)

    async def handle_message_create(self, request, task_id: str):
        body = await request.json()
        print(f"\n💬💬 Task {task_id} 收到 Message")
        print(body)
        return await super().handle_message_create(request, task_id)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9009)
    parser.add_argument("--card-url", type=str)
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
        agent_executor=green_agent,
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )

    app = server.build()

    # health check
    async def health(request):
        return JSONResponse({"status": "ok", "agent": "green"})
    app.router.routes.append(Route("/health", endpoint=health, methods=["GET"]))

    # 自动发布任务
    @app.on_event("startup")
    async def startup_event():
        asyncio.create_task(auto_publish_tasks())

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
