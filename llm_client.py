"""OpenRouter for chat + sentence-transformers for embeddings (single router key)."""
import base64
import os
from typing import List, Optional

from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL

# Lazy init for sentence-transformers (used only for embeddings)
_embedding_model = None


def _get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model


def generate_text(
    prompt: str,
    image_data=None,
    system_instruction: str = None,
    **kwargs,
) -> str:
    """Call OpenRouter chat completions. image_data: bytes or PIL Image (vision models)."""
    import requests
    key = OPENROUTER_API_KEY or os.getenv("OPENROUTER_API_KEY")
    if not key:
        return ""
    try:
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        if image_data is not None:
            if hasattr(image_data, "tobytes"):
                import io
                buf = io.BytesIO()
                image_data.save(buf, format="PNG")
                b64 = base64.b64encode(buf.getvalue()).decode()
            elif isinstance(image_data, bytes):
                b64 = base64.b64encode(image_data).decode()
            else:
                b64 = image_data
            content = [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                {"type": "text", "text": prompt},
            ]
            messages.append({"role": "user", "content": content})
        else:
            messages.append({"role": "user", "content": prompt})
        payload = {"model": OPENROUTER_MODEL, "messages": messages, "max_tokens": 4096}
        payload.update(kwargs)
        r = requests.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json=payload,
            timeout=60,
        )
        r.raise_for_status()
        data = r.json()
        text = (data.get("choices", [{}])[0].get("message", {}).get("content") or "").strip()
        return text
    except Exception:
        return ""


def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Embed using sentence-transformers (local, no API key)."""
    if not texts:
        return []
    model = _get_embedding_model()
    return model.encode(texts, convert_to_numpy=True).tolist()


def embed_single(text: str) -> List[float]:
    r = get_embeddings([text])
    return r[0] if r else []
