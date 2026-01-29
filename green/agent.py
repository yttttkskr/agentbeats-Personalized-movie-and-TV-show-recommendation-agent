import os
import json
from dataclasses import dataclass
from typing import Dict, Any, List

import httpx

from evaluator import Evaluator
from messenger import Messenger
from task_generator import TaskGenerator

from a2a.types import Part, DataPart, TextPart
from a2a.utils import new_agent_text_message



@dataclass
class EvalRequest:
    participants: Dict[str, str]
    config: Dict[str, Any]



class GreenA2AAgent:
    def __init__(self):
        persona_dir = "data/personas"
        prompts_dir = "data/prompts"

        self.personas = self._load_personas(persona_dir)

        self.repeat_runs = 3
        self.llm_temperature = 0.0
        self.version = "agentbeats-green-v1"

        task_prompt_file = os.path.join(prompts_dir, "task_prompt.txt")
        eval_prompt_file = os.path.join(prompts_dir, "eval_prompt.txt")

        self.task_generator = TaskGenerator(task_prompt_file)
        self.evaluator = Evaluator(eval_prompt_file)
        self.messenger = Messenger()

    # =========================
    # Persona 加载
    # =========================
    def _load_personas(self, persona_dir: str) -> Dict[str, dict]:
        
        personas = {}

        if not os.path.exists(persona_dir):
            os.makedirs(persona_dir, exist_ok=True)
            return personas

        for file in os.listdir(persona_dir):
            if not file.endswith(".json"):
                continue

            path = os.path.join(persona_dir, file)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

                # 如果文件里是 list，就逐个取出
                if isinstance(data, list):
                    for p in data:
                        if not isinstance(p, dict) or "name" not in p:
                            continue
                        personas[p["name"]] = p  # 用 persona 中的 name 做 key
                # 如果文件里是 dict，取 name
                elif isinstance(data, dict):
                    if "name" in data:
                        personas[data["name"]] = data

        return personas

    # =========================
    # A2A 协议入口
    # =========================
    async def run(self, msg, updater):
        

        
        if not msg.parts or not msg.parts[0].root:
            await updater.failed(new_agent_text_message("Empty A2A message"))
            return

        root = msg.parts[0].root
        if isinstance(root, TextPart):
            raw_text = root.text
        elif isinstance(root, DataPart):
            raw_text = json.dumps(root.data)
        else:
            await updater.failed(new_agent_text_message("Unsupported message part type"))
            return

        
        try:
            payload = json.loads(raw_text)
        except json.JSONDecodeError:
            await updater.failed(new_agent_text_message("Message is not valid JSON"))
            return

        participants = payload.get("participants", {})
        config = payload.get("config", {})

        purple_url = participants.get("purple_agent")
        if not purple_url:
            await updater.failed(new_agent_text_message("Missing participants.purple_agent"))
            return

        
        request = EvalRequest(
            participants={"purple_agent": purple_url},
            config=config
        )

        
        try:
            # 如果消息里有 persona，则只评估该 persona
            # 如果没有 persona，则评估所有 persona
            if "persona" in config:
                personas_to_run = [config["persona"]]
            else:
                personas_to_run = list(self.personas.keys())

            for persona_name in personas_to_run:
                await self._run_evaluation(request, updater, persona_name)

        except Exception as e:
            await updater.failed(new_agent_text_message(f"Evaluation failed: {e}"))
            return

        
        await updater.complete(new_agent_text_message("Green agent evaluation completed"))

    
    async def _run_evaluation(self, request: EvalRequest, updater, persona_name: str):
        
        task_count = int(request.config.get("task_count", 3))
        purple_url = request.participants["purple_agent"]
        persona_name = request.config["persona"]
        print(persona_name)

        await self.auto_publish_persona_tasks(persona_name, purple_url, updater, task_count)

    
    async def auto_publish_persona_tasks(self, persona_name: str, purple_url: str, updater=None, task_count: int = 3):


        # 取 persona

        persona = self.personas[persona_name]

        print(f"Running evaluation for persona: {persona_name}")
        tasks = self.task_generator.generate_tasks(persona, task_count=task_count)
        all_results: List[Dict[str, Any]] = []

        for task in tasks:
            
            task["user_history"] = persona.get("history", [])
            outputs = []


            for run_idx in range(self.repeat_runs):
                try:
                    reply = await self.messenger.talk_to_agent(
                        message=json.dumps(task, ensure_ascii=False),
                        url=purple_url,
                        new_conversation=(run_idx == 0)
                    )
                    text = reply.strip()

                    # 去掉 ``` 和 json 前缀
                    if text.startswith("```"):
                        text = text.strip("` \n")
                    if text.startswith("json"):
                        text = text[4:].strip()

                    # 如果有多余前缀，去掉
                    if text.startswith("Prediction completed successfully"):
                        text = text[len("Prediction completed successfully"):].strip()

                    # 尝试解析 JSON
                    try:
                        parsed = json.loads(text)
                    except json.JSONDecodeError:
                        parsed = {"raw": text}

                    outputs.append(parsed)

                except Exception as e:
                    print(f"Purple Agent call failed for task {task.get('task_id')}: {e}")

            if not outputs:
                print(f"No valid outputs for task {task.get('task_id')}")
                continue

            last_output = outputs[-1]

            # ---------- 评分 ----------
            try:
                structural = self.evaluator.score_structural(task, last_output)
                semantic = self.evaluator.score_reasoning(task, last_output)
                consistency = self.evaluator.score_consistency(persona, outputs)
                explainability = self.evaluator.score_explainability(persona, last_output)
            except Exception as e:
                print(f"Scoring failed for task {task.get('task_id')}: {e}")
                continue

            structural_score = round(
                0.4 * structural.get("precision", 0.0)
                + 0.4 * structural.get("recall", 0.0)
                + 0.2 * structural.get("ndcg", 0.0),
                4
            )

            semantic_score = semantic.get("score", 0.0)
            final_score = round(
                max(0.0, min(1.0, 0.6 * semantic_score + 0.2 * consistency + 0.2 * explainability)),
                4
            )

            task_result = {
                "task_id": task.get("task_id", "task-unknown"),
                "instruction": task.get("instruction", ""),
                "output": last_output,
                
                "structural": {
                    "score": round(structural_score, 4),
                    "role": "diagnostic_only",
                    "note": "Heuristic reference metric, not used for scoring"
                },
                "semantic": round(semantic_score, 4),
                "consistency": round(consistency, 4),
                "explainability": round(explainability, 4),
                "final_score": final_score,
            }

            all_results.append(task_result)


        if not all_results:
            print(f"No results generated for persona {persona_name}")
            return

        persona_score = round(
            sum(r["final_score"] for r in all_results) / len(all_results),
            4
        )

        final_output = {
            "persona": persona_name,
            "persona_score": persona_score,
            "tasks": all_results,
        }

        # 总结 artifact
        if updater is not None:
            await updater.add_artifact(
                name="GreenAgentSummary",
                parts=[Part(root=DataPart(data=final_output))]
            )
        print("persona_score:", persona_score)


        
        os.makedirs("results", exist_ok=True)
        output_path = os.path.join("results", f"results_{persona_name}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(final_output, f, ensure_ascii=False, indent=2)

        print(f"Completed evaluation for persona {persona_name}, saved to {output_path}")

