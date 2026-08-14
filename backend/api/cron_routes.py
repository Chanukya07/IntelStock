"""Externally-triggered scheduled job endpoints.

Scheduling is deliberately decoupled from hosting. These are plain
authenticated HTTP endpoints, so *any* external scheduler can drive them:
GitHub Actions, Render Cron, Vercel Cron, cron-job.org, or a laptop crontab.

Why this matters here:
  - On a persistent host (Render), backend/tasks/scheduler.py already runs
    these tasks on an in-process loop. But Render's free tier spins the
    service down after ~15 minutes of inactivity, which stops that loop.
    An external ping both wakes the service and runs the checks.
  - On a serverless host (Vercel), no in-process loop can exist at all, so
    external triggering is the only option. Vercel's Hobby cron is capped at
    once per day, which is useless for price alerts — hence GitHub Actions.

Keeping this host-agnostic means changing hosts later does not mean
rewriting the scheduler.
"""

from __future__ import annotations

import logging
import os
import secrets

from fastapi import APIRouter, Header, HTTPException, status

from backend.tasks.scheduler import check_price_alerts, refresh_rag_index

router = APIRouter(prefix="/api/v1/cron", tags=["cron"])
logger = logging.getLogger(__name__)


def _verify_cron_auth(authorization: str | None) -> None:
    """Authenticate an external scheduler.

    These endpoints are publicly reachable URLs that mutate state, so they
    must not be callable by anyone who guesses the path.
    """
    expected_secret = os.getenv("CRON_SECRET", "")

    if not expected_secret:
        # Fail closed. An unset secret must never mean "allow everyone".
        logger.error("CRON_SECRET is not configured; refusing cron request")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cron endpoints are not configured on this deployment.",
        )

    if not authorization or not secrets.compare_digest(
        authorization, f"Bearer {expected_secret}"
    ):
        logger.warning("Rejected cron request with invalid credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing cron credentials.",
        )


@router.post("/check-alerts")
async def cron_check_alerts(
    authorization: str | None = Header(default=None),
) -> dict[str, object]:
    """Evaluate every active price alert against current quotes."""
    _verify_cron_auth(authorization)

    logger.info("Cron: running price alert check")
    try:
        await check_price_alerts()
    except Exception as exc:  # noqa: BLE001 - report failure to the scheduler
        logger.exception("Cron alert check failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Alert check failed: {exc}",
        ) from exc

    return {"status": "ok", "job": "check-alerts"}


@router.post("/refresh-rag")
async def cron_refresh_rag(
    authorization: str | None = Header(default=None),
) -> dict[str, object]:
    """Re-index the latest news headlines into the vector store."""
    _verify_cron_auth(authorization)

    logger.info("Cron: refreshing RAG index")
    try:
        await refresh_rag_index()
    except Exception as exc:  # noqa: BLE001 - report failure to the scheduler
        logger.exception("Cron RAG refresh failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG refresh failed: {exc}",
        ) from exc

    return {"status": "ok", "job": "refresh-rag"}


@router.get("/ping")
def cron_ping() -> dict[str, str]:
    """Unauthenticated keep-warm probe.

    Deliberately does no work and touches no state, so it is safe to expose:
    it exists purely so an external scheduler can prevent a free-tier host
    from spinning the service down. Real work lives behind the authenticated
    POST endpoints above.
    """
    return {"status": "awake"}
