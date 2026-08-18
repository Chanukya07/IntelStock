"""Backend API endpoint configuration for the Streamlit frontend.

The API host must not be hardcoded: locally the backend is on loopback, on
Render it is loopback *inside the same container*, and in a split deployment
(Next.js on Vercel, API on Render) it is a public URL. Centralising it here
means a deployment change is one env var, not a code edit.

Set INTELSTOCK_API_BASE to the API root, without a trailing slash and
without the /api/v1 suffix, e.g.:
    INTELSTOCK_API_BASE=https://intelstock-api.onrender.com
"""

import os

# Root of the FastAPI app (no version prefix).
API_ROOT = os.getenv("INTELSTOCK_API_BASE", "http://127.0.0.1:8000").rstrip("/")

# Versioned prefix used by the advanced endpoints (alerts, analytics, reports).
API_BASE = f"{API_ROOT}/api/v1"

# Network timeouts (seconds). Report generation is slower than a plain read,
# and free-tier hosts cold-start, so these are deliberately generous.
REQUEST_TIMEOUT = int(os.getenv("INTELSTOCK_REQUEST_TIMEOUT", "15"))
REPORT_TIMEOUT = int(os.getenv("INTELSTOCK_REPORT_TIMEOUT", "60"))
