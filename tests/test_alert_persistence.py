"""Regression tests: price alerts must outlive the process that created them.

Alerts used to live in a process-local dict, so a restart silently deleted
them and a second worker could not see them at all. These tests exercise the
DB-backed service through separate service instances and separate sessions,
which is what a restart / second worker actually looks like.
"""

import os
import tempfile

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database.models import Base
from backend.services.alert_service import AlertService, AlertType


@pytest.fixture()
def session_factory():
    """A private on-disk SQLite DB so these tests never touch the shared one."""
    db_path = os.path.join(tempfile.mkdtemp(prefix="alert-persistence-"), "alerts.db")
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    try:
        yield factory
    finally:
        engine.dispose()


def test_alert_survives_a_fresh_service_instance(session_factory):
    session = session_factory()
    try:
        created = AlertService(session).create_alert(
            user_id=11, symbol="RELIANCE", alert_type=AlertType.PRICE_ABOVE, threshold=3500.0
        )

        # A new AlertService is what the process gets after a restart.
        reloaded = AlertService(session).get_user_alerts(11)
    finally:
        session.close()

    assert [a.id for a in reloaded] == [created.id]
    assert reloaded[0].symbol == "RELIANCE"
    assert reloaded[0].alert_type == AlertType.PRICE_ABOVE
    assert reloaded[0].threshold == 3500.0
    assert reloaded[0].is_active is True
    assert reloaded[0].created_at


def test_alert_is_visible_from_another_session(session_factory):
    """A second worker process sees alerts it did not create."""
    writer = session_factory()
    try:
        created = AlertService(writer).create_alert(
            user_id=12, symbol="TCS", alert_type=AlertType.PRICE_BELOW, threshold=4000.0
        )
    finally:
        writer.close()

    reader = session_factory()
    try:
        alerts = AlertService(reader).get_user_alerts(12)
    finally:
        reader.close()

    assert [a.id for a in alerts] == [created.id]


def test_triggered_state_persists_and_never_refires(session_factory):
    writer = session_factory()
    try:
        created = AlertService(writer).create_alert(
            user_id=13, symbol="INFY", alert_type=AlertType.PRICE_ABOVE, threshold=1500.0
        )
        triggered = AlertService(writer).check_alerts(
            symbol="INFY", current_price=1600.0, change_pct=2.0, volume="4.2M"
        )
        assert [a.id for a in triggered] == [created.id]
    finally:
        writer.close()

    reader = session_factory()
    try:
        service = AlertService(reader)
        stored = service.get_user_alerts(13)[0]
        assert stored.is_active is False
        assert stored.triggered_at is not None
        assert stored.triggered_price == 1600.0

        # A restarted process must not re-trigger an already-triggered alert.
        assert service.check_alerts(symbol="INFY", current_price=1700.0, change_pct=3.0, volume="4.2M") == []
    finally:
        reader.close()


def test_deleted_alert_stays_deleted(session_factory):
    writer = session_factory()
    try:
        created = AlertService(writer).create_alert(
            user_id=14, symbol="WIPRO", alert_type=AlertType.PRICE_ABOVE, threshold=500.0
        )
        assert AlertService(writer).delete_alert(created.id) is True
    finally:
        writer.close()

    reader = session_factory()
    try:
        assert AlertService(reader).get_user_alerts(14) == []
    finally:
        reader.close()


def test_delete_scoped_to_owner(session_factory):
    session = session_factory()
    try:
        service = AlertService(session)
        created = service.create_alert(
            user_id=15, symbol="ITC", alert_type=AlertType.PRICE_ABOVE, threshold=450.0
        )

        # Another user must not be able to delete it.
        assert service.delete_alert(created.id, user_id=16) is False
        assert [a.id for a in service.get_user_alerts(15)] == [created.id]

        assert service.delete_alert(created.id, user_id=15) is True
        assert service.get_user_alerts(15) == []
    finally:
        session.close()


def test_active_symbols_cover_untracked_tickers(session_factory):
    """The scheduler can discover symbols outside its hardcoded tuple."""
    session = session_factory()
    try:
        service = AlertService(session)
        service.create_alert(user_id=17, symbol="MARUTI", alert_type=AlertType.PRICE_ABOVE, threshold=11000.0)
        service.create_alert(user_id=17, symbol="TATASTEEL", alert_type=AlertType.PRICE_BELOW, threshold=120.0)

        assert sorted(service.get_active_symbols()) == ["MARUTI", "TATASTEEL"]
    finally:
        session.close()
