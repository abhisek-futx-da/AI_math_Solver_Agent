"""Memory layer: store interactions, retrieve similar for reuse. No model retraining."""
import json
import os
from pathlib import Path
from typing import Any, List
from llm_client import embed_single

MEMORY_DIR = Path("memory_data")
MEMORY_FILE = MEMORY_DIR / "interactions.jsonl"
MEMORY_EMBEDDINGS_FILE = MEMORY_DIR / "embeddings.json"


def _ensure_dir():
    MEMORY_DIR.mkdir(exist_ok=True)


def add_interaction(
    raw_input: str,
    parsed: dict,
    retrieved_context: list,
    solution: str,
    verifier_outcome: dict,
    feedback: str = None,
    user_comment: str = None,
):
    """Append one interaction to memory."""
    _ensure_dir()
    record = {
        "raw_input": raw_input[:2000],
        "parsed_problem": parsed.get("problem_text", "")[:1000],
        "topic": parsed.get("topic", ""),
        "retrieved_sources": [c.get("source") for c in retrieved_context],
        "solution_preview": (solution or "")[:500],
        "verifier_correct": verifier_outcome.get("is_correct"),
        "verifier_confidence": verifier_outcome.get("confidence"),
        "feedback": feedback,
        "user_comment": user_comment or "",
    }
    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    # Update embeddings cache for similarity search
    try:
        text_for_embed = f"{record['parsed_problem']} {record['topic']}"
        emb = embed_single(text_for_embed)
        _append_embedding(len(open(MEMORY_FILE, encoding="utf-8").readlines()) - 1, emb, record)
    except Exception:
        pass


def _append_embedding(idx: int, embedding: list, record: dict):
    _ensure_dir()
    data = {"index": idx, "embedding": embedding, "record": record}
    with open(MEMORY_EMBEDDINGS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps({"idx": idx, "record": record}) + "\n")
    # We don't store full embedding in JSONL for simplicity; we recompute on load for retrieve
    return


def _load_all_records() -> List[dict]:
    if not MEMORY_FILE.exists():
        return []
    records = []
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except Exception:
                continue
    return records


def memory_retrieve_similar(query: str, parsed: dict, top_k: int = 3) -> List[dict]:
    """
    Retrieve similar past solved problems for pattern reuse.
    Returns list of past records with solution_preview and feedback.
    """
    records = _load_all_records()
    if not records or not query:
        return []
    try:
        query_emb = embed_single(f"{parsed.get('problem_text', '')} {parsed.get('topic', '')}")
        # Simple similarity: embed each record and compare (could use numpy dot)
        import numpy as np
        record_embs = []
        for r in records:
            text = f"{r.get('parsed_problem', '')} {r.get('topic', '')}"
            record_embs.append(embed_single(text))
        query_arr = np.array(query_emb)
        scores = []
        for i, re in enumerate(record_embs):
            if len(re) != len(query_arr):
                continue
            sim = np.dot(query_arr, np.array(re)) / (np.linalg.norm(query_arr) * np.linalg.norm(re) + 1e-9)
            scores.append((i, float(sim)))
        scores.sort(key=lambda x: -x[1])
        out = []
        for i, _ in scores[:top_k]:
            out.append(records[i])
        return out
    except Exception:
        return records[:top_k]


def memory_store():
    """Return the path for storage (for UI)."""
    return MEMORY_DIR
