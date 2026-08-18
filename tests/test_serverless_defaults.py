"""Serverless (Vercel) runtime defaults.

Vercel injects VERCEL=1 and mounts the deployment bundle read-only, with /tmp
as the only writable path and no long-lived process between invocations. Each
of these defaults exists because its non-serverless counterpart crashes or
misbehaves there; the tests pin the platform detection so a refactor cannot
silently regress the deploy.
"""

import logging

import pytest


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    for var in ("VERCEL", "ENABLE_SCHEDULER", "RAG_VECTORSTORE_PATH", "LOG_DIR"):
        monkeypatch.delenv(var, raising=False)


def test_scheduler_defaults_off_on_vercel(monkeypatch):
    """Frozen serverless instances cannot host a while-True asyncio loop, so
    the in-process scheduler must not start there unless explicitly forced."""
    from backend.main import _scheduler_enabled

    assert _scheduler_enabled() is True  # persistent-host default

    monkeypatch.setenv("VERCEL", "1")
    assert _scheduler_enabled() is False

    # An explicit setting must still win in both directions.
    monkeypatch.setenv("ENABLE_SCHEDULER", "true")
    assert _scheduler_enabled() is True
    monkeypatch.setenv("ENABLE_SCHEDULER", "false")
    assert _scheduler_enabled() is False


def test_sqlite_default_moves_to_tmp_on_vercel(monkeypatch):
    """./intelstock.db sits inside the read-only bundle on Vercel; the default
    must relocate to /tmp so an unconfigured deploy boots instead of crashing
    in init_db()."""
    from backend.database.session import _default_database_url

    assert _default_database_url() == "sqlite:///./intelstock.db"

    monkeypatch.setenv("VERCEL", "1")
    assert _default_database_url() == "sqlite:////tmp/intelstock.db"


def test_vectorstore_path_resolution(monkeypatch):
    from backend.rag.vectorstore import _default_store_path

    assert _default_store_path() == "vectorstore"

    monkeypatch.setenv("VERCEL", "1")
    assert _default_store_path() == "/tmp/vectorstore"

    # Explicit override beats platform detection.
    monkeypatch.setenv("RAG_VECTORSTORE_PATH", "/tmp/custom-store")
    assert _default_store_path() == "/tmp/custom-store"


def test_logging_degrades_to_console_on_unwritable_dir(monkeypatch):
    """The old module-scope LOG_DIR.mkdir() crashed the entire app at import
    time on a read-only filesystem. File logging must now fail soft."""
    from backend import logging_config

    monkeypatch.setenv("LOG_DIR", "/proc/definitely-not-writable/logs")
    monkeypatch.setattr(logging_config.setup_logging, "_configured", False, raising=False)

    root = logging.getLogger()
    before = list(root.handlers)
    try:
        logging_config.setup_logging()  # must not raise
        added = [h for h in root.handlers if h not in before]
        assert added, "console handler should still be installed"
        assert not any(isinstance(h, logging.FileHandler) for h in added), (
            "no file handler should exist when the log dir is unwritable"
        )
    finally:
        for h in root.handlers[:]:
            if h not in before:
                root.removeHandler(h)
        logging_config.setup_logging._configured = False
