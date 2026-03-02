"""Parser Agent: raw input -> structured problem. Triggers HITL if needs_clarification."""
import json
import re
from llm_client import generate_text

SYSTEM = """You are a Parser Agent for a math mentor. Your job is to clean OCR/ASR output and convert the user's question into a structured format.
Output ONLY a single JSON object (no markdown, no explanation) with exactly these keys:
- "problem_text": string (cleaned, unambiguous problem statement)
- "topic": one of "algebra", "probability", "calculus", "linear_algebra"
- "variables": list of variable names mentioned (e.g. ["x", "n"])
- "constraints": list of constraints (e.g. ["x > 0", "n positive integer"])
- "needs_clarification": boolean (true only if information is missing or ambiguous and the problem cannot be solved without asking the user)
If the problem is clear enough to attempt, set needs_clarification to false."""

def parse_problem(raw_input: str) -> dict:
    raw_input = (raw_input or "").strip()
    if not raw_input:
        return {
            "problem_text": "",
            "topic": "algebra",
            "variables": [],
            "constraints": [],
            "needs_clarification": True,
        }
    prompt = f"""Clean and structure this math problem. Raw input:\n\n{raw_input}\n\nOutput the JSON object only."""
    try:
        out = generate_text(prompt, system_instruction=SYSTEM)
        # Extract JSON from response (in case of extra text)
        json_match = re.search(r"\{[\s\S]*\}", out)
        if json_match:
            obj = json.loads(json_match.group())
            return {
                "problem_text": obj.get("problem_text", raw_input),
                "topic": obj.get("topic", "algebra"),
                "variables": obj.get("variables", []),
                "constraints": obj.get("constraints", []),
                "needs_clarification": bool(obj.get("needs_clarification", False)),
            }
    except Exception:
        pass
    return {
        "problem_text": raw_input,
        "topic": "algebra",
        "variables": [],
        "constraints": [],
        "needs_clarification": False,
    }


class ParserAgent:
    @staticmethod
    def run(raw_input: str) -> dict:
        return parse_problem(raw_input)
