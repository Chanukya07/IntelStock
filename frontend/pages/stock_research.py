"""Stock Research page."""
import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Stock Research — IntelStock", layout="wide")

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
.stTextInput input{background:#0d1117!important;border:1px solid rgba(255,255,255,0.1)!important;color:#e2e8f0!important;border-radius:8px!important;}
.stTextInput input:focus{border-color:rgba(0,212,170,0.5)!important;box-shadow:0 0 0 3px rgba(0,212,170,0.12)!important;}
.stButton>button{background:rgba(0,212,170,0.12)!important;border:1px solid rgba(0,212,170,0.3)!important;color:#00d4aa!important;border-radius:8px!important;font-weight:600!important;}
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

st.markdown("<h1 style='color:#e2e8f0;font-size:1.6rem;font-weight:700;margin-bottom:4px;'>Stock Research</h1>", unsafe_allow_html=True)
st.markdown("<div style='color:#64748b;font-size:0.8rem;margin-bottom:24px;'>Enter any NSE symbol for AI-powered analysis</div>", unsafe_allow_html=True)

STOCKS = {
    "RELIANCE": {"name":"Reliance Industries","price":2987,"chg":2.4,"pe":24.3,"pb":2.1,"mktcap":"₹20.2L Cr","div":0.8,"roe":13.2,"sentiment":"Bullish","score":82,
                 "ai":"Reliance Industries is showing strong bullish momentum. Q4 FY26 results beat estimates with Jio revenue up 12% YoY and retail segment delivering record margins. Key support at ₹2,880, resistance at ₹3,050. FII ownership increased 0.4% this quarter. Recommendation: Hold / Accumulate on dips."},
    "TCS":      {"name":"Tata Consultancy","price":4124,"chg":1.8,"pe":31.2,"pb":12.4,"mktcap":"₹14.9L Cr","div":1.2,"roe":47.8,"sentiment":"Bullish","score":78,
                 "ai":"TCS continues to outperform the IT index. US deal pipeline commentary for Q1 FY27 is positive with large deal wins of $2.4B. Key levels: support ₹3,980, resistance ₹4,280. Recommendation: Buy on dips."},
    "HDFC":     {"name":"HDFC Bank","price":1680,"chg":-0.9,"pe":19.1,"pb":2.8,"mktcap":"₹12.7L Cr","div":1.6,"roe":15.4,"sentiment":"Neutral","score":54,
                 "ai":"HDFC Bank is facing near-term headwinds post merger integration. NIM compression continues but credit growth remains healthy at 14% YoY. Recommendation: Neutral — wait for NIM stabilization."},
    "INFY":     {"name":"Infosys","price":1925,"chg":3.1,"pe":27.4,"pb":8.9,"mktcap":"₹7.9L Cr","div":2.1,"roe":32.6,"sentiment":"Bullish","score":75,
                 "ai":"Infosys raised FY27 revenue guidance to 4-7% in CC terms, beating analyst expectations. The stock broke out of a 3-month consolidation range. Recommendation: Buy."},
    "WIPRO":    {"name":"Wipro","price":548,"chg":-0.4,"pe":22.1,"pb":3.4,"mktcap":"₹2.8L Cr","div":0.5,"roe":14.2,"sentiment":"Neutral","score":49,
                 "ai":"Wipro remains range-bound as deal ramp-ups take time to reflect in revenue. Monitor Q1 results for direction. Recommendation: Neutral."},
}

col_in, col_btn = st.columns([3, 1])
with col_in:
    symbol = st.text_input("", placeholder="Enter NSE symbol (e.g. RELIANCE, TCS, INFY)", label_visibility="collapsed")
with col_btn:
    search = st.button("🔍  Analyze", use_container_width=True)

if symbol or search:
    sym = symbol.strip().upper()
    if sym in STOCKS:
        s = STOCKS[sym]
        pnl_color = "#34d399" if s['chg'] > 0 else "#f87171"
        sent_rgb = "52,211,153" if s['sentiment']=="Bullish" else "248,113,113" if s['sentiment']=="Bearish" else "100,116,139"
        sent_color = "#34d399" if s['sentiment']=="Bullish" else "#f87171" if s['sentiment']=="Bearish" else "#94a3b8"
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:16px;margin:20px 0 8px;'>
          <div>
            <div style='font-size:1.2rem;font-weight:700;color:#e2e8f0;'>{sym} <span style='font-size:0.9rem;font-weight:400;color:#64748b;'>· {s['name']}</span></div>
            <div style='font-size:2rem;font-weight:700;color:#e2e8f0;font-family:"JetBrains Mono",monospace;'>₹{s['price']:,} <span style='font-size:1rem;color:{pnl_color};'>{'+' if s['chg']>0 else ''}{s['chg']}%</span></div>
          </div>
          <div style='margin-left:auto;background:rgba({sent_rgb},0.15);color:{sent_color};padding:6px 16px;border-radius:999px;font-weight:600;font-size:0.8rem;'>{s['sentiment']} · {s['score']}%</div>
        </div>
        """, unsafe_allow_html=True)

        k1,k2,k3,k4,k5 = st.columns(5)
        with k1: st.metric("P/E Ratio", s['pe'])
        with k2: st.metric("P/B Ratio", s['pb'])
        with k3: st.metric("Mkt Cap", s['mktcap'])
        with k4: st.metric("Div Yield", f"{s['div']}%")
        with k5: st.metric("ROE", f"{s['roe']}%")

        st.markdown("<br>", unsafe_allow_html=True)
        col_chart, col_ai = st.columns([3, 2])

        with col_chart:
            st.markdown("<div class='intel-card'><h3 style='color:#e2e8f0;margin-bottom:16px;'>Price Chart — 1 Month</h3>", unsafe_allow_html=True)
            days = list(range(22))
            prices = [s['price'] * (1 + 0.004*i + 0.006*np.sin(i*0.5)) for i in days]
            prices = [round(p - 80 + 20*np.random.rand(), 2) for p in prices]
            prices[-1] = s['price']
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=days, y=prices,
                mode='lines',
                line=dict(color='#00d4aa', width=2),
                fill='tozeroy',
                fillcolor='rgba(0,212,170,0.06)',
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=240, margin=dict(l=0,r=0,t=8,b=0),
                xaxis=dict(showgrid=False, color='#64748b', tickfont=dict(size=10)),
                yaxis=dict(gridcolor='rgba(255,255,255,0.04)', color='#64748b', tickfont=dict(size=10)),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            st.markdown("</div>", unsafe_allow_html=True)

        with col_ai:
            st.markdown(f"""
            <div class='intel-card'>
              <h3 style='color:#00d4aa;margin-bottom:12px;'>🤖 AI Analysis</h3>
              <p style='color:#cbd5e1;font-size:0.85rem;line-height:1.7;'>{s['ai']}</p>
            </div>
            """, unsafe_allow_html=True)
    elif sym:
        st.warning(f"Symbol '{sym}' not found. Try: RELIANCE, TCS, HDFC, INFY, WIPRO")
else:
    st.markdown("""
    <div style='text-align:center;padding:60px 20px;color:#334155;'>
      <div style='font-size:3rem;margin-bottom:16px;'>🔍</div>
      <div style='font-size:1rem;font-weight:600;color:#64748b;'>Enter an NSE symbol to get started</div>
      <div style='font-size:0.8rem;color:#334155;margin-top:8px;'>Try: RELIANCE · TCS · HDFC · INFY · WIPRO</div>
    </div>
    """, unsafe_allow_html=True)
