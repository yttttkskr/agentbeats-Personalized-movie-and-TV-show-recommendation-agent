# agentbeats/green/scoring_rules.py

import math
from typing import List, Dict, Any

def precision_at_k(pred: Any, truth: List[str], k: int) -> float:
    if isinstance(pred, dict):
        pred = list(pred.keys())
    elif not isinstance(pred, list):
        pred = list(pred)
    pred_k = pred[:k]
    hits = sum([1 for x in pred_k if x in truth])
    return hits / k


def recall_at_k(pred: List[str], truth: List[str], k: int) -> float:
    if isinstance(pred, dict):
        pred = list(pred.keys())
    elif not isinstance(pred, list):
        pred = list(pred)
    pred_k = pred[:k]
    hits = sum([1 for x in pred_k if x in truth])
    if len(truth) == 0:
        return 0.0
    return hits / len(truth)


def ndcg_at_k(pred: List[str], truth: List[str], k: int) -> float:
    def dcg(items):
        s = 0
        for i, item in enumerate(items):
            if item in truth:
                s += 1 / math.log2(i + 2)
        return s
    if isinstance(pred, dict):
        pred = list(pred.keys())
    elif not isinstance(pred, list):
        pred = list(pred)
    dcg_val = dcg(pred[:k])
    ideal = sorted(truth, key=lambda x: 1, reverse=True)
    idcg_val = dcg(ideal[:k])
    if idcg_val == 0:
        return 0.0
    return dcg_val / idcg_val
