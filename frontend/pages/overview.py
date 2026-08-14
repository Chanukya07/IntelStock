"""Overview page — market indices and watchlist."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from frontend.sidebar import inject_styles, render_sidebar
from frontend.animations import inject_animations, animated_header

st.set_page_config(page_title="Overview — IntelStock", layout="wide")

inject_styles()
inject_animations()

st.markdown("""
<style>
[data-testid="metric-container"]{background:#0d1117;border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:20px;}
[data-testid="stMetricValue"]{font-family:'JetBrains Mono',monospace!important;font-size:1.5rem!important;font-weight:700!important;color:#e2e8f0!important;}
.intel-card{background:#0d1117;border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:20px 24px;margin-bottom:16px;}
</style>
""", unsafe_allow_html=True)

render_sidebar()

animated_header("Market Overview", "Live indices · NSE/BSE · August 2026")

# KPIs — August 2026 levels
c1,c2,c3,c4 = st.columns(4)
with c1: st.metric("NIFTY 50","26,485","+328 (+1.25%)")
with c2: st.metric("NIFTY BANK","57,120","+0.74%")
with c3: st.metric("SENSEX","86,940","+1,050 (+1.22%)")
with c4: st.metric("VIX","12.8","-0.6%",delta_color="inverse")

st.markdown("<br>", unsafe_allow_html=True)

# Watchlist table — current August 2026 prices
watchlist = [
    {"Symbol":"RELIANCE","Name":"Reliance Industries","Price":"₹3,245","Change":"+2.4%","52W Low":"₹2,480","52W High":"₹3,320","Volume":"4.2M","Sentiment":"Bullish"},
    {"Symbol":"TCS",     "Name":"Tata Consultancy",   "Price":"₹4,385","Change":"+1.8%","52W Low":"₹3,620","52W High":"₹4,490","Volume":"1.8M","Sentiment":"Bullish"},
    {"Symbol":"HDFCBANK","Name":"HDFC Bank",          "Price":"₹1,945","Change":"-0.6%","52W Low":"₹1,590","52W High":"₹2,010","Volume":"6.1M","Sentiment":"Neutral"},
    {"Symbol":"INFY",    "Name":"Infosys",            "Price":"₹2,156","Change":"+3.1%","52W Low":"₹1,640","52W High":"₹2,230","Volume":"3.3M","Sentiment":"Bullish"},
    {"Symbol":"WIPRO",   "Name":"Wipro",              "Price":"₹625",  "Change":"-0.4%","52W Low":"₹462",  "52W High":"₹670",  "Volume":"2.7M","Sentiment":"Neutral"},
    {"Symbol":"ITC",     "Name":"ITC Limited",        "Price":"₹540",  "Change":"+0.7%","52W Low":"₹458",  "52W High":"₹568",  "Volume":"5.8M","Sentiment":"Bullish"},
    {"Symbol":"TATASTEEL","Name":"Tata Steel",        "Price":"₹165",  "Change":"-1.8%","52W Low":"₹110",  "52W High":"₹182",  "Volume":"9.2M","Sentiment":"Bearish"},
    {"Symbol":"MARUTI",  "Name":"Maruti Suzuki",      "Price":"₹13,840","Change":"+0.5%","52W Low":"₹11,200","52W High":"₹14,960","Volume":"0.8M","Sentiment":"Bullish"},
]

st.markdown("<div class='intel-card'><h3 style='color:#e2e8f0;margin-bottom:16px;'>📋 My Watchlist</h3>", unsafe_allow_html=True)
df = pd.DataFrame(watchlist)
st.dataframe(
    df,
    width="stretch",
    hide_index=True,
    column_config={
        "Change": st.column_config.TextColumn("Change"),
        "Sentiment": st.column_config.TextColumn("Sentiment"),
    }
)
st.markdown("</div>", unsafe_allow_html=True)
