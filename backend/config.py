"""Configuration and environment setup for IntelStock."""

import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")
OPENROUTER_API_BASE = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")

# Warn at startup rather than crash at import — allows unit tests and
# degraded-mode runs where the LLM is not invoked.
if not OPENROUTER_API_KEY:
    import logging as _logging
    _logging.getLogger(__name__).warning(
        "OPENROUTER_API_KEY not set. LLM features will be unavailable. "
        "Set it in .env or environment variables."
    )
