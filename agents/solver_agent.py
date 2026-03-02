"""Solver Agent: solve using RAG context + optional tools (calculator)."""
from llm_client import generate_text
from config import RAG_TOP_K

def solve_problem(parsed: dict, topic: str, rag_context: list) -> str:
    problem = parsed.get("problem_text", "")
    constraints = parsed.get("constraints", [])
    context_str = "\n\n".join([c.get("text", "") for c in rag_context]) if rag_context else "No retrieved context."
    prompt = f"""You are a math solver. Use the following reference material when relevant. Only use formulas and facts from the provided context; do not invent citations.

Reference material:
{context_str}

Problem: {problem}
Constraints: {constraints}

Solve the problem step by step. Give the final numerical or symbolic answer clearly at the end. If the problem has multiple parts, answer each part. Do not say "according to the context" unless you are actually quoting the context."""

    return generate_text(prompt)


class SolverAgent:
    def __init__(self, top_k: int = None):
        self.top_k = top_k or RAG_TOP_K

    def run(self, parsed: dict, topic: str) -> tuple[str, list[dict]]:
        query = f"{parsed.get('problem_text', '')} {topic}"
        try:
            from rag_pipeline import retrieve
            rag_context = retrieve(query, top_k=self.top_k)
        except Exception:
            rag_context = []
        solution = solve_problem(parsed, topic, rag_context)
        return solution, rag_context
