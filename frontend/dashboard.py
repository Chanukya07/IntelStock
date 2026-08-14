"""IntelStock — Main Streamlit entry point."""
import streamlit as st
import plotly.graph_objects as go

from frontend.sidebar import inject_styles, render_sidebar

st.set_page_config(
    page_title="IntelStock",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_styles()

st.markdown("""
<style>
.intel-card h3{color:#e2e8f0;font-size:0.875rem;font-weight:600;margin-bottom:4px;}
.intel-card .sub{color:#64748b;font-size:0.75rem;margin-bottom:16px;}
.ticker-wrap{background:#0d1117;border-bottom:1px solid rgba(255,255,255,0.07);padding:8px 0;overflow:hidden;white-space:nowrap;margin-bottom:24px;}
.ticker-content{display:inline-block;animation:ticker 30s linear infinite;font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#64748b;}
.ticker-content .up{color:#34d399;}
.ticker-content .dn{color:#f87171;}
@keyframes ticker{0%{transform:translateX(100vw)}100%{transform:translateX(-100%)}}
.live-dot{display:inline-block;width:7px;height:7px;background:#f87171;border-radius:50%;margin-right:6px;animation:pulse-r 1.5s infinite;}
@keyframes pulse-r{0%,100%{opacity:1}50%{opacity:0.3}}
</style>
""", unsafe_allow_html=True)

render_sidebar()

# ── Ticker ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ticker-wrap">
  <div class="ticker-content">
    &nbsp;&nbsp;&nbsp;
    <span class="up">▲ RELIANCE 3,245.50 (+2.4%)</span> &nbsp;·&nbsp;
    <span class="up">▲ TCS 4,385.75 (+1.8%)</span> &nbsp;·&nbsp;
    <span class="dn">▼ HDFCBANK 1,945.30 (-0.6%)</span> &nbsp;·&nbsp;
    <span class="up">▲ INFY 2,156.40 (+3.1%)</span> &nbsp;·&nbsp;
    <span class="dn">▼ WIPRO 625.80 (-0.4%)</span> &nbsp;·&nbsp;
    <span class="up">▲ ITC 540.20 (+0.7%)</span> &nbsp;·&nbsp;
    <span class="dn">▼ TATASTEEL 165.30 (-1.8%)</span> &nbsp;·&nbsp;
    <span class="up">▲ NIFTY 26,485 (+1.25%)</span> &nbsp;·&nbsp;
    <span class="up">▲ SENSEX 86,940 (+1.22%)</span>
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
with c1: st.metric("NIFTY 50", "26,485", "+1.25% today")
with c2: st.metric("SENSEX", "86,940", "+1.22%")
with c3: st.metric("Portfolio P&L", "+₹1.24L", "+8.3% overall")
with c4: st.metric("AI Sentiment", "Bullish 🟢", "73% positive signals", delta_color="off")

st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)

# ── Chart + Movers ────────────────────────────────────────────────────────────
col_chart, col_movers = st.columns([2, 1])

with col_chart:
    st.markdown("<div class='intel-card'><h3>Nifty 50 — Price Chart</h3><div class='sub'>NSE · Live feed</div>", unsafe_allow_html=True)
    times  = ["9:15","9:45","10:15","10:45","11:15","11:45","12:15","12:45","13:15","13:45","14:15","14:45","15:00","15:29"]
    prices = [26185,26220,26195,26260,26310,26290,26280,26320,26350,26335,26360,26330,26380,26485]
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
    st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

with col_movers:
    st.markdown("<div class='intel-card'><h3>Top Movers</h3><div class='sub'>NSE today</div>", unsafe_allow_html=True)
    movers = [
        {"sym":"INFY",    "sector":"IT",      "price":"₹2,156","chg":"+3.1%","up":True},
        {"sym":"RELIANCE","sector":"Energy",  "price":"₹3,245","chg":"+2.4%","up":True},
        {"sym":"TCS",     "sector":"IT",      "price":"₹4,385","chg":"+1.8%","up":True},
        {"sym":"BAJFIN",  "sector":"Finance", "price":"₹8,640","chg":"-1.2%","up":False},
        {"sym":"HDFCBANK","sector":"Banking", "price":"₹1,945","chg":"-0.6%","up":False},
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
st.plotly_chart(fig2, width="stretch", config={'displayModeBar': False})
st.markdown("</div>", unsafe_allow_html=True)
