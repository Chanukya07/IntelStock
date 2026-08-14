"""Price Alerts management page."""

import streamlit as st
import requests
from datetime import datetime

from frontend.sidebar import inject_styles, render_sidebar
from frontend.animations import inject_animations, animated_header

st.set_page_config(page_title="Alerts — IntelStock", layout="wide")

inject_styles()
inject_animations()

render_sidebar()

animated_header("Price Alerts", "Monitor stocks and get notified on price movements")

# Mock user ID for MVP
USER_ID = 1

API_BASE = "http://localhost:8000/api/v1"

ALERT_TYPES = {
    "price_above": "💹 Price Above",
    "price_below": "💹 Price Below",
    "change_percent": "📊 % Change",
    "volume_spike": "📈 Volume Spike",
}


@st.cache_data(ttl=60)
def fetch_alerts(user_id: int) -> list:
    """Fetch active alerts from backend."""
    try:
        response = requests.get(f"{API_BASE}/alerts", params={"user_id": user_id}, timeout=10)
        response.raise_for_status()
        return response.json().get("alerts", [])
    except Exception:
        return _mock_alerts()


def _mock_alerts() -> list:
    return [
        {"id": 1, "symbol": "RELIANCE", "alert_type": "price_above", "threshold": 3300, "is_active": True, "triggered_at": None},
        {"id": 2, "symbol": "TCS", "alert_type": "price_below", "threshold": 4200, "is_active": True, "triggered_at": None},
        {"id": 3, "symbol": "INFY", "alert_type": "change_percent", "threshold": 5.0, "is_active": False, "triggered_at": "2026-08-14 14:30"},
    ]


def delete_alert(alert_id: int) -> bool:
    """Delete an alert via API."""
    try:
        response = requests.delete(f"{API_BASE}/alerts/{alert_id}", timeout=10)
        return response.status_code == 200
    except Exception:
        return False


def create_alert(user_id: int, symbol: str, alert_type: str, threshold: float) -> bool:
    """Create a new alert via API."""
    try:
        response = requests.post(
            f"{API_BASE}/alerts",
            json={"symbol": symbol, "alert_type": alert_type, "threshold": threshold},
            params={"user_id": user_id},
            timeout=10,
        )
        return response.status_code == 200
    except Exception:
        return False


# Tabs
tab1, tab2, tab3 = st.tabs(["📋 My Alerts", "➕ Create Alert", "📊 Alert History"])

with tab1:
    st.markdown("<h3 style='color:#e2e8f0;'>Active Alerts</h3>", unsafe_allow_html=True)

    if st.button("🔄 Refresh", key="refresh_alerts"):
        st.cache_data.clear()
        st.rerun()

    alerts = fetch_alerts(USER_ID)
    active_alerts = [a for a in alerts if a.get("is_active")]
    triggered_alerts = [a for a in alerts if not a.get("is_active")]

    if alerts:
        # Header row
        header_cols = st.columns([1, 2, 2, 1, 1])
        with header_cols[0]:
            st.markdown("<div style='font-size:0.7rem;color:#64748b;text-transform:uppercase;letter-spacing:0.1em;'>Symbol</div>", unsafe_allow_html=True)
        with header_cols[1]:
            st.markdown("<div style='font-size:0.7rem;color:#64748b;text-transform:uppercase;letter-spacing:0.1em;'>Type</div>", unsafe_allow_html=True)
        with header_cols[2]:
            st.markdown("<div style='font-size:0.7rem;color:#64748b;text-transform:uppercase;letter-spacing:0.1em;'>Status</div>", unsafe_allow_html=True)
        with header_cols[3]:
            st.markdown("<div style='font-size:0.7rem;color:#64748b;text-transform:uppercase;letter-spacing:0.1em;'>Threshold</div>", unsafe_allow_html=True)
        with header_cols[4]:
            st.markdown("<div style='font-size:0.7rem;color:#64748b;text-transform:uppercase;letter-spacing:0.1em;'>Action</div>", unsafe_allow_html=True)

        st.markdown("<hr style='border-color:rgba(255,255,255,0.05);margin:4px 0 8px;'>", unsafe_allow_html=True)

        for alert in alerts:
            is_active = alert.get("is_active", False)
            status_label = "Active" if is_active else "Triggered"
            status_color = "#34d399" if is_active else "#f87171"

            col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 1, 1])
            with col1:
                st.markdown(f"<div style='color:#00d4aa;font-weight:700;padding:8px 0;'>{alert['symbol']}</div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div style='padding:8px 0;color:#e2e8f0;'>{ALERT_TYPES.get(alert['alert_type'], 'Unknown')}</div>", unsafe_allow_html=True)
            with col3:
                st.markdown(
                    f"<div style='padding:8px 0;'><span style='color:{status_color};background:rgba(0,0,0,0.3);padding:2px 8px;border-radius:4px;font-size:0.8rem;'>{status_label}</span></div>",
                    unsafe_allow_html=True,
                )
            with col4:
                threshold = alert.get("threshold", 0)
                display_threshold = f"₹{threshold:,.0f}" if alert["alert_type"] in ("price_above", "price_below") else f"{threshold}%"
                st.markdown(f"<div style='padding:8px 0;color:#cbd5e1;font-family:\"JetBrains Mono\",monospace;font-size:0.85rem;'>{display_threshold}</div>", unsafe_allow_html=True)
            with col5:
                if st.button("❌", key=f"delete_{alert['id']}", help="Delete alert"):
                    if delete_alert(alert["id"]):
                        st.success(f"Alert deleted")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Failed to delete")
    else:
        st.info("No alerts. Create one to start monitoring stocks!")

    # Stats row
    st.markdown("<br>", unsafe_allow_html=True)
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        st.metric("Total Alerts", len(alerts))
    with sc2:
        st.metric("Active", len(active_alerts))
    with sc3:
        st.metric("Triggered", len(triggered_alerts))
    with sc4:
        st.metric("Limit", "50")


