"""IntelStock — Main Streamlit entry point."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="IntelStock",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300..700&family=JetBrains+Mono:wght@400;500&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;}
#MainMenu,footer,header{visibility:hidden;}

/* Hide Streamlit's auto-generated page nav in sidebar — but keep the collapse toggle */
[data-testid="stSidebarNav"]{display:none!important;}

.stApp{background:#080c12!important;}
[data-testid="stSidebar"]{background:#0d1117!important;border-right:1px solid rgba(255,255,255,0.07)!important;}
[data-testid="stSidebar"] *{color:#e2e8f0!important;}
[data-testid="stSidebarContent"]{padding:0!important;}

/* Style the collapse/expand toggle button */
[data-testid="collapsedControl"]{
  background:#0d1117!important;
  border:1px solid rgba(255,255,255,0.07)!important;
  border-left:none!important;
  color:#64748b!important;
}
[data-testid="collapsedControl"]:hover{color:#00d4aa!important;background:#111820!important;}

/* Page links inside sidebar */
[data-testid="stSidebar"] [data-testid="stPageLink"] a {
  display:flex!important;align-items:center!important;gap:10px!important;
  padding:9px 16px!important;border-radius:8px!important;margin:2px 8px!important;
  font-size:0.85rem!important;font-weight:500!important;color:#94a3b8!important;
  text-decoration:none!important;transition:all 180ms ease!important;
  background:transparent!important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
  background:rgba(255,255,255,0.05)!important;color:#e2e8f0!important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"][aria-current="page"] a,
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] {
  background:rgba(0,212,170,0.1)!important;color:#00d4aa!important;
  border:1px solid rgba(0,212,170,0.2)!important;
}

[data-testid="metric-container"]{background:#0d1117;border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:20px;}
[data-testid="metric-container"]:hover{border-color:rgba(0,212,170,0.3);box-shadow:0 4px 24px rgba(0,212,170,0.08);}
[data-testid="metric-container"] label{color:#64748b!important;font-size:0.7rem!important;text-transform:uppercase;letter-spacing:0.08em;}
[data-testid="stMetricValue"]{font-family:'JetBrains Mono',monospace!important;font-size:1.6rem!important;font-weight:700!important;color:#e2e8f0!important;}
[data-testid="stMetricDelta"]{font-size:0.8rem!important;}
.intel-card{background:#0d1117;border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:20px 24px;margin-bottom:16px;}
.intel-card h3{color:#e2e8f0;font-size:0.875rem;font-weight:600;margin-bottom:4px;}
.intel-card .sub{color:#64748b;font-size:0.75rem;margin-bottom:16px;}
.ticker-wrap{background:#0d1117;border-bottom:1px solid rgba(255,255,255,0.07);padding:8px 0;overflow:hidden;white-space:nowrap;margin-bottom:24px;}
.ticker-content{display:inline-block;animation:ticker 30s linear infinite;font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#64748b;}
.ticker-content .up{color:#34d399;}
.ticker-content .dn{color:#f87171;}
@keyframes ticker{0%{transform:translateX(100vw)}100%{transform:translateX(-100%)}}
.stButton>button{background:rgba(0,212,170,0.12)!important;border:1px solid rgba(0,212,170,0.3)!important;color:#00d4aa!important;border-radius:8px!important;font-weight:600!important;}
.live-dot{display:inline-block;width:7px;height:7px;background:#f87171;border-radius:50%;margin-right:6px;animation:pulse-r 1.5s infinite;}
@keyframes pulse-r{0%,100%{opacity:1}50%{opacity:0.3}}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:20px 16px 16px;">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
        <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
          <rect width="32" height="32" rx="8" fill="rgba(0,212,170,0.12)"/>
          <path d="M8 22 L12 16 L16 19 L20 12 L24 14" stroke="#00d4aa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <circle cx="24" cy="14" r="2.5" fill="#00d4aa"/>
        </svg>
        <span style="font-size:1.2rem;font-weight:700;color:#e2e8f0;">Intel<span style="color:#00d4aa;">Stock</span></span>
      </div>
      <div style="font-size:0.65rem;color:#64748b;letter-spacing:0.06em;padding-left:42px;">AI STOCK INTELLIGENCE</div>
    </div>
    <hr style="border:none;border-top:1px solid rgba(255,255,255,0.07);margin:0 0 8px;"/>
    <div style="font-size:0.62rem;color:#334155;text-transform:uppercase;letter-spacing:0.1em;padding:8px 24px 4px;">Navigation</div>
    """, unsafe_allow_html=True)

    st.page_link("dashboard.py",                   label="📊  Dashboard")
    st.page_link("pages/overview.py",              label="🏠  Overview")
    st.page_link("pages/stock_research.py",        label="🔍  Stock Research")
    st.page_link("pages/sentiment_dashboard.py",   label="🧠  Sentiment")
    st.page_link("pages/portfolio_analyzer.py",    label="💼  Portfolio")
    st.page_link("pages/ai_chat.py",               label="💬  AI Chat")

    st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.07);margin:8px 0;'/>", unsafe_allow_html=True)
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding:10px 16px 16px;">
      <div style="width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#00d4aa,#60a5fa);display:grid;place-items:center;font-size:0.65rem;font-weight:700;color:#fff;flex-shrink:0;">CK</div>
      <div>
        <div style="font-size:0.8rem;font-weight:600;color:#e2e8f0;">Chanukya</div>
        <div style="font-size:0.7rem;color:#64748b;">Pro Trader</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Ticker ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ticker-wrap">
  <div class="ticker-content">
    &nbsp;&nbsp;&nbsp;
    <span class="up">▲ RELIANCE 2,987.45 (+2.4%)</span> &nbsp;·&nbsp;
    <span class="up">▲ TCS 4,123.80 (+1.8%)</span> &nbsp;·&nbsp;
    <span class="dn">▼ HDFC 1,680.20 (-0.9%)</span> &nbsp;·&nbsp;
    <span class="up">▲ INFY 1,924.60 (+3.1%)</span> &nbsp;·&nbsp;
    <span class="dn">▼ WIPRO 548.30 (-0.4%)</span> &nbsp;·&nbsp;
    <span class="up">▲ ITC 468.90 (+0.7%)</span> &nbsp;·&nbsp;
    <span class="dn">▼ TATASTEEL 184.50 (-1.8%)</span> &nbsp;·&nbsp;
    <span class="up">▲ NIFTY 24,762 (+1.24%)</span> &nbsp;·&nbsp;
    <span class="up">▲ SENSEX 81,467 (+0.87%)</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
