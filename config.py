import os
from dotenv import load_dotenv

load_dotenv()

# OpenRouter (replaces Gemini for chat)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

RAG_TOP_K = 5
CHROMA_PERSIST_DIR = "chroma_data"
KNOWLEDGE_BASE_DIR = "knowledge_base"
