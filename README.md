# Personalized-movie-and-TV-show-recommendation-agent
For Agentbeats compitition. This responsiry contains both green and purple agent, 

## Project Structure

```lua
main/
├─green/
│  └─ data/
│  └─ personas/
│  ├─prompts/
│  ├─results/
│  ├─.dockerignore
│  ├─.env.example
│  ├─_init_.py
│  ├─agent.py
│  ├─Dockerfile
│  ├─evaluator.py
│  ├─executor.py
│  ├─llm.py
│  ├─messenger.py
│  ├─requirements.txt
│  ├─scoring_rules.py
│  ├─server.py
│  └─ task_generator.py
└─ purple
   ├─executor.py
   ├─Dockerfile
   └─ server.py

```


## Start

```bash
docker run -e DEEPSEEK_API_KEY="your_key" green
docker run  purple
```
