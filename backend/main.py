"""FastAPI application entrypoint for IntelStock."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.routes import router
from backend.api.advanced_routes import router as advanced_router
from backend.database import init_db
from backend.tasks.scheduler import run_background_tasks

logger = logging.getLogger(__name__)
background_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    global background_task
    init_db()
    logger.info("Database initialized")

    background_task = asyncio.create_task(run_background_tasks())
    logger.info("Background tasks started")
    yield

    if background_task:
        background_task.cancel()
    logger.info("Background tasks stopped")


app = FastAPI(title="IntelStock API", version="0.1.0", lifespan=lifespan)
app.include_router(router)
app.include_router(advanced_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "db": "initialized"}
