"""Price Alerts management page."""

import streamlit as st
from datetime import datetime

from frontend.sidebar import inject_styles, render_sidebar
from frontend.animations import inject_animations, animated_header, stat_badges

st.set_page_config(page_title="Alerts — IntelStock", layout="wide")

inject_styles()
inject_animations()

render_sidebar()

animated_header("Price Alerts", "Monitor stocks and get notified on price movements")

# Mock user ID for MVP
USER_ID = 1

# Alert types
ALERT_TYPES = {
    "price_above": "💹 Price Above",
    "price_below": "💹 Price Below",
    "change_percent": "📊 % Change",
    "volume_spike": "📈 Volume Spike",
}

# Tabs
tab1, tab2, tab3 = st.tabs(["📋 My Alerts", "➕ Create Alert", "📊 Alert History"])

with tab1:
    st.markdown("<h3 style='color:#e2e8f0;'>Active Alerts</h3>", unsafe_allow_html=True)

    # Mock active alerts
    alerts = [
        {
            "id": 1,
            "symbol": "RELIANCE",
            "type": "price_above",
            "threshold": 3300,
            "status": "Active",
        },
        {
            "id": 2,
            "symbol": "TCS",
            "type": "price_below",
            "threshold": 4200,
            "status": "Active",
        },
        {
            "id": 3,
            "symbol": "INFY",
            "type": "change_percent",
            "threshold": 5.0,
            "status": "Triggered",
        },
    ]

    if alerts:
        for alert in alerts:
            col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 1, 1])
            with col1:
                st.markdown(f"<div style='color:#00d4aa;font-weight:700;'>{alert['symbol']}</div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div>{ALERT_TYPES.get(alert['type'], 'Unknown')}</div>", unsafe_allow_html=True)
            with col3:
                status_color = "#34d399" if alert["status"] == "Active" else "#f87171"
                st.markdown(
                    f"<div style='color:{status_color};'>{alert['status']}</div>",
                    unsafe_allow_html=True,
                )
            with col4:
                st.markdown(f"<div>{alert['threshold']}</div>", unsafe_allow_html=True)
            with col5:
                if st.button("❌", key=f"delete_{alert['id']}", help="Delete alert"):
                    st.success(f"Alert {alert['id']} deleted")
                    st.rerun()
    else:
        st.info("No active alerts. Create one to get started!")

with tab2:
    st.markdown("<h3 style='color:#e2e8f0;'>Create New Alert</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        symbol = st.selectbox(
            "Select Stock",
            ["RELIANCE", "TCS", "INFY", "WIPRO", "HDFCBANK", "NIFTY"],
            label_visibility="collapsed",
        )
        alert_type = st.selectbox(
            "Alert Type",
            list(ALERT_TYPES.keys()),
            format_func=lambda x: ALERT_TYPES[x],
            label_visibility="collapsed",
        )

    with col2:
        threshold = st.number_input(
            "Threshold Value",
            min_value=0.0,
            value=100.0,
            step=10.0,
            label_visibility="collapsed",
        )

    if st.button("✨ Create Alert", use_container_width=True):
        st.success(
            f"✓ Alert created for {symbol} ({ALERT_TYPES[alert_type]}) at {threshold}"
        )
        st.balloons()

with tab3:
    st.markdown("<h3 style='color:#e2e8f0;'>Alert History</h3>", unsafe_allow_html=True)

    # Mock alert history
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
            "threshold": 3300,
            "triggered": True,
            "price": 3245.50,
        },
        {
            "date": "2026-08-13 16:45",
            "symbol": "TCS",
            "type": "price_below",
            "threshold": 4200,
            "triggered": False,
            "price": 4385.75,
        },
    ]

    for event in history:
        triggered_badge = (
            "<span style='background:#34d399;color:#080c12;padding:2px 8px;border-radius:4px;font-size:0.75rem;font-weight:600;'>Triggered</span>"
            if event["triggered"]
            else "<span style='background:#94a3b8;color:#fff;padding:2px 8px;border-radius:4px;font-size:0.75rem;font-weight:600;'>Pending</span>"
        )
        st.markdown(
            f"""
            <div style='padding:12px;border:1px solid rgba(255,255,255,0.05);border-radius:8px;margin-bottom:8px;'>
                <div style='display:flex;justify-content:space-between;margin-bottom:6px;'>
                    <span style='font-weight:600;color:#e2e8f0;'>{event['symbol']}</span>
                    <span style='font-size:0.8rem;color:#64748b;'>{event['date']}</span>
                </div>
                <div style='display:flex;justify-content:space-between;align-items:center;'>
                    <span style='color:#cbd5e1;font-size:0.9rem;'>{ALERT_TYPES.get(event['type'], 'Unknown')} @ {event['threshold']}</span>
                    <span style='color:#cbd5e1;'>₹{event['price']:,.2f}</span>
                    {triggered_badge}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Summary stats
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<h4 style='color:#e2e8f0;margin-bottom:12px;'>Alert Summary</h4>", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Alerts", 3)
with col2:
    st.metric("Active", 2)
with col3:
    st.metric("Triggered", 1)
with col4:
    st.metric("Limit", "50")
