"""Text input: normalize typed input."""
def normalize_text_input(raw: str) -> str:
    return (raw or "").strip()