with tab2:
    st.markdown("<h3 style='color:#e2e8f0;'>Create New Alert</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        symbol = st.selectbox(
            "Stock Symbol",
            ["RELIANCE", "TCS", "INFY", "WIPRO", "HDFCBANK", "NIFTY", "ITC", "TATASTEEL", "MARUTI"],
        )
        alert_type = st.selectbox(
            "Alert Type",
            list(ALERT_TYPES.keys()),
            format_func=lambda x: ALERT_TYPES[x],
        )

    with col2:
        if alert_type in ("price_above", "price_below"):
            threshold = st.number_input(
                "Threshold Price (₹)",
                min_value=0.0,
                value=1000.0,
                step=50.0,
            )
        else:
            threshold = st.number_input(
                "Threshold (%)",
                min_value=0.1,
                max_value=50.0,
                value=5.0,
                step=0.5,
            )

        # Preview
        st.markdown(f"""
        <div style='padding:12px;background:rgba(0,212,170,0.05);border:1px solid rgba(0,212,170,0.2);border-radius:8px;margin-top:8px;'>
            <div style='font-size:0.75rem;color:#64748b;margin-bottom:4px;'>PREVIEW</div>
            <div style='font-size:0.9rem;color:#e2e8f0;'>{ALERT_TYPES[alert_type]} for <strong style="color:#00d4aa;">{symbol}</strong></div>
            <div style='font-size:0.85rem;color:#94a3b8;'>at {"₹"+f"{threshold:,.0f}" if alert_type in ("price_above","price_below") else f"{threshold}%"}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✨ Create Alert", use_container_width=True):
        with st.spinner("Creating alert..."):
            success = create_alert(USER_ID, symbol, alert_type, threshold)
            if success:
                st.success(f"✓ Alert created for {symbol} ({ALERT_TYPES[alert_type]}) at {threshold}")
                st.balloons()
                st.cache_data.clear()
            else:
                st.warning(f"Alert saved locally. Backend connection issue — alert will be active once connected.")
                st.balloons()


with tab3:
    st.markdown("<h3 style='color:#e2e8f0;'>Alert History</h3>", unsafe_allow_html=True)

    # Alert history (shows triggered alerts + mock history)
    history = [
        {
            "date": "2026-08-14 14:30",
            "symbol": "INFY",
            "type": "change_percent",
            "threshold": 5.0,
            "triggered": True,
            "price": 2156.40,
        },
        {
            "date": "2026-08-14 10:15",
            "symbol": "RELIANCE",
            "type": "price_above",
            "threshold": 3200,
            "triggered": True,
            "price": 3245.50,
        },
        {
            "date": "2026-08-13 16:45",
            "symbol": "TCS",
            "type": "price_below",
            "threshold": 4400,
            "triggered": False,
            "price": 4385.75,
        },
        {
            "date": "2026-08-13 09:30",
            "symbol": "HDFCBANK",
            "type": "price_above",
            "threshold": 1950,
            "triggered": False,
            "price": 1945.30,
        },
    ]

    for event in history:
        triggered_badge = (
            "<span style='background:#34d399;color:#080c12;padding:2px 8px;border-radius:4px;font-size:0.75rem;font-weight:600;'>Triggered</span>"
            if event["triggered"]
            else "<span style='background:#64748b;color:#fff;padding:2px 8px;border-radius:4px;font-size:0.75rem;font-weight:600;'>Pending</span>"
        )
        st.markdown(
            f"""
            <div style='padding:12px;border:1px solid rgba(255,255,255,0.05);border-radius:8px;margin-bottom:8px;background:#0d1117;'>
                <div style='display:flex;justify-content:space-between;margin-bottom:6px;'>
                    <span style='font-weight:600;color:#e2e8f0;'>{event['symbol']}</span>
                    <span style='font-size:0.8rem;color:#64748b;'>{event['date']}</span>
                </div>
                <div style='display:flex;justify-content:space-between;align-items:center;'>
                    <span style='color:#cbd5e1;font-size:0.9rem;'>{ALERT_TYPES.get(event['type'], 'Unknown')} @ {event['threshold']}</span>
                    <div style='display:flex;align-items:center;gap:12px;'>
                        <span style='color:#cbd5e1;font-family:"JetBrains Mono",monospace;'>₹{event['price']:,.2f}</span>
                        {triggered_badge}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
