"""FastAPI application entrypoint for IntelStock."""

import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.routes import router
from backend.api.advanced_routes import router as advanced_router
from backend.api.cron_routes import router as cron_router
from backend.database import init_db
from backend.tasks.scheduler import run_background_tasks
from backend.logging_config import setup_logging
from backend.middleware import LoggingMiddleware, ErrorHandlingMiddleware

setup_logging()
logger = logging.getLogger(__name__)
background_task = None


def _scheduler_enabled() -> bool:
    """Whether to run the in-process background scheduler.

    Enabled by default, which is correct on a persistent host. Set
    ENABLE_SCHEDULER=false when an external scheduler drives
    /api/v1/cron/* instead, so the jobs don't run twice — and on
    serverless hosts, where a long-lived asyncio loop cannot survive
    between invocations anyway.
    """
    return os.getenv("ENABLE_SCHEDULER", "true").strip().lower() not in {
        "false",
        "0",
        "no",
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    global background_task
    init_db()
    logger.info("Database initialized")

    if _scheduler_enabled():
        background_task = asyncio.create_task(run_background_tasks())
        logger.info("Background tasks started")
    else:
        logger.info(
            "In-process scheduler disabled (ENABLE_SCHEDULER=false); "
            "expecting an external scheduler to call /api/v1/cron/*"
        )

    yield

    if background_task:
        background_task.cancel()
        logger.info("Background tasks stopped")


app = FastAPI(title="IntelStock API", version="0.1.0", lifespan=lifespan)

# Add middleware
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(router)
app.include_router(advanced_router)
app.include_router(cron_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "db": "initialized"}
