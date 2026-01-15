# agentbeats/green/task_generator.py

import json
from typing import Dict, Any, List
from llm import deepseek_chat


class TaskGenerator:
    def __init__(self, task_prompt_path: str):

        with open(task_prompt_path, "r", encoding="utf-8") as f:
            self.base_prompt = f.read()

    def generate_tasks(self, persona: Dict[str, Any], task_count: int = 3) -> List[Dict[str, Any]]:
        """
        Generate tasks for a persona using the LLM.
        Returns a list of task dicts.
        """
        prompt = (
            self.base_prompt
            .replace("{{persona}}", json.dumps(persona, ensure_ascii=False))
            .replace("{{task_count}}", str(task_count))
        )

        messages = [
            {"role": "system", "content": "You are a benchmark task generator. Output strictly in JSON format."},
            {"role": "user", "content": prompt}
        ]

        raw_output = deepseek_chat(messages, model="deepseek-chat", temperature=0.0)

        # Attempt to parse JSON
        try:
            tasks = json.loads(raw_output)
            if not isinstance(tasks, list):
                # If the output is not a list, wrap in a single-item list
                tasks = [tasks]
            return tasks
        except Exception:
            # Fallback: return raw text with error info
            return [{"raw_output": raw_output, "error": "JSON parse failed"}]



if __name__ == "__main__":
    sample_persona = {
        "name": "TestUser",
        "preferences": ["sci-fi", "action", "gaming"],
        "history": ["speed movie", "avengers"]
    }

    tg = TaskGenerator("./prompts/task_prompt.txt")
    tasks = tg.generate_tasks(sample_persona, task_count=3)

    print(json.dumps(tasks, ensure_ascii=False, indent=2))
