"""Guardrail Agent: filter non-math or harmful inputs before processing."""
from llm_client import generate_text

SYSTEM = """You are a Guardrail Agent for a math mentor application.
Your job is to determine if the user's input is appropriate for processing.
Output ONLY a JSON object with exactly these keys (no markdown):
- "is_valid": boolean (true if the input is a math question; false if it is unrelated, harmful, or empty)
- "reason": string (brief reason if not valid; empty string if valid)

Valid inputs: math questions about algebra, probability, calculus, linear algebra, trigonometry, coordinate geometry, sequences/series (JEE level).
Invalid inputs: questions unrelated to math, harmful content, gibberish, empty input."""

import json
import re

def check_input(raw_input: str) -> dict:
    raw_input = (raw_input or "").strip()
    if not raw_input:
        return {"is_valid": False, "reason": "Input is empty."}
    # Short-circuit: if input is clearly math-like (numbers, operators, common words), pass it through
    math_keywords = [
        "find", "solve", "calculate", "evaluate", "differentiate", "integrate",
        "prove", "simplify", "expand", "factor", "limit", "derivative", "probability",
        "matrix", "determinant", "eigenvalue", "integral", "sum", "series",
        "triangle", "angle", "sin", "cos", "tan", "log", "equation", "inequality",
        "quadratic", "linear", "vector", "area", "volume", "distance", "root",
        "x", "y", "z", "n", "a", "b", "c", "+", "-", "*", "/", "^", "=",
    ]
    lower = raw_input.lower()
    if any(kw in lower for kw in math_keywords):
        return {"is_valid": True, "reason": ""}
    # For ambiguous inputs, ask the LLM
    prompt = f"""Is this input a math question suitable for a JEE-level math mentor?\nInput: {raw_input[:500]}\nOutput the JSON object only."""
    try:
        out = generate_text(prompt, system_instruction=SYSTEM)
        json_match = re.search(r"\{[\s\S]*\}", out)
        if json_match:
            obj = json.loads(json_match.group())
            return {
                "is_valid": bool(obj.get("is_valid", True)),
                "reason": str(obj.get("reason", "")),
            }
    except Exception:
        pass
    # Default: allow through (avoid false positives)
    return {"is_valid": True, "reason": ""}


class GuardrailAgent:
    @staticmethod
    def run(raw_input: str) -> dict:
        return check_input(raw_input)
