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
try:
    idx = mkt.fetch_index_values()
except Exception:  # page must still render with the network down
    idx = {}


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
quotes = []
for sym in watch_symbols:
    try:
        quotes.append(mkt.fetch_live_quote(sym))
    except Exception:  # a single bad symbol must not blank the page
        continue
# fetch_live_quote carries "name" on both the live and cached branches, so no
# local symbol->name table is needed.
watch = [
    {
        "Symbol": q["symbol"],
        "Name": q["name"],
        "Price": q["price"],
        "Change": f"{q['change_pct']:+.2f}%",
        "Volume": q["volume"],
        "Sentiment": q["sentiment"],
    }
    for q in quotes
]
if watch:
    st.dataframe(
        pd.DataFrame(watch),
        width="stretch",
        hide_index=True,
        column_config={
            "Change": st.column_config.TextColumn("Change"),
            "Volume": st.column_config.TextColumn("Volume"),
            "Sentiment": st.column_config.TextColumn("Sentiment"),
        },
    )
else:
    st.info("Quote data unavailable.")
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown(f"<div class='intel-card'><h3 style='color:#e2e8f0;margin-bottom:12px;'>Nifty 50 — Session Move</h3><div style='color:#64748b;font-size:0.75rem;margin-bottom:16px;'>Open to last print{st_live(n_st)}</div>", unsafe_allow_html=True)
# MarketDataService has no intraday history method, so the minute-by-minute series
# that used to live here was fabricated from n_val. The only two points actually
# sourced are the session open (last - change) and the latest print; the connecting
# line is drawn dashed because the real path between them is unknown.
if n_val:
    n_open = n_val - n_chg
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=["Open", "Last"], y=[n_open, n_val], mode="lines+markers+text",
        line=dict(color="#00d4aa", width=2, dash="dot"),
        marker=dict(color="#00d4aa", size=10),
        text=[f"{n_open:,.2f}", f"{n_val:,.2f}"], textposition="top center",
        textfont=dict(size=11, color="#e2e8f0"),
        hovertemplate="<b>%{x}</b><br>%{y:,.2f}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=280, margin=dict(l=0, r=0, t=24, b=0),
        xaxis=dict(showgrid=False, color="#64748b", tickfont=dict(size=10)),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)", color="#64748b", tickfont=dict(size=10)),
        showlegend=False, hovermode="x unified",
    )
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    st.markdown("<div style='color:#64748b;font-size:0.7rem;'>Indicative — tick-level intraday history is not available; only the open and last print are sourced.</div>", unsafe_allow_html=True)
else:
    st.info("Intraday series unavailable.")
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Breadth is counted over the symbols this page actually quoted — the old 2847/753/45
# NIFTY 500 reading was never measured anywhere in the codebase. Both halves of the
# card read from these three counters so they cannot drift apart.
adv = sum(1 for q in quotes if q["change_pct"] > 0)
dec = sum(1 for q in quotes if q["change_pct"] < 0)
unch = len(quotes) - adv - dec
breadth_st = "live" if quotes and all(q.get("status") == "live" for q in quotes) else "cached"
st.markdown(f"<div class='intel-card'><h3 style='color:#e2e8f0;margin-bottom:12px;'>Market Breadth</h3><div style='color:#64748b;font-size:0.75rem;margin-bottom:16px;'>Advancers vs decliners across tracked symbols{st_live(breadth_st)}</div>", unsafe_allow_html=True)
if quotes:
    bc1, bc2 = st.columns(2)
    with bc1:
        st.markdown(
            f"""
            <div style='display:flex;align-items:center;gap:12px;margin-bottom:12px;'><span style='width:12px;height:12px;border-radius:50%;background:#34d399;'></span><span style='color:#e2e8f0;font-size:0.85rem;'>Advancing: <span style='font-weight:700;color:#34d399;'>{adv}</span></span></div>
            <div style='display:flex;align-items:center;gap:12px;'><span style='width:12px;height:12px;border-radius:50%;background:#f87171;'></span><span style='color:#e2e8f0;font-size:0.85rem;'>Declining: <span style='font-weight:700;color:#f87171;'>{dec}</span></span></div>
            <div style='display:flex;align-items:center;gap:12px;margin-top:12px;'><span style='width:12px;height:12px;border-radius:50%;background:#64748b;'></span><span style='color:#e2e8f0;font-size:0.85rem;'>Unchanged: <span style='font-weight:700;color:#94a3b8;'>{unch}</span></span></div>
            <div style='font-size:0.7rem;color:#64748b;margin-top:8px;'>NSE · {len(quotes)} tracked symbols</div>
            """,
            unsafe_allow_html=True,
        )
    with bc2:
        fig_b = go.Figure(go.Pie(
            labels=["Advancing", "Declining", "Unchanged"], values=[adv, dec, unch],
            marker_colors=["#34d399", "#f87171", "#64748b"], hole=0.5,
            textinfo="percent", textfont=dict(size=11, color="#e2e8f0"),
        ))
        fig_b.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=220, margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
        st.plotly_chart(fig_b, width="stretch", config={"displayModeBar": False})
else:
    st.info("Breadth unavailable — no quotes could be loaded.")
st.markdown("</div>", unsafe_allow_html=True)
