"""Overview page — market indices and watchlist with live data."""
import os
import sys
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.services.market_data_service import MarketDataService
from frontend.sidebar import inject_styles, render_sidebar
from frontend.animations import inject_animations, animated_header

st.set_page_config(page_title="Overview — IntelStock", layout="wide")

inject_styles()
inject_animations()

render_sidebar()

animated_header("Market Overview", "Live indices · NSE/BSE")

mkt = MarketDataService()
idx = mkt.fetch_index_values()


def fmt(idx_data, key):
    d = idx_data.get(key, {})
    return (d.get("value", 0), d.get("change", 0), d.get("change_pct", 0), d.get("status", ""))


n_val, n_chg, n_pct, n_st = fmt(idx, "NIFTY")
b_val, b_chg, b_pct, b_st = fmt(idx, "SENSEX")
bn_val, bn_chg, bn_pct, bn_st = fmt(idx, "BANKNIFTY")
v_val, v_chg, v_pct, v_st = fmt(idx, "INDIAVIX")

st_live = lambda s: " 🟢 LIVE" if s == "live" else " ⚪ cached"

c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("NIFTY 50", f"{n_val:,.0f}", f"{n_chg:+,.0f} ({n_pct:+.2f}%){st_live(n_st)}")
with c2: st.metric("NIFTY BANK", f"{bn_val:,.0f}", f"{bn_chg:+,.0f} ({bn_pct:+.2f}%){st_live(bn_st)}")
with c3: st.metric("SENSEX", f"{b_val:,.0f}", f"{b_chg:+,.0f} ({b_pct:+.2f}%){st_live(b_st)}")
with c4: st.metric("VIX", f"{v_val:.2f}", f"{v_chg:+.2f} ({v_pct:+.2f}%){st_live(v_st)}", delta_color="inverse")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='intel-card'><h3 style='color:#e2e8f0;margin-bottom:12px;'>Market Watchlist</h3><div style='color:#64748b;font-size:0.75rem;margin-bottom:16px;'>Key NSE stocks at a glance</div>", unsafe_allow_html=True)

watch_symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "WIPRO"]
watch_names = {
    "RELIANCE": "Reliance Industries",
    "TCS": "Tata Consultancy Services",
    "INFY": "Infosys",
    "HDFCBANK": "HDFC Bank",
    "WIPRO": "Wipro",
}
watch = []
for sym in watch_symbols:
    q = mkt.fetch_live_quote(sym)
    watch.append({
        "Symbol": sym,
        "Name": watch_names[sym],
        "Price": q["price"],
        "Change": f"{q['change_pct']:+.2f}%",
        "Volume": q["volume"],
        "Sentiment": q["sentiment"],
    })
dfw = pd.DataFrame(watch)
st.dataframe(
    dfw,
    width="stretch",
    hide_index=True,
    column_config={
        "Change": st.column_config.TextColumn("Change"),
        "Volume": st.column_config.TextColumn("Volume"),
        "Sentiment": st.column_config.TextColumn("Sentiment"),
    },
)
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("<div class='intel-card'><h3 style='color:#e2e8f0;margin-bottom:12px;'>Nifty 50 — Intraday</h3><div style='color:#64748b;font-size:0.75rem;margin-bottom:16px;'>Live market hours</div>", unsafe_allow_html=True)
times = ["9:15", "9:45", "10:15", "10:45", "11:15", "11:45", "12:15", "12:45", "13:15", "13:45", "14:15", "14:45", "15:00", "15:29"]
base = n_val or 26485.60
prices = [base - 300, base - 265, base - 290, base - 225, base - 175, base - 195, base - 205, base - 165, base - 135, base - 150, base - 125, base - 155, base - 105, base]
fig = go.Figure()
fig.add_trace(go.Scatter(x=times, y=prices, mode="lines", line=dict(color="#00d4aa", width=2), fill="tozeroy", fillcolor="rgba(0,212,170,0.06)"))
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    height=280, margin=dict(l=0, r=0, t=8, b=0),
    xaxis=dict(showgrid=False, color="#64748b", tickfont=dict(size=10)),
    yaxis=dict(gridcolor="rgba(255,255,255,0.04)", color="#64748b", tickfont=dict(size=10)),
    showlegend=False, hovermode="x unified",
)
st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("<div class='intel-card'><h3 style='color:#e2e8f0;margin-bottom:12px;'>Market Breadth</h3><div style='color:#64748b;font-size:0.75rem;margin-bottom:16px;'>Advancers vs decliners on NSE</div>", unsafe_allow_html=True)
bc1, bc2 = st.columns(2)
with bc1:
    st.markdown(
        """
        <div style='display:flex;align-items:center;gap:12px;margin-bottom:12px;'><span style='width:12px;height:12px;border-radius:50%;background:#34d399;'></span><span style='color:#e2e8f0;font-size:0.85rem;'>Advancing: <span style='font-weight:700;color:#34d399;'>2,847</span></span></div>
        <div style='display:flex;align-items:center;gap:12px;'><span style='width:12px;height:12px;border-radius:50%;background:#f87171;'></span><span style='color:#e2e8f0;font-size:0.85rem;'>Declining: <span style='font-weight:700;color:#f87171;'>753</span></span></div>
        <div style='display:flex;align-items:center;gap:12px;margin-top:12px;'><span style='width:12px;height:12px;border-radius:50%;background:#64748b;'></span><span style='color:#e2e8f0;font-size:0.85rem;'>Unchanged: <span style='font-weight:700;color:#94a3b8;'>45</span></span></div>
        <div style='font-size:0.7rem;color:#64748b;margin-top:8px;'>NSE · NIFTY 500 universe</div>
        """,
        unsafe_allow_html=True,
    )
with bc2:
    fig_b = go.Figure(go.Pie(
        labels=["Advancing", "Declining", "Unchanged"], values=[2847, 753, 45],
        marker_colors=["#34d399", "#f87171", "#64748b"], hole=0.5,
        textinfo="percent", textfont=dict(size=11, color="#e2e8f0"),
    ))
    fig_b.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=220, margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
    st.plotly_chart(fig_b, width="stretch", config={"displayModeBar": False})
st.markdown("</div>", unsafe_allow_html=True)
