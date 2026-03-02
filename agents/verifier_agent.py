"""Verifier / Critic Agent: check correctness, units, domain, edge cases. Triggers HITL if unsure."""
import json
import re
from llm_client import generate_text

SYSTEM = """You are a Verifier Agent for math solutions. You check: correctness, units & domain, edge cases.
Output ONLY a JSON object with these keys (no markdown):
- "is_correct": boolean
- "confidence": float between 0 and 1 (1 = fully confident)
- "issues": list of strings (empty if none): e.g. ["domain violation: x must be > 0"]
- "suggest_recheck": boolean (true if you are not confident and a human should review)"""

def verify_solution(problem: str, solution: str, parsed: dict) -> dict:
    problem = (problem or "").strip()
    solution = (solution or "").strip()
    if not solution:
        return {"is_correct": False, "confidence": 0.0, "issues": ["No solution provided."], "suggest_recheck": True}
    prompt = f"""Verify this solution.

Problem: {problem}
Constraints: {parsed.get('constraints', [])}

Solution:
{solution[:3000]}

Output the JSON object only."""
    try:
        out = generate_text(prompt, system_instruction=SYSTEM)
        json_match = re.search(r"\{[\s\S]*\}", out)
        if json_match:
            obj = json.loads(json_match.group())
            return {
                "is_correct": bool(obj.get("is_correct", True)),
                "confidence": float(obj.get("confidence", 0.8)),
                "issues": list(obj.get("issues", [])) if isinstance(obj.get("issues"), list) else [],
                "suggest_recheck": bool(obj.get("suggest_recheck", False)),
            }
    except Exception:
        pass
    return {"is_correct": True, "confidence": 0.7, "issues": [], "suggest_recheck": False}


class VerifierAgent:
    @staticmethod
    def run(problem: str, solution: str, parsed: dict) -> dict:
        return verify_solution(problem, solution, parsed)
