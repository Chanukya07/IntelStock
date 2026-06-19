"""Portfolio Analyzer page."""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Portfolio — IntelStock", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300..700&family=JetBrains+Mono:wght@400;500&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;}
#MainMenu,footer,header{visibility:hidden;}
.stApp{background:#080c12!important;}
[data-testid="stSidebar"]{background:#0d1117!important;border-right:1px solid rgba(255,255,255,0.07)!important;}
[data-testid="stSidebar"] *{color:#e2e8f0!important;}
[data-testid="metric-container"]{background:#0d1117;border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:20px;}
[data-testid="stMetricValue"]{font-family:'JetBrains Mono',monospace!important;font-size:1.4rem!important;font-weight:700!important;color:#e2e8f0!important;}
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

st.markdown("<h1 style='color:#e2e8f0;font-size:1.6rem;font-weight:700;margin-bottom:4px;'>Portfolio Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<div style='color:#64748b;font-size:0.8rem;margin-bottom:24px;'>Total value: ₹16.2L · 8.3% overall returns</div>", unsafe_allow_html=True)

c1,c2,c3,c4 = st.columns(4)
with c1: st.metric("Total Value","₹16.2L","+₹1.24L")
with c2: st.metric("Overall Return","+8.3%","+2.1% this month")
with c3: st.metric("Day P&L","+₹18,420","+1.14%")
with c4: st.metric("XIRR","22.4%","annualised")

st.markdown("<br>", unsafe_allow_html=True)

col_donut, col_holdings = st.columns([1, 2])

with col_donut:
    st.markdown("<div class='intel-card'><h3 style='color:#e2e8f0;margin-bottom:16px;'>Allocation</h3>", unsafe_allow_html=True)
    labels = ["IT","Banking","Energy","Finance","Auto"]
    values = [32, 24, 20, 14, 10]
    colors = ["#00d4aa","#60a5fa","#fbbf24","#34d399","#f87171"]

    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.72,
        marker=dict(colors=colors, line=dict(color='#080c12', width=2)),
        textinfo='label+percent',
        textfont=dict(size=11, color='#e2e8f0'),
        hovertemplate='<b>%{label}</b><br>%{percent}<extra></extra>'
    ))
    fig.add_annotation(text="₹16.2L", x=0.5, y=0.55, font=dict(size=18, color='#e2e8f0', family='JetBrains Mono'), showarrow=False)
    fig.add_annotation(text="Total",  x=0.5, y=0.42, font=dict(size=12, color='#64748b'), showarrow=False)
    fig.update_layout(
        paper_bgcolor='transparent', height=300,
        margin=dict(l=0,r=0,t=0,b=0),
        legend=dict(font=dict(color='#94a3b8', size=11), bgcolor='transparent')
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

with col_holdings:
    st.markdown("<div class='intel-card'><h3 style='color:#e2e8f0;margin-bottom:16px;'>Holdings</h3>", unsafe_allow_html=True)
    holdings = [
        {"sym":"RELIANCE","name":"Reliance Industries","qty":12,"avg":"₹2,640","cmp":"₹2,987","value":"₹3.58L","pnl":"+₹18,400","ret":"+13.1%","up":True},
        {"sym":"TCS",     "name":"Tata Consultancy",   "qty":5, "avg":"₹3,700","cmp":"₹4,124","value":"₹2.06L","pnl":"+₹12,100","ret":"+11.5%","up":True},
        {"sym":"HDFC",    "name":"HDFC Bank",          "qty":30,"avg":"₹1,787","cmp":"₹1,680","value":"₹5.04L","pnl":"-₹3,200", "ret":"-6.0%", "up":False},
        {"sym":"INFY",    "name":"Infosys",            "qty":20,"avg":"₹1,444","cmp":"₹1,925","value":"₹3.85L","pnl":"+₹9,600", "ret":"+33.3%","up":True},
        {"sym":"ITC",     "name":"ITC Limited",        "qty":100,"avg":"₹440", "cmp":"₹469",  "value":"₹4.69L","pnl":"+₹2,900", "ret":"+6.6%", "up":True},
    ]
    for h in holdings:
        pnl_color = "#34d399" if h['up'] else "#f87171"
        bar_pct = min(abs(float(h['ret'].replace('%','').replace('+','').replace('-',''))) * 2, 100)
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:12px;padding:12px;border:1px solid rgba(255,255,255,0.05);border-radius:8px;margin-bottom:8px;'>
          <div style='width:40px;height:40px;border-radius:8px;background:rgba(0,212,170,0.1);display:grid;place-items:center;font-size:0.6rem;font-weight:700;color:#00d4aa;flex-shrink:0;'>{h['sym'][:4]}</div>
          <div style='flex:1;min-width:0;'>
            <div style='font-size:0.85rem;font-weight:600;color:#e2e8f0;'>{h['name']}</div>
            <div style='font-size:0.72rem;color:#64748b;'>{h['qty']} shares · Avg {h['avg']}</div>
            <div style='height:4px;background:rgba(255,255,255,0.06);border-radius:2px;margin-top:6px;overflow:hidden;'>
              <div style='height:100%;width:{bar_pct}%;background:{pnl_color};border-radius:2px;transition:width 1s ease;'></div>
            </div>
          </div>
          <div style='text-align:right;'>
            <div style='font-size:0.85rem;font-weight:600;color:#e2e8f0;font-family:"JetBrains Mono",monospace;'>{h['value']}</div>
            <div style='font-size:0.75rem;font-weight:600;color:{pnl_color};'>{h['pnl']} ({h['ret']})</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
