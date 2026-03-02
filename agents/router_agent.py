"""Intent Router Agent: classify problem type and route workflow."""
from llm_client import generate_text

SYSTEM = """You are an Intent Router for a math mentor. Given a structured math problem, respond with exactly one line: the topic.
Allowed topics: algebra, probability, calculus, linear_algebra.
No other text."""

def route_intent(parsed: dict) -> str:
    topic = (parsed.get("topic") or "").strip().lower()
    if topic in ("algebra", "probability", "calculus", "linear_algebra"):
        return topic
    problem_text = parsed.get("problem_text", "")
    if not problem_text:
        return "algebra"
    prompt = f"""Classify this math problem into exactly one topic. Problem: {problem_text[:500]}
Topic (one word from: algebra, probability, calculus, linear_algebra):"""
    try:
        out = generate_text(prompt, system_instruction=SYSTEM).strip().lower()
        for t in ("algebra", "probability", "calculus", "linear_algebra"):
            if t in out:
                return t
    except Exception:
        pass
    return "algebra"


class IntentRouterAgent:
    @staticmethod
    def run(parsed: dict) -> str:
        return route_intent(parsed)
