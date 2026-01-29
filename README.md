# Personalized-movie-and-TV-show-recommendation-agent


## Overview

This project is developed for the AgentBeats Competition and focuses on the evaluation of a movie content recommendation agent(purple agent).

The Green Agent acts as an automatic evaluator that assesses the performance of a the Purple Agent across dynamically generated recommendation tasks. During the evaluation process, the Green Agent generates test scenarios, interacts with the Purple Agent, and analyzes its outputs. The evaluation emphasizes the tested agent’s LLM-based semantic reasoning ability, response consistency, and explainability, producing quantitative performance scores. Structured scoring criteria are provided as reference guidelines and do not directly determine the final evaluation results.

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

First, create a `.env` file based on `.env.example` and add your DeepSeek API key.

Then, you may modify the `[config]` section in the `scenario.toml` file.The `[config]` contains user personas for testing, which can be selected from `green.data.personas.personas`.

Commit and push your `scenario.toml` file. This will trigger a GitHub Action workflow that runs the assessment in a reproducible environment. Once the assessment completes successfully, the workflow automatically parses the A2A artifacts generated by the green agent into a structured JSON results file.


## Limitations & Future Work

### Limitations

The current evaluation framework relies on LLM-based judgment, which may introduce a degree of subjectivity despite structured scoring criteria. Consistency evaluation is limited to a fixed number of tasks per persona, and the diversity of personas and recommendation contexts remains constrained compared to real-world scenarios. The Purple Agent is implemented as a baseline and does not yet incorporate long-term user modeling or multi-turn feedback mechanisms.

### Future Work

Future work will primarily focus on improving the Purple Agent’s recommendation performance, including richer user preference modeling, enhanced semantic reasoning, and multi-turn interaction capabilities.

In parallel, we plan to extend the Green Agent to strengthen evaluation robustness and scalability. Directions include ensemble-based evaluation to mitigate single-model bias, expanded consistency testing across longer task sequences, adaptive task generation, and potential human-in-the-loop validation for critical evaluation cases.
