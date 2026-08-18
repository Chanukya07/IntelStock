#!/usr/bin/env bash
# Start both IntelStock processes inside a single Render web service.
#
#   FastAPI   -> 127.0.0.1:$BACKEND_PORT  (loopback only, not publicly routable)
#   Streamlit -> 0.0.0.0:$PORT            (the port Render exposes)
#
# Render sets $PORT. Everything else falls back to sane local defaults so this
# script also works for `./start.sh` on a laptop.

set -euo pipefail

BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${PORT:-8501}"

echo "[start] launching FastAPI on 127.0.0.1:${BACKEND_PORT}"
uvicorn backend.main:app \
  --host 127.0.0.1 \
  --port "${BACKEND_PORT}" \
  --log-level "${UVICORN_LOG_LEVEL:-info}" &
BACKEND_PID=$!

# If the backend dies, take the whole container down so Render restarts it,
# rather than serving a UI whose API is silently gone.
trap 'echo "[start] shutting down backend ${BACKEND_PID}"; kill "${BACKEND_PID}" 2>/dev/null || true' EXIT INT TERM

echo "[start] waiting for backend to become healthy..."
for _ in $(seq 1 45); do
  if curl -sf "http://127.0.0.1:${BACKEND_PORT}/health" >/dev/null 2>&1; then
    echo "[start] backend is healthy"
    break
  fi
  if ! kill -0 "${BACKEND_PID}" 2>/dev/null; then
    echo "[start] FATAL: backend exited during startup" >&2
    exit 1
  fi
  sleep 1
done

echo "[start] launching Streamlit on 0.0.0.0:${FRONTEND_PORT}"
exec streamlit run frontend/dashboard.py \
  --server.port "${FRONTEND_PORT}" \
  --server.address 0.0.0.0 \
  --server.headless true \
  --server.enableCORS false \
  --server.enableXsrfProtection true \
  --browser.gatherUsageStats false
