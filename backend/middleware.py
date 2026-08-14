"""Middleware for IntelStock API."""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import logging

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging all requests and responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Log request and response details."""
        # Extract request info
        method = request.method
        path = request.url.path
        start_time = time.time()

        try:
            # Process request
            response = await call_next(request)
            process_time = time.time() - start_time

            # Log success
            logger.info(
                f"{method} {path} - {response.status_code} - {process_time:.3f}s"
            )

            # Add processing time header
            response.headers["X-Process-Time"] = str(process_time)
            return response

        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"{method} {path} - ERROR - {str(e)} - {process_time:.3f}s",
                exc_info=True,
            )
            raise


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for standardized error handling."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Handle errors and return standardized responses."""
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(f"Unhandled error: {str(e)}", exc_info=True)
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": "Internal server error"},
            )