col_title, col_live = st.columns([6, 1])
with col_title:
    st.markdown("<h1 style='color:#e2e8f0;font-size:1.6rem;font-weight:700;letter-spacing:-0.02em;margin:0;'>Dashboard</h1>", unsafe_allow_html=True)
with col_live:
    st.markdown("<div style='text-align:right;padding-top:8px;'><span class='live-dot'></span><span style='font-size:0.7rem;color:#f87171;font-weight:600;'>LIVE</span></div>", unsafe_allow_html=True)
st.markdown("<div style='color:#64748b;font-size:0.8rem;margin-bottom:24px;'>NSE · BSE · Real-time intelligence</div>", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("NIFTY 50", "24,762", "+1.24% today")
with c2: st.metric("SENSEX", "81,467", "+0.87%")
with c3: st.metric("Portfolio P&L", "+₹1.24L", "+8.3% overall")
with c4: st.metric("AI Sentiment", "Bullish 🟢", "73% positive signals", delta_color="off")

st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)

# ── Chart + Movers ────────────────────────────────────────────────────────────
col_chart, col_movers = st.columns([2, 1])

with col_chart:
    st.markdown("<div class='intel-card'><h3>Nifty 50 — Price Chart</h3><div class='sub'>NSE · Live feed</div>", unsafe_allow_html=True)
    times  = ["9:15","9:45","10:15","10:45","11:15","11:45","12:15","12:45","13:15","13:45","14:15","14:45","15:00","15:29"]
    prices = [24580,24620,24595,24660,24710,24690,24680,24720,24750,24735,24760,24730,24780,24762]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=times, y=prices, mode='lines',
        line=dict(color='#00d4aa', width=2),
        fill='tozeroy', fillcolor='rgba(0,212,170,0.06)',
        hovertemplate='<b>%{x}</b><br>Nifty: %{y:,}<extra></extra>'
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=280, margin=dict(l=0,r=0,t=8,b=0),
        xaxis=dict(showgrid=False, color='#64748b', tickfont=dict(size=10)),
        yaxis=dict(gridcolor='rgba(255,255,255,0.04)', color='#64748b', tickfont=dict(size=10)),
        showlegend=False, hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

