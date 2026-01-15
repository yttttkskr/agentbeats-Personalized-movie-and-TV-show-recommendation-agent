import os
import json
import asyncio
from typing import Dict, Any
import httpx
from evaluator import Evaluator
from messenger import Messenger
from task_generator import TaskGenerator


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

    def _load_personas(self, persona_dir: str) -> Dict[str, Any]:
        personas = {}
        if not os.path.exists(persona_dir):
            os.makedirs(persona_dir, exist_ok=True)
            return personas

        for file in os.listdir(persona_dir):
            if file.endswith(".json"):
                name = file.replace(".json", "")
                name_display = name.replace("_", " ").title()  
                with open(os.path.join(persona_dir, file), "r", encoding="utf-8") as f:
                    personas[name_display] = json.load(f)
        return personas

    async def auto_publish_persona_tasks(self, persona_name: str, purple_url: str):

        persona = self.personas.get(persona_name)
        if persona is None:
            print(f"⚠️ Persona {persona_name} 不存在")
            return

        if isinstance(persona, list):
            persona = persona[0]

        # 生成任务
        tasks = self.task_generator.generate_tasks(persona, task_count=3)
        all_results = []

        async with httpx.AsyncClient() as client:
            for task in tasks:
                task["user_history"] = persona.get("history", [])
                outputs = []

                for run_num in range(self.repeat_runs):
                    try:
                        print(f"\n第 {run_num + 1} 次调用 Purple Agent...")
                        reply = await self.messenger.talk_to_agent(
                            json.dumps(task, ensure_ascii=False),
                            purple_url
                        )

                        resp_text = reply.strip()
                        if resp_text.startswith("```json"):
                            resp_text = resp_text[len("```json"):].strip()
                        if resp_text.endswith("```"):
                            resp_text = resp_text[:-3].strip()
                        if resp_text.startswith("Prediction completed successfully"):
                            resp_text = resp_text.replace("Prediction completed successfully", "").strip()

                        try:
                            reply_data = json.loads(resp_text)
                        except json.JSONDecodeError:
                            reply_data = {"raw": resp_text}

                        outputs.append(reply_data)
                        print(f"原始回复: {reply}")
                        print(f"解析后数据: {reply_data}")

                    except Exception as e:
                        print(f"⚠️ 调用 Purple Agent 失败: {e}")

                if not outputs:
                    print(f"⚠️ Purple Agent 没有返回有效输出")
                    continue

                # 最后一次输出作为预测
                last_output = outputs[-1]
                if not isinstance(last_output, dict):
                    last_output = {"raw": str(last_output)}

                # 确保所有 outputs 都是 dict，用于一致性评分
                parsed_outputs = []
                for o in outputs:
                    if isinstance(o, str):
                        try:
                            parsed_outputs.append(json.loads(o))
                        except json.JSONDecodeError:
                            parsed_outputs.append({"raw": o})
                    else:
                        parsed_outputs.append(o)

                # 评分
                structural = self.evaluator.score_structural(task, last_output)
                semantic = self.evaluator.score_reasoning(task, last_output)
                consistency_score = self.evaluator.score_consistency(persona, parsed_outputs)
                explainability_score = self.evaluator.score_explainability(persona, last_output)

                semantic_score = semantic.get("score", 0.0)
                rule_score = structural.get("recall", 0.0)
                final_score = round(
                    max(0.0, min(1.0, 0.6 * semantic_score + 0.2 * consistency_score + 0.2 * explainability_score)),
                    4
                )

                all_results.append({
                    "task_id": task.get("task_id", "task-unknown"),
                    "task_instruction": task.get("instruction", ""),
                    "prediction": last_output,
                    "evaluation": {
                        "semantic": round(semantic_score, 4),
                        "structural": round(rule_score, 4),
                        "consistency": round(consistency_score, 4),
                        "explainability": round(explainability_score, 4),
                        "final_score": final_score
                    }
                })

                print(f"\n✅ 任务评分完成: task_id={task.get('task_id')}, final_score={final_score}")

        if not all_results:
            print("⚠️ 没有任务结果，跳过保存 JSON")
            return

        persona_score = round(sum(r["evaluation"]["final_score"] for r in all_results) / len(all_results), 4)

        final_output = {
            "persona": persona.get("name", persona_name),
            "tasks": all_results,
            "persona_score": persona_score
        }

        output_dir = "results"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"results_{persona_name.replace(' ', '_').lower()}.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(final_output, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 保存完成: {output_file}, persona_score={persona_score}")
