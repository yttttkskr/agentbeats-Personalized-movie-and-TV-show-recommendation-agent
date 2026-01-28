# Auto-generated from scenario.toml

services:
  green-agent:
    image: ghcr.io/yttttkskr/green.v2:latest
    platform: linux/amd64
    container_name: green-agent
    environment:
      - PYTHONUNBUFFERED=1
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - PURPLE_AGENT_URL=http://purple_agent:9010
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9009/.well-known/agent-card.json"]
      interval: 5s
      timeout: 3s
      retries: 10
      start_period: 30s
    depends_on:
      purple_agent:
        condition: service_healthy
    networks:
      - agent-network

  purple_agent:
    image: ghcr.io/yttttkskr/purple.v2:latest
    platform: linux/amd64
    container_name: purple_agent
    environment:
      - PYTHONUNBUFFERED=1
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9010/.well-known/agent-card.json"]
      interval: 5s
      timeout: 3s
      retries: 10
      start_period: 30s
    networks:
      - agent-network

  agentbeats-client:
    image: ghcr.io/agentbeats/agentbeats-client:v1.0.0
    platform: linux/amd64
    container_name: agentbeats-client
    volumes:
      - ./a2a-scenario.toml:/app/scenario.toml
      - ./output:/app/output
    command: ["scenario.toml", "output/results.json"]
    depends_on:
      green-agent:
        condition: service_healthy
      purple_agent:
        condition: service_healthy
    networks:
      - agent-network

networks:
  agent-network:
    driver: bridge