with col_movers:
    st.markdown("<div class='intel-card'><h3>Top Movers</h3><div class='sub'>NSE today</div>", unsafe_allow_html=True)
    movers = [
        {"sym":"INFY",    "sector":"IT",      "price":"₹1,924","chg":"+3.1%","up":True},
        {"sym":"RELIANCE","sector":"Energy",  "price":"₹2,987","chg":"+2.4%","up":True},
        {"sym":"TCS",     "sector":"IT",      "price":"₹4,124","chg":"+1.8%","up":True},
        {"sym":"BAJFIN",  "sector":"Finance", "price":"₹7,240","chg":"-1.2%","up":False},
        {"sym":"HDFC",    "sector":"Banking", "price":"₹1,680","chg":"-0.9%","up":False},
    ]
    for m in movers:
        color = "#34d399" if m["up"] else "#f87171"
        arrow = "▲" if m["up"] else "▼"
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;padding:10px;border-radius:8px;margin-bottom:4px;border:1px solid rgba(255,255,255,0.05);">
          <div style="width:36px;height:36px;border-radius:8px;background:#111820;border:1px solid rgba(255,255,255,0.07);display:grid;place-items:center;font-size:0.55rem;font-weight:700;color:#64748b;">{m['sym'][:3]}</div>
          <div style="flex:1;"><div style="font-size:0.82rem;font-weight:600;color:#e2e8f0;">{m['sym']}</div><div style="font-size:0.7rem;color:#64748b;">{m['sector']}</div></div>
          <div style="text-align:right;"><div style="font-size:0.82rem;font-weight:600;color:#e2e8f0;font-family:'JetBrains Mono',monospace;">{m['price']}</div><div style="font-size:0.72rem;font-weight:600;color:{color};">{arrow} {m['chg']}</div></div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── Sector bar chart ─────────────────────────────────────────────────────────
st.markdown("<div class='intel-card'><h3>Sector Performance</h3><div class='sub'>Today vs yesterday</div>", unsafe_allow_html=True)
sectors = ["IT","Banking","Energy","Auto","FMCG","Pharma","Metal","Realty"]
changes = [2.4,-0.6,1.8,0.5,-0.3,1.1,-1.8,0.9]
colors  = ['#34d399' if c>0 else '#f87171' for c in changes]
fig2 = go.Figure(go.Bar(
    x=sectors, y=changes, marker_color=colors,
    text=[f"{'+' if c>0 else ''}{c}%" for c in changes],
    textposition='outside', textfont=dict(size=11, color='#e2e8f0')
))
fig2.update_layout(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    height=200, margin=dict(l=0,r=0,t=24,b=0),
    xaxis=dict(showgrid=False, color='#64748b', tickfont=dict(size=11)),
    yaxis=dict(showgrid=False, visible=False),
    showlegend=False,
)
st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
st.markdown("</div>", unsafe_allow_html=True)
