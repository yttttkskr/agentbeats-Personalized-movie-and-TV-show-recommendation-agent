# agentbeats/green/evaluator.py

import json
from typing import Dict, Any, List
from llm import deepseek_chat
from scoring_rules import precision_at_k, recall_at_k, ndcg_at_k
from sentence_transformers import SentenceTransformer
import numpy as np


class Evaluator:
    def __init__(self, eval_prompt_path: str, genre_descriptions: Dict[str, str] = None):
        with open(eval_prompt_path, "r", encoding="utf-8") as f:
            self.eval_prompt = f.read()

        # ====== For enhanced consistency scoring ======
        self.genre_descriptions = genre_descriptions or {
            "Action": "action, fight, war, mission, killer",
            "Thriller": "thrill, crime, murder, dark, detective",
            "Drama": "life, family, love, story",
            "Comedy": "fun, comedy, funny",
            "Romance": "love, romance, relationship"
        }
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        # precompute genre embeddings
        self.genre_embeddings = {
            genre: self.model.encode(desc, convert_to_numpy=True)
            for genre, desc in self.genre_descriptions.items()
        }

    # ==================================================
    # ① LLM Semantic Reasoning
    # ==================================================
    def score_reasoning(self, task: Dict[str, Any], output: Dict[str, Any]) -> Dict[str, Any]:
        prompt = (
            self.eval_prompt
            .replace("<<task>>", json.dumps(task, ensure_ascii=False))
            .replace("<<output>>", json.dumps(output, ensure_ascii=False))
        )

        raw = deepseek_chat(
            messages=[
                {"role": "system", "content": "You are a strict AI evaluator. Only output JSON {score, reason}"},
                {"role": "user", "content": prompt}
            ],
            model="deepseek-chat",
            temperature=0
        )

        try:
            obj = json.loads(raw)
            score = float(obj.get("score", 0))
            reason = obj.get("reason", "")
            score = max(0.0, min(1.0, score))
            return {"score": score, "reason": reason}
        except Exception:
            return {"score": 0.0, "reason": f"Parsing failed: {raw}"}

    # ==================================================
    # ② Behavioral Consistency
    # ==================================================
    def infer_genres(self, movie_name: str, threshold: float = 0.3) -> List[str]:
        """
        Use embedding similarity to infer movie genres.
        """
        movie_emb = self.model.encode(movie_name, convert_to_numpy=True)
        inferred = []
        for genre, emb in self.genre_embeddings.items():
            sim = np.dot(movie_emb, emb) / (np.linalg.norm(movie_emb) * np.linalg.norm(emb))
            if sim >= threshold:
                inferred.append(genre)
        return inferred

    def score_consistency(self, persona: Dict[str, Any], outputs: List[Dict[str, Any]]) -> float:
        prefs = set(persona.get("preferences", []))
        if not prefs or not outputs:
            return 0.0

        scores = []
        for out in outputs:
            preds = out.get("prediction", [])
            if not preds:
                scores.append(0.0)
                continue

            match_scores = []
            for m in preds:
                genres = set(self.infer_genres(str(m)))
                if not genres:
                    continue
                # multi-label intersection-over-union score
                score = len(genres & prefs) / len(genres | prefs)
                match_scores.append(score)

            scores.append(np.mean(match_scores) if match_scores else 0.0)

        return float(np.mean(scores)) if scores else 0.0

    # ==================================================
    # ③ Explainability
    # ==================================================
    def score_explainability(self, persona: Dict[str, Any], output: Dict[str, Any]) -> float:
        explanation = output.get("explanation", "")
        if not explanation:
            return 0.0

        prompt = f"""
Persona:
{json.dumps(persona, ensure_ascii=False)}

Explanation:
{explanation}

Rate from 0 to 1 whether the explanation:
- References key persona info
- Reasonably supports final decision
- Avoids empty templating
Only output a single number.
"""

        raw = deepseek_chat(
            messages=[
                {"role": "system", "content": "You are an explanation evaluator. Only output a number"},
                {"role": "user", "content": prompt}
            ],
            model="deepseek-chat",
            temperature=0
        )

        try:
            return max(0.0, min(1.0, float(raw.strip())))
        except Exception:
            return 0.0

    # ==================================================
    # ④ Structural metrics
    # ==================================================
    def score_structural(self, task: Dict[str, Any], output: Dict[str, Any]) -> Dict[str, float]:
        truth = []
        for x in task.get("ground_truth", []):
            if isinstance(x, dict):
                truth.append(x.get("title", ""))
            elif isinstance(x, str):
                truth.append(x)

        pred = output.get("prediction", [])
        if isinstance(pred, str):
            pred = [pred]

        if not truth or not pred:
            return {"precision": 0.0, "recall": 0.0, "ndcg": 0.0}

        return {
            "precision": precision_at_k(pred, truth, k=5),
            "recall": recall_at_k(pred, truth, k=5),
            "ndcg": ndcg_at_k(pred, truth, k=5)
        }
