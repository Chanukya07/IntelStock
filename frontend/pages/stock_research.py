"""Stock Research page."""
import streamlit as st
import plotly.graph_objects as go
import numpy as np

from backend.services.insight_service import InsightService
from backend.services.market_data_service import MarketDataService
from frontend.sidebar import inject_styles, render_sidebar

st.set_page_config(page_title="Stock Research — IntelStock", layout="wide")

inject_styles()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300..700&family=JetBrains+Mono:wght@400;500&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;}
[data-testid="metric-container"]{background:#0d1117;border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:20px;}
[data-testid="stMetricValue"]{font-family:'JetBrains Mono',monospace!important;font-size:1.4rem!important;font-weight:700!important;color:#e2e8f0!important;}
.intel-card{background:#0d1117;border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:20px 24px;margin-bottom:16px;}
.stTextInput input{background:#0d1117!important;border:1px solid rgba(255,255,255,0.1)!important;color:#e2e8f0!important;border-radius:8px!important;}
.stTextInput input:focus{border-color:rgba(0,212,170,0.5)!important;box-shadow:0 0 0 3px rgba(0,212,170,0.12)!important;}
.stButton>button{background:rgba(0,212,170,0.12)!important;border:1px solid rgba(0,212,170,0.3)!important;color:#00d4aa!important;border-radius:8px!important;font-weight:600!important;}
.quick-chip{display:inline-block;border:1px solid rgba(255,255,255,0.08);border-radius:999px;padding:6px 12px;margin:0 8px 8px 0;color:#cbd5e1;font-size:0.74rem;}
</style>
""", unsafe_allow_html=True)

render_sidebar()

market_data_service = MarketDataService()
insight_service = InsightService()

st.markdown("<h1 style='color:#e2e8f0;font-size:1.6rem;font-weight:700;margin-bottom:4px;'>Stock Research</h1>", unsafe_allow_html=True)
st.markdown("<div style='color:#64748b;font-size:0.8rem;margin-bottom:16px;'>Enter any NSE symbol for AI-powered analysis</div>", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom:14px;'><span class='quick-chip'>RELIANCE</span><span class='quick-chip'>TCS</span><span class='quick-chip'>INFY</span><span class='quick-chip'>HDFC</span><span class='quick-chip'>NIFTY</span></div>", unsafe_allow_html=True)

col_in, col_btn = st.columns([3, 1])
with col_in:
    symbol = st.text_input("", placeholder="Enter NSE symbol (e.g. RELIANCE, TCS, INFY)", label_visibility="collapsed")
with col_btn:
    search = st.button("🔍  Analyze", use_container_width=True)

if symbol or search:
    sym = symbol.strip().upper()
        if sym:
                quote = market_data_service.fetch_live_quote(sym)
                report = insight_service.generate_report(sym)
                pnl_color = "#34d399" if quote['change_pct'] > 0 else "#f87171"
                sent_rgb = "52,211,153" if quote['sentiment']=="Bullish" else "248,113,113" if quote['sentiment']=="Bearish" else "100,116,139"
                sent_color = "#34d399" if quote['sentiment']=="Bullish" else "#f87171" if quote['sentiment']=="Bearish" else "#94a3b8"
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:16px;margin:20px 0 8px;'>
          <div>
                        <div style='font-size:1.2rem;font-weight:700;color:#e2e8f0;'>{quote['symbol']} <span style='font-size:0.9rem;font-weight:400;color:#64748b;'>· {quote['name']}</span></div>
                        <div style='font-size:2rem;font-weight:700;color:#e2e8f0;font-family:"JetBrains Mono",monospace;'>₹{quote['price']:,} <span style='font-size:1rem;color:{pnl_color};'>{'+' if quote['change_pct']>0 else ''}{quote['change_pct']}%</span></div>
          </div>
                    <div style='margin-left:auto;background:rgba({sent_rgb},0.15);color:{sent_color};padding:6px 16px;border-radius:999px;font-weight:600;font-size:0.8rem;'>{quote['sentiment']} · {report['confidence']}</div>
        </div>
        """, unsafe_allow_html=True)

        k1,k2,k3,k4,k5 = st.columns(5)
                with k1: st.metric("Sector", quote['sector'])
                with k2: st.metric("Volume", quote['volume'])
                with k3: st.metric("Support", f"₹{quote['support']:,}")
                with k4: st.metric("Resistance", f"₹{quote['resistance']:,}")
                with k5: st.metric("Signal", quote['sentiment'])

        st.markdown("<br>", unsafe_allow_html=True)
        col_chart, col_ai = st.columns([3, 2])

        with col_chart:
            st.markdown("<div class='intel-card'><h3 style='color:#e2e8f0;margin-bottom:16px;'>Price Chart — 1 Month</h3>", unsafe_allow_html=True)
            days = list(range(22))
            prices = [quote['price'] * (1 + 0.004*i + 0.006*np.sin(i*0.5)) for i in days]
            prices = [round(p - 80 + 20*np.random.rand(), 2) for p in prices]
            prices[-1] = quote['price']
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
                            <p style='color:#cbd5e1;font-size:0.85rem;line-height:1.7;'>{report['summary']}</p>
                            <p style='color:#e2e8f0;font-size:0.82rem;font-weight:600;margin-top:12px;'>Recommendation: {report['recommendation']}</p>
                            <p style='color:#64748b;font-size:0.75rem;margin-top:8px;'>Catalyst: {report['catalysts'][0]}</p>
            </div>
            """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style='text-align:center;padding:60px 20px;color:#334155;'>
      <div style='font-size:3rem;margin-bottom:16px;'>🔍</div>
      <div style='font-size:1rem;font-weight:600;color:#64748b;'>Enter an NSE symbol to get started</div>
            <div style='font-size:0.8rem;color:#334155;margin-top:8px;'>Try: RELIANCE · TCS · HDFC · INFY · NIFTY</div>
    </div>
    """, unsafe_allow_html=True)
