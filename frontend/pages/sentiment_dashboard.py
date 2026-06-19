"""Sentiment Dashboard page."""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from frontend.sidebar import inject_styles, render_sidebar

st.set_page_config(page_title="Sentiment — IntelStock", layout="wide")

inject_styles()

st.markdown("""
<style>
[data-testid="metric-container"]{background:#0d1117;border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:20px;}
[data-testid="stMetricValue"]{font-family:'JetBrains Mono',monospace!important;font-size:1.4rem!important;font-weight:700!important;color:#e2e8f0!important;}
.intel-card{background:#0d1117;border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:20px 24px;margin-bottom:16px;}
</style>
""", unsafe_allow_html=True)

render_sidebar()

st.markdown("<h1 style='color:#e2e8f0;font-size:1.6rem;font-weight:700;margin-bottom:4px;'>Sentiment Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<div style='color:#64748b;font-size:0.8rem;margin-bottom:24px;'>AI-powered market sentiment · Updated every 15 min</div>", unsafe_allow_html=True)

# Top metrics
c1,c2,c3,c4 = st.columns(4)
with c1: st.metric("Overall Sentiment","Bullish 🟢","73% positive")
with c2: st.metric("FII Flow","+₹2,847 Cr","Net buying")
with c3: st.metric("DII Flow","+₹1,243 Cr","Net buying")
with c4: st.metric("Put/Call Ratio","0.82","-0.06",delta_color="inverse")

st.markdown("<br>", unsafe_allow_html=True)

col_radar, col_news = st.columns([1, 1])

with col_radar:
    st.markdown("<div class='intel-card'><h3 style='color:#e2e8f0;margin-bottom:16px;'>Sector Sentiment Radar</h3>", unsafe_allow_html=True)
    sectors = ["IT","Banking","Energy","Auto","FMCG","Pharma","Metal"]
    scores  = [78, 54, 72, 61, 58, 65, 34]
    sectors_closed = sectors + [sectors[0]]
    scores_closed  = scores  + [scores[0]]

    fig = go.Figure(go.Scatterpolar(
        r=scores_closed, theta=sectors_closed,
        fill='toself',
        fillcolor='rgba(0,212,170,0.12)',
        line=dict(color='#00d4aa', width=2),
        marker=dict(color='#00d4aa', size=6)
    ))
    fig.update_layout(
        paper_bgcolor='transparent',
        polar=dict(
            bgcolor='transparent',
            radialaxis=dict(visible=True, range=[0,100], color='#64748b', gridcolor='rgba(255,255,255,0.06)', tickfont=dict(size=9)),
            angularaxis=dict(color='#e2e8f0', gridcolor='rgba(255,255,255,0.06)', tickfont=dict(size=11))
        ),
        showlegend=False,
        height=320,
        margin=dict(l=40,r=40,t=20,b=20)
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

with col_news:
    st.markdown("<div class='intel-card'><h3 style='color:#e2e8f0;margin-bottom:16px;'>Market News</h3>", unsafe_allow_html=True)
    news = [
        {"src":"Economic Times","time":"14m ago","title":"RBI holds repo rate at 6.5%; signals cautious easing in H2 FY26","sent":"Neutral"},
        {"src":"Moneycontrol",  "time":"38m ago","title":"Reliance Q4 results beat estimates; Jio revenue up 12% YoY","sent":"Bullish"},
        {"src":"Business Std",  "time":"1h ago", "title":"IT sector outlook positive as US deal pipeline strengthens","sent":"Bullish"},
        {"src":"Mint",          "time":"2h ago", "title":"Metal stocks under pressure as China demand concerns resurface","sent":"Bearish"},
        {"src":"NDTV Profit",   "time":"3h ago", "title":"Auto sales data beats estimates; Maruti & M&M rally","sent":"Bullish"},
    ]
    sent_color = {"Bullish":"#34d399","Bearish":"#f87171","Neutral":"#94a3b8"}
    sent_bg    = {"Bullish":"rgba(52,211,153,0.12)","Bearish":"rgba(248,113,113,0.12)","Neutral":"rgba(100,116,139,0.15)"}
    for n in news:
        st.markdown(f"""
        <div style='padding:12px;border:1px solid rgba(255,255,255,0.05);border-radius:8px;margin-bottom:8px;'>
          <div style='display:flex;justify-content:space-between;margin-bottom:4px;'>
            <span style='font-size:0.7rem;font-weight:600;color:#00d4aa;'>{n['src']}</span>
            <span style='font-size:0.7rem;color:#64748b;'>{n['time']}</span>
          </div>
          <div style='font-size:0.82rem;color:#cbd5e1;line-height:1.4;margin-bottom:6px;'>{n['title']}</div>
          <span style='background:{sent_bg[n['sent']]};color:{sent_color[n['sent']]};padding:2px 8px;border-radius:999px;font-size:0.65rem;font-weight:600;'>{n['sent']}</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Trending stocks
st.markdown("<div class='intel-card'><h3 style='color:#e2e8f0;margin-bottom:16px;'>Trending Stocks</h3>", unsafe_allow_html=True)
tickers = [
    {"sym":"RELIANCE","chg":"+2.4%","sent":"Bullish","mentions":"4,821"},
    {"sym":"TCS",     "chg":"+1.8%","sent":"Bullish","mentions":"2,345"},
    {"sym":"INFY",    "chg":"+3.1%","sent":"Bullish","mentions":"1,987"},
    {"sym":"HDFC",    "chg":"-0.9%","sent":"Neutral","mentions":"1,543"},
    {"sym":"TATASTEEL","chg":"-1.8%","sent":"Bearish","mentions":"1,221"},
]
cols = st.columns(5)
for i, t in enumerate(tickers):
    sc = {"Bullish":"#34d399","Bearish":"#f87171","Neutral":"#94a3b8"}[t['sent']]
    bg = {"Bullish":"rgba(52,211,153,0.12)","Bearish":"rgba(248,113,113,0.12)","Neutral":"rgba(100,116,139,0.15)"}[t['sent']]
    with cols[i]:
        st.markdown(f"""
        <div style='background:#111820;border:1px solid rgba(255,255,255,0.07);border-radius:10px;padding:14px;text-align:center;'>
          <div style='font-weight:700;color:#e2e8f0;font-size:0.9rem;'>{t['sym']}</div>
          <div style='color:{sc};font-size:0.82rem;font-weight:600;margin:4px 0;'>{t['chg']}</div>
          <span style='background:{bg};color:{sc};padding:2px 8px;border-radius:999px;font-size:0.65rem;font-weight:600;'>{t['sent']}</span>
          <div style='color:#64748b;font-size:0.7rem;margin-top:6px;'>💬 {t['mentions']}</div>
        </div>
        """, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
