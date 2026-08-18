"""Logging configuration for IntelStock."""

import logging
import logging.handlers
import os
from pathlib import Path


def _default_log_dir() -> str:
    # On Vercel the deployment bundle is read-only; /tmp is the only writable
    # path. Everywhere else, keep the repo-local logs/ directory.
    return "/tmp/logs" if os.getenv("VERCEL") else "logs"


def setup_logging() -> None:
    """Configure application-wide logging.

    File handlers are best-effort: on a read-only filesystem (serverless) the
    mkdir/open raises OSError, and logging must degrade to console-only rather
    than take the whole app down at import time — which is exactly what the
    previous module-scope ``LOG_DIR.mkdir()`` did.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Avoid stacking duplicate handlers when setup_logging() runs more than
    # once in a process (tests, serverless re-imports).
    if getattr(setup_logging, "_configured", False):
        return

    console_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    log_dir = Path(os.getenv("LOG_DIR", _default_log_dir()))
    try:
        log_dir.mkdir(parents=True, exist_ok=True)

        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
        )

        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / "intelstock.log",
            maxBytes=10_000_000,  # 10MB
            backupCount=5,
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        error_handler = logging.FileHandler(log_dir / "intelstock_errors.log")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        logger.addHandler(error_handler)
    except OSError as exc:
        logger.warning("File logging disabled (%s not writable): %s", log_dir, exc)

    # Suppress verbose third-party logs
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    setup_logging._configured = True
    logger.info("Logging configured successfully")


def get_logger(name: str) -> logging.Logger:
    """Get logger for a module."""
    return logging.getLogger(name)
