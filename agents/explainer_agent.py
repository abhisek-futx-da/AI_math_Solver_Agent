"""Explainer / Tutor Agent: step-by-step, student-friendly explanation."""
from llm_client import generate_text

SYSTEM = """You are a friendly math tutor. Explain solutions in a clear, step-by-step way suitable for a JEE-level student. Use simple language and highlight key formulas or ideas. Do not assume the student has already solved it—explain the reasoning."""

def explain_solution(problem: str, solution: str, parsed: dict) -> str:
    problem = (problem or "").strip()
    solution = (solution or "").strip()
    prompt = f"""Problem: {problem}

Solution (for reference): {solution[:2000]}

Write a clear, step-by-step explanation that a student can follow. Number the steps. Mention any formulas or concepts used."""
    return generate_text(prompt, system_instruction=SYSTEM)


class ExplainerAgent:
    @staticmethod
    def run(problem: str, solution: str, parsed: dict) -> str:
        return explain_solution(problem, solution, parsed)
