"""Overview page — market indices and watchlist."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Overview — IntelStock", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300..700&family=JetBrains+Mono:wght@400;500&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;}
#MainMenu,footer,header{visibility:hidden;}
.stApp{background:#080c12!important;}
[data-testid="stSidebar"]{background:#0d1117!important;border-right:1px solid rgba(255,255,255,0.07)!important;}
[data-testid="stSidebar"] *{color:#e2e8f0!important;}
[data-testid="metric-container"]{background:#0d1117;border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:20px;}
[data-testid="stMetricValue"]{font-family:'JetBrains Mono',monospace!important;font-size:1.5rem!important;font-weight:700!important;color:#e2e8f0!important;}
.intel-card{background:#0d1117;border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:20px 24px;margin-bottom:16px;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<div style='padding:8px 0 16px;'><span style='font-size:1.2rem;font-weight:700;color:#e2e8f0;'>Intel<span style='color:#00d4aa;'>Stock</span></span></div>", unsafe_allow_html=True)
    st.page_link("dashboard.py", label="📊  Dashboard")
    st.page_link("pages/overview.py", label="🏠  Overview")
    st.page_link("pages/stock_research.py", label="🔍  Stock Research")
    st.page_link("pages/sentiment_dashboard.py", label="🧠  Sentiment")
    st.page_link("pages/portfolio_analyzer.py", label="💼  Portfolio")
    st.page_link("pages/ai_chat.py", label="💬  AI Chat")

st.markdown("<h1 style='color:#e2e8f0;font-size:1.6rem;font-weight:700;margin-bottom:4px;'>Market Overview</h1>", unsafe_allow_html=True)
st.markdown("<div style='color:#64748b;font-size:0.8rem;margin-bottom:24px;'>Live indices · NSE/BSE</div>", unsafe_allow_html=True)

# KPIs
c1,c2,c3,c4 = st.columns(4)
with c1: st.metric("NIFTY 50","24,762","+306 (+1.24%)")
with c2: st.metric("NIFTY BANK","52,847","+0.63%")
with c3: st.metric("SENSEX","81,467","+702 (+0.87%)")
with c4: st.metric("VIX","13.42","-0.8%",delta_color="inverse")

st.markdown("<br>", unsafe_allow_html=True)

# Watchlist table
watchlist = [
    {"Symbol":"RELIANCE","Name":"Reliance Industries","Price":"₹2,987","Change":"+2.4%","52W Low":"₹2,220","52W High":"₹3,024","Volume":"4.2M","Sentiment":"Bullish"},
    {"Symbol":"TCS",     "Name":"Tata Consultancy",   "Price":"₹4,124","Change":"+1.8%","52W Low":"₹3,441","52W High":"₹4,592","Volume":"1.8M","Sentiment":"Bullish"},
    {"Symbol":"HDFC",    "Name":"HDFC Bank",          "Price":"₹1,680","Change":"-0.9%","52W Low":"₹1,430","52W High":"₹1,795","Volume":"6.1M","Sentiment":"Neutral"},
    {"Symbol":"INFY",    "Name":"Infosys",            "Price":"₹1,925","Change":"+3.1%","52W Low":"₹1,358","52W High":"₹2,006","Volume":"3.3M","Sentiment":"Bullish"},
    {"Symbol":"WIPRO",   "Name":"Wipro",              "Price":"₹548",  "Change":"-0.4%","52W Low":"₹398",  "52W High":"₹593",  "Volume":"2.7M","Sentiment":"Neutral"},
    {"Symbol":"ITC",     "Name":"ITC Limited",        "Price":"₹469",  "Change":"+0.7%","52W Low":"₹412",  "52W High":"₹509",  "Volume":"5.8M","Sentiment":"Bullish"},
    {"Symbol":"TATASTEEL","Name":"Tata Steel",        "Price":"₹184",  "Change":"-1.8%","52W Low":"₹122",  "52W High":"₹199",  "Volume":"9.2M","Sentiment":"Bearish"},
    {"Symbol":"MARUTI",  "Name":"Maruti Suzuki",      "Price":"₹12,440","Change":"+0.5%","52W Low":"₹10,030","52W High":"₹13,680","Volume":"0.8M","Sentiment":"Bullish"},
]

st.markdown("<div class='intel-card'><h3 style='color:#e2e8f0;margin-bottom:16px;'>📋 My Watchlist</h3>", unsafe_allow_html=True)
df = pd.DataFrame(watchlist)
st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Change": st.column_config.TextColumn("Change"),
        "Sentiment": st.column_config.TextColumn("Sentiment"),
    }
)
st.markdown("</div>", unsafe_allow_html=True)
