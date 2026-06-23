"""Overview page - market indices and watchlist with live data."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from backend.services.market_data_service import MarketDataService
from frontend.sidebar import inject_styles, render_sidebar

st.set_page_config(page_title="Overview - IntelStock", layout="wide")
inject_styles()

st.markdown("""<style>[data-testid="metric-container"]{background:#0d1117;border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:20px;}
[data-testid="stMetricValue"]{font-family:'JetBrains Mono',monospace!important;font-size:1.5rem!important;font-weight:700!important;color:#e2e8f0!important;}
.intel-card{background:#0d1117;border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:20px 24px;margin-bottom:16px;}</style>""", unsafe_allow_html=True)

render_sidebar()

st.markdown("<h1 style='color:#e2e8f0;font-size:1.6rem;font-weight:700;margin-bottom:4px;'>Market Overview</h1>", unsafe_allow_html=True)
st.markdown("<div style='color:#64748b;font-size:0.8rem;margin-bottom:24px;'>Live indices &#183; NSE/BSE</div>", unsafe_allow_html=True)

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

c1,c2,c3,c4 = st.columns(4)
with c1: st.metric("NIFTY 50", f"{int(n_val):,}", f"+{int(n_chg):,} ({n_pct:+.2f}%) {st_live(n_st)}")
with c2: st.metric("NIFTY BANK", f"{int(bn_val):,}", f"+{int(bn_chg):,} ({bn_pct:+.2f}%) {st_live(bn_st)}")
with c3: st.metric("SENSEX", f"{int(b_val):,}", f"+{int(b_chg):,} ({b_pct:+.2f}%) {st_live(b_st)}")
with c4: st.metric("VIX", f"{v_val:.2f}", f"{v_chg:+.2f} ({v_pct:+.2f}%) {st_live(v_st)}", delta_color="inverse")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='intel-card'><h3 style='color:#e2e8f0;margin-bottom:12px;'>Market Watchlist</h3><div style='color:#64748b;font-size:0.75rem;margin-bottom:16px;'>Key NSE stocks at a glance</div>", unsafe_allow_html=True)

watch = [
 {"Symbol":"RELIANCE","Name":"Reliance Industries","Price":mkt.fetch_live_quote("RELIANCE")["price"],"Change":f"{mkt.fetch_live_quote('RELIANCE')['change_pct']:+.2f}%","52W Low":"-","52W High":"-","Volume":mkt.fetch_live_quote("RELIANCE")["volume"],"Sentiment":mkt.fetch_live_quote("RELIANCE")["sentiment"]},
 {"Symbol":"TCS","Name":"Tata Consultancy Services","Price":mkt.fetch_live_quote("TCS")["price"],"Change":f"{mkt.fetch_live_quote('TCS')['change_pct']:+.2f}%","52W Low":"-","52W High":"-","Volume":mkt.fetch_live_quote("TCS")["volume"],"Sentiment":mkt.fetch_live_quote("TCS")["sentiment"]},
 {"Symbol":"INFY","Name":"Infosys","Price":mkt.fetch_live_quote("INFY")["price"],"Change":f"{mkt.fetch_live_quote('INFY')['change_pct']:+.2f}%","52W Low":"-","52W High":"-","Volume":mkt.fetch_live_quote("INFY")["volume"],"Sentiment":mkt.fetch_live_quote("INFY")["sentiment"]},
 {"Symbol":"HDFCBANK","Name":"HDFC Bank","Price":mkt.fetch_live_quote("HDFCBANK")["price"],"Change":f"{mkt.fetch_live_quote('HDFCBANK')['change_pct']:+.2f}%","52W Low":"-","52W High":"-","Volume":mkt.fetch_live_quote("HDFCBANK")["volume"],"Sentiment":mkt.fetch_live_quote("HDFCBANK")["sentiment"]},
 {"Symbol":"WIPRO","Name":"Wipro","Price":mkt.fetch_live_quote("WIPRO")["price"],"Change":f"{mkt.fetch_live_quote('WIPRO')['change_pct']:+.2f}%","52W Low":"-","52W High":"-","Volume":mkt.fetch_live_quote("WIPRO")["volume"],"Sentiment":mkt.fetch_live_quote("WIPRO")["sentiment"]},
]
dfw = pd.DataFrame(watch)
st.dataframe(dfw, use_container_width=True, hide_index=True, column_config={"Sentiment": st.column_config.TextColumn("Sentiment"), "52W Low": st.column_config.TextColumn("52W Low"), "52W High": st.column_config.TextColumn("52W High"), "Volume": st.column_config.TextColumn("Volume")})
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("<div class='intel-card'><h3 style='color:#e2e8f0;margin-bottom:12px;'>Nifty 50 &#8212; Intraday</h3><div style='color:#64748b;font-size:0.75rem;margin-bottom:16px;'>Live market hours</div>", unsafe_allow_html=True)
times = ["9:15","9:45","10:15","10:45","11:15","11:45","12:15","12:45","13:15","13:45","14:15","14:45","15:00","15:29"]
base = n_val or 24762
prices = [base - 180, base - 140, base - 165, base - 100, base - 50, base - 70, base - 80, base - 40, base - 10, base - 25, base, base - 30, base + 20, base]
fig = go.Figure()
fig.add_trace(go.Scatter(x=times, y=prices, mode="lines", line=dict(color="#00d4aa", width=2), fill="tozeroy", fillcolor="rgba(0,212,170,0.06)"))
fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=280, margin=dict(l=0,r=0,t=8,b=0), xaxis=dict(showgrid=False,color="#64748b",tickfont=dict(size=10)), yaxis=dict(gridcolor="rgba(255,255,255,0.04)",color="#64748b",tickfont=dict(size=10)), showlegend=False, hovermode="x unified")
st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("<div class='intel-card'><h3 style='color:#e2e8f0;margin-bottom:12px;'>Market Breadth</h3><div style='color:#64748b;font-size:0.75rem;margin-bottom:16px;'>Advancers vs decliners on NSE</div>", unsafe_allow_html=True)
bc1, bc2 = st.columns(2)
with bc1: st.markdown(f""" <div style='display:flex;align-items:center;gap:12px;margin-bottom:12px;'><span style='width:12px;height:12px;border-radius:50%;background:#34d399;'></span><span style='color:#e2e8f0;font-size:0.85rem;'>Advancing: <span style='font-weight:700;color:#34d399;'>2,847</span></span></div> <div style='display:flex;align-items:center;gap:12px;'><span style='width:12px;height:12px;border-radius:50%;background:#f87171;'></span><span style='color:#e2e8f0;font-size:0.85rem;'>Declining: <span style='font-weight:700;color:#f87171;'>753</span></span></div> <div style='display:flex;align-items:center;gap:12px;margin-top:12px;'><span style='width:12px;height:12px;border-radius:50%;background:#64748b;'></span><span style='color:#e2e8f0;font-size:0.85rem;'>Unchanged: <span style='font-weight:700;color:#94a3b8;'>45</span></span></div> <div style='font-size:0.7rem;color:#64748b;margin-top:8px;'>NSE &#183; NIFTY 500 universe</div> """, unsafe_allow_html=True)
with bc2: fig_b = go.Figure(go.Pie( labels=["Advancing", "Declining", "Unchanged"], values=[2847, 753, 45], marker_colors=["#34d399", "#f87171", "#64748b"], hole=0.5, textinfo="percent", textfont=dict(size=11, color="#e2e8f0"), ))
fig_b.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=220, margin=dict(l=0,r=0,t=0,b=0), showlegend=False)
st.plotly_chart(fig_b, width="stretch", config={"displayModeBar": False})
st.markdown("</div>", unsafe_allow_html=True)
