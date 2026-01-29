# Personalized-movie-and-TV-show-recommendation-agent


## Overview

This project is developed for the AgentBeats Competition and focuses on the evaluation of a movie and TV content recommendation agent(purple agent).

The Green Agent acts as an automatic evaluator that assesses the performance of the Purple Agent across dynamically generated recommendation tasks. During the evaluation process, the Green Agent generates test scenarios, interacts with the Purple Agent, and analyzes its outputs. The evaluation emphasizes the tested agent’s LLM-based semantic reasoning ability, response consistency, and explainability, producing quantitative performance scores. Structured scoring criteria are provided as reference guidelines and do not directly determine the final evaluation results.

Our implementation is specifically designed for movie and TV recommendation scenarios. We construct a diverse set of test cases covering varying user preferences, genres, and viewing histories. These scenarios range from common recommendation situations to more challenging and edge cases, ensuring comprehensive coverage. Each test case evaluates whether the Purple Agent can deliver relevant, coherent, and interpretable recommendations under different content contexts.

Due to the diversity of user profiles and recommendation scenarios, agent performance is expected to vary across tasks, allowing for a more fine-grained and realistic assessment of recommendation capabilities.


## Team Information

**Team**: **try-try**

**Member**:  **J R, Yao** and **Y T, Feng**

**Official Profile**: https://agentbeats.dev/yttttkskr

**Demo Video**:  https://youtu.be/to5L9YSCaF0


## Evaluation Pipeline

The evaluation pipeline is fully automated and consists of a multi-stage interaction between the Green Agent (evaluator) and the Purple Agent (tested recommendation agent). Each evaluation is organized around a user persona, under which multiple recommendation tasks are generated and assessed.

### 1. Persona-based Task Generation
For each user persona, the Green Agent uses a large language model (DeepSeek) to generate multiple recommendation instructions.

Each instruction represents a distinct recommendation task derived from the same persona, varying in phrasing, emphasis, or contextual constraints (e.g., genre focus, viewing habits, or narrative preferences). This design enables robustness testing across semantically similar but non-identical tasks.

Each task follows a structured format for example:

```json
{
    "task_id": "task-x",
    "instruction": "Natural language description of the task",
    "input":{
        "history": ["user history movie 1","..."],
        "persona": {"...."},
        "candidate_items": ["Movie A","..."],
        "k":5
    }
    "ground_truth": [
        {"title": "Correct Movie 1"},
        {"title": "Correct Movie 2"}
    ]
}
```

### 2. Agent Interaction
Each generated instruction is passed to the Purple Agent, which is responsible for producing movie recommendations.  

For every task, the Purple Agent returns:
- A ranked list of **five recommended movies**
- A brief explanation describing the recommendation output

The Purple Agent operates independently and does not have access to the evaluation logic.

### 3. Multi-dimensional Evaluation

The evaluation framework consists of three complementary dimensions:

- **Semantic Reasoning**: Measures the agent’s ability to understand user preferences, content context, and recommendation intent, and to generate semantically relevant and coherent recommendations.

- **Consistency**: Evaluates the stability of the agent’s recommendations across similar or related scenarios, ensuring logical alignment and avoidance of contradictory outputs.

- **Explainability**: Assesses whether the agent can provide clear, interpretable, and user-aligned explanations for its recommendations, making the decision process transparent and understandable.

Examples:

- A purple agent recommending genre-aligned movies with clear explanations --> high semantic reasoning, consistency, explainability, and structural scores.
- A purple agent providing partially relevant or inconsistent recommendations --> medium scores.
- A purple agent giving irrelevant recommendations with no explanations --> low
scores across all metrics.

In addition, a **structural score** is computed as a heuristic reference metric for diagnostic purposes only and does not directly influence the final score.

### 4. Task-level Scoring

Each task receives individual dimension scores as well as a final aggregated score. This allows fine-grained analysis of agent performance under specific recommendation instructions.

### 5. Persona-level Aggregation

For each persona, task-level scores are aggregated to produce an overall **persona score**, reflecting the Purple Agent’s performance across multiple recommendation scenarios derived from the same user profile.

### 6. Result Output

All evaluation results are stored in a structured JSON format, including:
- Persona-level scores
- Task-level instructions, outputs, and evaluation metrics

This design enables transparent analysis, reproducibility, and easy extension to additional personas or recommendation domains.


## Project Structure

```bash
├───.env.example
│
├───green  # Evaluation agent implementation
│   │   .dockerignore
│   │   agent.py
│   │   Dockerfile
│   │   evaluator.py
│   │   executor.py
│   │   llm.py
│   │   messenger.py
│   │   requirements.txt
│   │   scoring_rules.py
│   │   server.py
│   │   task_generator.py
│   │   __init__.py
│   │
│   ├───data
│   │   ├───personas  # example of character portrait
│   │   │       personas.json
│   │   │
│   │   └───prompts  # Prompt templates for agents
│   │           eval_prompt.txt
│   │           task_prompt.txt
│   │
│   └───results  # computational results
│       └───results_General User1.json
│
└───purple  # Tested recommendation agent (baseline)
    │   .dockerignore
    │   Dockerfile
    │   executor.py
    │   purple_agent.py
    │   README.md
    │   requirements.txt
    └───server.py
```


## Quick Start

The entire evaluation process is non-interactive and requires no manual intervention after configuration.This project supports both **GitHub Actions–based execution** (recommended for reproducibility) and **local execution via Docker**.

### Execute via GitHub Actions (Recommended)

1. Configure API Key

   Add your DeepSeek API key as a GitHub Actions secret.  
   Follow the official GitHub documentation for *Creating secrets for a repository*.  
   Set:
   - **Name**: `DEEPSEEK_API_KEY`
   - **Secret**: your DeepSeek API key

2. Configure Evaluation Scenario

    Modify the `[config]` section in the `scenario.toml` file. The `[config]` section defines the user personas used for evaluation, which can be selected from: `green.data.personas.personas`.

3. Trigger the Workflow
    Commit and push the updated `scenario.toml` file. This will automatically trigger a GitHub Actions workflow that runs the evaluation in a reproducible environment.

Upon completion, the workflow parses the A2A artifacts generated by the Green Agent and produces a structured JSON file containing persona-level and task-level evaluation results.

### Execute Locally (Docker)

Local execution is supported via pre-built Docker images.

1. Pull docker image

```bash
docker pull ghcr.io/yttttkskr/green.v1:latest
docker pull ghcr.io/yttttkskr/purple.v1:latest
```

2. Run the Green Agent and the Purple Agent

```bash
docker run -e DEEPSEEK_API_KEY=sk-yourkey green.v1:latest 
docker run purple.v1:latest 
```

Both agents run without requiring any manual interaction after startup.

## Limitations & Future Work

### Limitations

The current evaluation framework relies on LLM-based judgment, which may introduce a degree of subjectivity despite structured scoring criteria. Consistency evaluation is limited to a fixed number of tasks per persona, and the diversity of personas and recommendation contexts remains constrained compared to real-world scenarios. The Purple Agent is implemented as a baseline and does not yet incorporate long-term user modeling or multi-turn feedback mechanisms.

### Future Work

Future work will primarily focus on improving the Purple Agent’s recommendation performance, including richer user preference modeling, enhanced semantic reasoning, and multi-turn interaction capabilities.

In parallel, we plan to extend the Green Agent to strengthen evaluation robustness and scalability. Directions include ensemble-based evaluation to mitigate single-model bias, expanded consistency testing across longer task sequences, adaptive task generation, and potential human-in-the-loop validation for critical evaluation cases.
