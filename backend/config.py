"""Configuration and environment setup for IntelStock."""
import os
from dotenv import load_dotenv

load_dotenv()

def _get_api_key() -> str:
    """Get API key from environment variable or Streamlit secrets."""
    key = os.getenv("OPENROUTER_API_KEY", "")
    if not key:
        try:
            import streamlit as st
            key = st.secrets.get("OPENROUTER_API_KEY", "")
        except Exception:
            pass
    return key

OPENROUTER_API_KEY = _get_api_key()
LLM_MODEL = os.getenv("LLM_MODEL", "meta-llama/llama-2-7b-chat")
OPENROUTER_API_BASE = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")


