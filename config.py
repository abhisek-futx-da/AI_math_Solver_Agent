import os
from dotenv import load_dotenv

load_dotenv()

def _get_secret(key: str, default: str = None):
    """Read from Streamlit secrets (Cloud) first, then env vars / .env."""
    try:
        import streamlit as st
        val = st.secrets.get(key)
        if val:
            return val
    except Exception:
        pass
    return os.getenv(key, default)

# OpenRouter (replaces Gemini for chat)
OPENROUTER_API_KEY = _get_secret("OPENROUTER_API_KEY")
OPENROUTER_MODEL = _get_secret("OPENROUTER_MODEL", "google/gemini-2.5-flash")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

RAG_TOP_K = 5
CHROMA_PERSIST_DIR = "chroma_data"
KNOWLEDGE_BASE_DIR = "knowledge_base"
