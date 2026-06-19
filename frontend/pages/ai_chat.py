"""AI Chat page."""
import streamlit as st
import time

st.set_page_config(page_title="AI Chat — IntelStock", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300..700&family=JetBrains+Mono:wght@400;500&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;}
#MainMenu,footer,header{visibility:hidden;}
.stApp{background:#080c12!important;}
[data-testid="stSidebar"]{background:#0d1117!important;border-right:1px solid rgba(255,255,255,0.07)!important;}
[data-testid="stSidebar"] *{color:#e2e8f0!important;}
.stButton>button{background:rgba(0,212,170,0.1)!important;border:1px solid rgba(0,212,170,0.25)!important;color:#00d4aa!important;border-radius:8px!important;font-size:0.8rem!important;}
.stTextInput input{background:#0d1117!important;border:1px solid rgba(255,255,255,0.1)!important;color:#e2e8f0!important;border-radius:10px!important;}
.stTextInput input:focus{border-color:rgba(0,212,170,0.5)!important;}
.user-msg{background:rgba(0,212,170,0.08);border:1px solid rgba(0,212,170,0.15);border-radius:12px 12px 4px 12px;padding:12px 16px;margin-left:60px;color:#e2e8f0;font-size:0.875rem;line-height:1.6;}
.ai-msg{background:#0d1117;border:1px solid rgba(255,255,255,0.07);border-radius:12px 12px 12px 4px;padding:12px 16px;margin-right:60px;color:#e2e8f0;font-size:0.875rem;line-height:1.6;}
.msg-meta{font-size:0.65rem;color:#64748b;margin-top:4px;}
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

st.markdown("<h1 style='color:#e2e8f0;font-size:1.6rem;font-weight:700;margin-bottom:4px;'>AI Stock Assistant</h1>", unsafe_allow_html=True)
st.markdown("<div style='color:#64748b;font-size:0.8rem;margin-bottom:20px;'>Ask about any NSE/BSE stock, sector, or market condition</div>", unsafe_allow_html=True)

# Quick prompts
st.markdown("<div style='margin-bottom:12px;'>", unsafe_allow_html=True)
qp_cols = st.columns(4)
quick_prompts = ["Analyze RELIANCE", "Nifty outlook today", "Top IT stocks to watch", "FII activity this week"]
for i, qp in enumerate(quick_prompts):
    with qp_cols[i]:
        if st.button(qp, use_container_width=True, key=f"qp_{i}"):
            st.session_state.setdefault('messages', [])
            st.session_state.messages.append({"role": "user", "content": qp})
st.markdown("</div>", unsafe_allow_html=True)

# Init chat
if 'messages' not in st.session_state:
    st.session_state.messages = []

AI_RESPONSES = {
    "reliance": "**RELIANCE** is showing strong bullish momentum. Q4 FY26 results beat estimates with Jio revenue up 12% YoY and retail segment delivering record margins. Key support: ₹2,880 · Resistance: ₹3,050. AI Sentiment: **Bullish (82%)**. Recommendation: Hold / Accumulate on dips.",
    "tcs": "**TCS** continues to outperform the IT index. US deal pipeline is strong with $2.4B in large deal wins. Trading near all-time highs. Key levels: support ₹3,980, resistance ₹4,280. Sentiment: **Bullish (78%)**.",
    "nifty": "**Nifty 50** is in a strong uptrend at 24,762. FII buying ₹2,847 Cr today. Positive market breadth — advances outnumber declines 3:1. Key levels: support 24,400, resistance 25,000. Short-term outlook: **Bullish**.",
    "it": "Top IT stocks to watch: **INFY** (strongest momentum, +3.1%), **TCS** (large deal wins), **HCLTECH** (margin recovery story), **WIPRO** (restructuring upside). Sector sentiment is **Bullish (78%)** driven by US demand recovery.",
    "fii": "FII activity this week: Net buying of **₹12,480 Cr** over 5 sessions. Heaviest buying in IT (+₹4,200 Cr) and Energy (+₹3,100 Cr). Selling in PSU Banks (-₹1,240 Cr). Sustained FII inflows are a positive signal for market direction.",
    "default": ["The Nifty 50 is in a strong uptrend with 73% of top stocks showing positive momentum. FII inflows remain supportive. Key risk: US Fed rate decision next week.",
                "Sector rotation is favoring IT and Energy. Banking faces near-term NIM compression but long-term outlook remains positive. Watch for RBI's next MPC minutes.",
                "My sentiment model signals **Bullish** across 47 of 50 Nifty stocks. RSI is at 62 — elevated but not overbought. Recommended action: Stay invested, tighten stop-losses.",
                "Market breadth is strong — 1,840 advances vs 780 declines on NSE. Mid-cap and small-cap indices outperforming large-caps. Risk-on sentiment prevailing."]
}

def get_ai_response(msg):
    m = msg.lower()
    if 'reliance' in m: return AI_RESPONSES['reliance']
    if 'tcs' in m: return AI_RESPONSES['tcs']
    if 'nifty' in m or 'market' in m: return AI_RESPONSES['nifty']
    if 'it ' in m or 'infosys' in m or 'infy' in m: return AI_RESPONSES['it']
    if 'fii' in m: return AI_RESPONSES['fii']
    idx = len(st.session_state.messages) % len(AI_RESPONSES['default'])
    return AI_RESPONSES['default'][idx]

# Display messages
for msg in st.session_state.messages:
    if msg['role'] == 'user':
        st.markdown(f"<div style='display:flex;justify-content:flex-end;margin-bottom:12px;'><div class='user-msg'>{msg['content']}</div></div>", unsafe_allow_html=True)
        st.markdown("<div class='msg-meta' style='text-align:right;'>You</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='display:flex;margin-bottom:12px;gap:10px;'><div style='width:28px;height:28px;border-radius:50%;background:rgba(0,212,170,0.12);display:grid;place-items:center;font-size:0.6rem;font-weight:700;color:#00d4aa;flex-shrink:0;'>AI</div><div class='ai-msg'>{msg['content']}</div></div>", unsafe_allow_html=True)

# Chat input
st.markdown("<br>", unsafe_allow_html=True)
with st.form("chat_form", clear_on_submit=True):
    col_inp, col_send = st.columns([8, 1])
    with col_inp:
        user_input = st.text_input("", placeholder="Ask about any stock, sector or market condition...", label_visibility="collapsed")
    with col_send:
        submitted = st.form_submit_button("Send ➤", use_container_width=True)

if submitted and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.spinner("IntelStock AI is thinking..."):
        time.sleep(0.6)
    response = get_ai_response(user_input)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# Welcome state
if not st.session_state.messages:
    st.markdown("""
    <div style='text-align:center;padding:48px 20px;'>
      <div style='font-size:2.5rem;margin-bottom:12px;'>🤖</div>
      <div style='font-size:1rem;font-weight:600;color:#64748b;'>Ask me anything about Indian markets</div>
      <div style='font-size:0.8rem;color:#334155;margin-top:8px;'>Try: "Analyze RELIANCE" · "Nifty outlook" · "Top IT stocks"</div>
    </div>
    """, unsafe_allow_html=True)
