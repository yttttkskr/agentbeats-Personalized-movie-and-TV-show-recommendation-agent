# agentbeats/purple/purple_agent.py

import json
from typing import Dict, Any

from a2a.server.tasks import TaskUpdater
from a2a.types import Message, TaskState, Part, TextPart, DataPart
from a2a.utils import get_message_text, new_agent_text_message


class BaselinePurpleAgent:


    async def run(self, message: Message, updater: TaskUpdater) -> None:

        try:

            raw_text = get_message_text(message)
            task: Dict[str, Any] = json.loads(raw_text)
            
        except json.JSONDecodeError as e:

            await updater.reject(
                new_agent_text_message(f"Invalid JSON format: {e}")
            )
            return
        except Exception as e:

            await updater.reject(
                new_agent_text_message(f"Invalid input: {e}")
            )
            return


        task_input = task.get("input", {})
        

        candidates = task_input.get("candidate_items", [])
        
        if candidates:

            prediction = [str(x) for x in candidates[:5]]
            explanation = "Returned top-5 candidate items."
        else:

            prediction = []
            explanation = "No candidate items provided."


        await updater.add_artifact(
            name="prediction",
            parts=[
                Part(root=DataPart(data={
                    "prediction": prediction,
                    "explanation": explanation
                }))
            ],
        )


        await updater.update_status(
            TaskState.completed,
            new_agent_text_message("Prediction completed successfully")
        )