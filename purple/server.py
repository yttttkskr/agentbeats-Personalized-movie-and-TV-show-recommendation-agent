# agentbeats/purple/server.py

import argparse
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

from executor import Executor
from starlette.responses import JSONResponse
from starlette.routing import Route

def main():

    parser = argparse.ArgumentParser(description="Run the Purple Agent server.")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind the server")
    parser.add_argument("--port", type=int, default=9010, help="Port to bind the server")
    parser.add_argument("--card-url", type=str, help="URL to advertise in the agent card")
    args = parser.parse_args()


    skill = AgentSkill(
        id="baseline-purple-agent-v1",
        name="Baseline Recommendation Agent",
        description="Provides baseline recommendations by returning top-5 candidate items from the input list.",
        tags=["recommendation", "baseline", "ranking", "candidate-selection"],
        examples=[
            "Input: {'input': {'candidate_items': ['A', 'B', 'C', 'D', 'E', 'F']}}",
            "Output: {'prediction': ['A', 'B', 'C', 'D', 'E'], 'explanation': 'Returned top-5 candidate items.'}"
        ]
    )

    base_url = args.card_url or f"http://{args.host}{args.port}"
    base_url = base_url.rstrip("/") + "/"

    agent_card = AgentCard(
        name="Baseline Purple Agent",
        description="A2A-compatible purple agent for baseline recommendation tasks. Returns top-5 items from candidate lists.",
        url=base_url,
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
        preferredTransport="JSONRPC",
        protocolVersion="0.3.0"
    )


    request_handler = DefaultRequestHandler(
        agent_executor=Executor(),
        task_store=InMemoryTaskStore(),
    )


    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )


    print(f"Starting Purple Agent on http://{args.host}:{args.port}")
    print(f"Agent Card: {agent_card.url}.well-known/agent-card.json")
    app = server.build()


    async def health(request):
        return JSONResponse({"status": "ok", "agent": "green"})

    app.router.routes.append(
        Route("/health", endpoint=health, methods=["GET"])
    )


    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == '__main__':
    main()