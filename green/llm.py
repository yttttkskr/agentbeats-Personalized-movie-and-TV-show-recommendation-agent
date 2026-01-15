# agentbeats/green/llm.py

import requests
import os

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"



def deepseek_chat(messages, model="deepseek-chat", temperature=0.3):

    if not DEEPSEEK_API_KEY:
        return "[DeepSeek Error: Missing API Key]"

    try:
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }

        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }

        resp = requests.post(DEEPSEEK_URL, headers=headers, json=payload)
        resp.raise_for_status()

        data = resp.json()
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"[DeepSeek Error]: {e}"