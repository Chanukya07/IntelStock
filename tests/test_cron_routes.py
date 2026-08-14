"""Tests for the externally-triggered cron endpoints.

These endpoints are publicly reachable URLs that mutate state, so the auth
behaviour is security-relevant and deliberately tested in all four states:
no secret configured, no credentials, wrong credentials, right credentials.
"""

import pytest
from fastapi.testclient import TestClient

CRON_SECRET = "unit-test-cron-secret"


@pytest.fixture(scope="module")
def client():
    from backend.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def _set_cron_secret(monkeypatch):
    monkeypatch.setenv("CRON_SECRET", CRON_SECRET)


def _auth(secret: str = CRON_SECRET) -> dict[str, str]:
    return {"Authorization": f"Bearer {secret}"}


def test_ping_needs_no_auth(client):
    """The keep-warm probe must work unauthenticated — an external scheduler
    uses it to wake a spun-down free-tier host before authenticating."""
    response = client.get("/api/v1/cron/ping")
    assert response.status_code == 200
    assert response.json() == {"status": "awake"}


def test_check_alerts_rejects_missing_credentials(client):
    response = client.post("/api/v1/cron/check-alerts")
    assert response.status_code == 401


def test_check_alerts_rejects_wrong_credentials(client):
    response = client.post("/api/v1/cron/check-alerts", headers=_auth("wrong-secret"))
    assert response.status_code == 401


def test_check_alerts_rejects_raw_secret_without_bearer_prefix(client):
    """A bare secret must not authenticate — the scheme is part of the check."""
    response = client.post(
        "/api/v1/cron/check-alerts", headers={"Authorization": CRON_SECRET}
    )
    assert response.status_code == 401


def test_check_alerts_accepts_valid_credentials(client):
    response = client.post("/api/v1/cron/check-alerts", headers=_auth())
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "job": "check-alerts"}


def test_refresh_rag_accepts_valid_credentials(client):
    response = client.post("/api/v1/cron/refresh-rag", headers=_auth())
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "job": "refresh-rag"}


def test_endpoints_fail_closed_when_secret_unset(client, monkeypatch):
    """An unset CRON_SECRET must never mean 'allow everyone'.

    This is the dangerous failure mode: deploying without configuring the
    secret should disable the endpoints, not expose them.
    """
    monkeypatch.delenv("CRON_SECRET", raising=False)

    for path in ("/api/v1/cron/check-alerts", "/api/v1/cron/refresh-rag"):
        # Even presenting the previously-valid secret must be refused.
        response = client.post(path, headers=_auth())
        assert response.status_code == 503, f"{path} should fail closed"


def test_scheduler_can_be_disabled_for_external_cron(monkeypatch):
    """ENABLE_SCHEDULER=false must stop the in-process loop, so jobs don't
    run twice when an external scheduler is also driving /api/v1/cron/*."""
    import backend.main as main

    monkeypatch.setenv("ENABLE_SCHEDULER", "false")
    assert main._scheduler_enabled() is False

    for value in ("False", "0", "no", "NO"):
        monkeypatch.setenv("ENABLE_SCHEDULER", value)
        assert main._scheduler_enabled() is False, f"{value!r} should disable"

    for value in ("true", "True", "1", "yes"):
        monkeypatch.setenv("ENABLE_SCHEDULER", value)
        assert main._scheduler_enabled() is True, f"{value!r} should enable"

    # Default (unset) must be enabled — correct for a persistent host.
    monkeypatch.delenv("ENABLE_SCHEDULER", raising=False)
    assert main._scheduler_enabled() is True


@pytest.mark.parametrize(
    "url,expected",
    [
        # Render/Heroku hand out postgres://, which SQLAlchemy 2.x rejects.
        ("postgres://u:p@host:5432/db", "postgresql+psycopg2://u:p@host:5432/db"),
        ("postgresql://u:p@host:5432/db", "postgresql+psycopg2://u:p@host:5432/db"),
        # Already explicit — must be left alone.
        (
            "postgresql+psycopg2://u:p@host:5432/db",
            "postgresql+psycopg2://u:p@host:5432/db",
        ),
        # SQLite must pass through untouched.
        ("sqlite:///./intelstock.db", "sqlite:///./intelstock.db"),
    ],
)
def test_database_url_normalization(url, expected):
    """The single most common reason a working SQLite app dies on its first
    managed-Postgres deploy."""
    from backend.database.session import _normalize_database_url

    assert _normalize_database_url(url) == expected
