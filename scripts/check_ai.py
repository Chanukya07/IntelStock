#!/usr/bin/env python3
"""Verify the OpenRouter LLM path end to end.

The app degrades gracefully when the LLM is unreachable — sentiment falls back
to keyword scoring, chat returns a canned message — which is good for uptime but
means a broken key looks identical to a working one from the UI. This script
removes that ambiguity by making a real call and reporting exactly what happened.

    python scripts/check_ai.py
"""

from __future__ import annotations

import os
import sys

# python puts the *script's* directory on sys.path, not the cwd, so the repo
# root has to be added explicitly for "backend" to import.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def main() -> int:
    from backend.config import LLM_MODEL, OPENROUTER_API_BASE, OPENROUTER_API_KEY

    print("IntelStock — AI connectivity check")
    print("-" * 46)
    print(f"base   : {OPENROUTER_API_BASE}")
    print(f"model  : {LLM_MODEL}")

    if not OPENROUTER_API_KEY:
        print("key    : MISSING")
        print("\nFAIL: OPENROUTER_API_KEY is not set.")
        print("Put it in .env (gitignored) or export it, then re-run.")
        return 2

    print(f"key    : present ({OPENROUTER_API_KEY[:8]}…{OPENROUTER_API_KEY[-4:]})")
    print("\nCalling the model...")

    from openai import OpenAI

    try:
        client = OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_API_BASE)
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": "Reply with exactly: OK"}],
            max_tokens=10,
            temperature=0,
        )
    except Exception as exc:
        print(f"\nFAIL: {type(exc).__name__}: {exc}")
        hint = {
            "AuthenticationError": "The key was rejected — check it or generate a new one.",
            "NotFoundError": f"The model {LLM_MODEL!r} was not found. Set LLM_MODEL to a slug your key can reach.",
            "PermissionDeniedError": "The key is valid but not permitted to use this model.",
            "RateLimitError": "Rate limited or out of credit — check your OpenRouter balance.",
            "APIConnectionError": "Could not reach the host. Network/firewall/proxy is blocking it, not the key.",
        }.get(type(exc).__name__)
        if hint:
            print(f"Likely cause: {hint}")
        return 1

    reply = (response.choices[0].message.content or "").strip()
    print(f"\nPASS: model replied {reply!r}")

    usage = getattr(response, "usage", None)
    if usage:
        print(f"tokens: {usage.prompt_tokens} in / {usage.completion_tokens} out")
    print("\nThe AI path is working. Sentiment, insights and chat will use the model")
    print("rather than their offline fallbacks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
