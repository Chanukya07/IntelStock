"""AI Chat page."""
import streamlit as st
import time

from backend.services.insight_service import InsightService

from frontend.sidebar import inject_styles, render_sidebar

st.set_page_config(page_title="AI Chat — IntelStock", layout="wide")

inject_styles()

st.markdown("""
<style>
.stButton>button{background:rgba(0,212,170,0.1)!important;border:1px solid rgba(0,212,170,0.25)!important;color:#00d4aa!important;border-radius:8px!important;font-size:0.8rem!important;}
.stTextInput input{background:#0d1117!important;border:1px solid rgba(255,255,255,0.1)!important;color:#e2e8f0!important;border-radius:10px!important;}
.stTextInput input:focus{border-color:rgba(0,212,170,0.5)!important;}
.user-msg{background:rgba(0,212,170,0.08);border:1px solid rgba(0,212,170,0.15);border-radius:12px 12px 4px 12px;padding:12px 16px;margin-left:60px;color:#e2e8f0;font-size:0.875rem;line-height:1.6;}
.ai-msg{background:#0d1117;border:1px solid rgba(255,255,255,0.07);border-radius:12px 12px 12px 4px;padding:12px 16px;margin-right:60px;color:#e2e8f0;font-size:0.875rem;line-height:1.6;}
.msg-meta{font-size:0.65rem;color:#64748b;margin-top:4px;}
</style>
""", unsafe_allow_html=True)

render_sidebar()

insight_service = InsightService()

st.markdown("<h1 style='color:#e2e8f0;font-size:1.6rem;font-weight:700;margin-bottom:4px;'>AI Stock Assistant</h1>", unsafe_allow_html=True)
st.markdown("<div style='color:#64748b;font-size:0.8rem;margin-bottom:20px;'>Ask about any NSE/BSE stock, sector, or market condition</div>", unsafe_allow_html=True)

# Quick prompts
st.markdown("<div style='margin-bottom:12px;'>", unsafe_allow_html=True)
qp_cols = st.columns(4)
quick_prompts = ["Analyze RELIANCE", "Nifty outlook today", "Top IT stocks to watch", "HDFC near-term view"]
for i, qp in enumerate(quick_prompts):
    with qp_cols[i]:
        if st.button(qp, width="stretch", key=f"qp_{i}"):
            st.session_state.setdefault('messages', [])
            st.session_state.messages.append({"role": "user", "content": qp})
st.markdown("</div>", unsafe_allow_html=True)

# Init chat
if 'messages' not in st.session_state:
    st.session_state.messages = []

def infer_symbol(msg: str) -> str:
    normalized = msg.upper()
    for symbol in ("RELIANCE", "TCS", "INFY", "WIPRO", "HDFC", "HDFCBANK", "NIFTY"):
        if symbol in normalized:
            return symbol
    if any(token in normalized for token in ("INDEX", "MARKET", "FII", "IT STOCKS", "SECTOR")):
        return "NIFTY"
    return "RELIANCE"


def build_ai_response(msg: str) -> dict[str, object]:
    symbol = infer_symbol(msg)
    report = insight_service.generate_report(symbol, msg)
    response_lines = [
        f"**{report['name']}** · {report['quote']['sentiment']} bias",
        report["summary"],
        f"Recommendation: **{report['recommendation']}**",
        f"Support / resistance: ₹{report['quote']['support']:,} / ₹{report['quote']['resistance']:,}",
    ]
    return {"symbol": symbol, "report": report, "content": "\n\n".join(response_lines)}

# Display messages
for msg in st.session_state.messages:
    if msg['role'] == 'user':
        st.markdown(f"<div style='display:flex;justify-content:flex-end;margin-bottom:12px;'><div class='user-msg'>{msg['content']}</div></div>", unsafe_allow_html=True)
        st.markdown("<div class='msg-meta' style='text-align:right;'>You</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='display:flex;margin-bottom:12px;gap:10px;'><div style='width:28px;height:28px;border-radius:50%;background:rgba(0,212,170,0.12);display:grid;place-items:center;font-size:0.6rem;font-weight:700;color:#00d4aa;flex-shrink:0;'>AI</div><div class='ai-msg'>{msg['content']}</div></div>", unsafe_allow_html=True)
        report = msg.get('report')
        if report:
            st.markdown(
                f"""
                <div style='display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:-4px 0 16px 38px;'>
                  <div class='intel-card' style='margin:0;padding:14px 16px;'><div style='font-size:0.7rem;color:#64748b;'>Confidence</div><div style='font-size:1.2rem;font-weight:700;color:#e2e8f0;'>{report['confidence']}</div></div>
                  <div class='intel-card' style='margin:0;padding:14px 16px;'><div style='font-size:0.7rem;color:#64748b;'>Signal</div><div style='font-size:1.2rem;font-weight:700;color:#e2e8f0;'>{report['sentiment']['label']}</div></div>
                  <div class='intel-card' style='margin:0;padding:14px 16px;'><div style='font-size:0.7rem;color:#64748b;'>Action</div><div style='font-size:1.0rem;font-weight:700;color:#e2e8f0;'>{report['recommendation']}</div></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# Chat input
st.markdown("<br>", unsafe_allow_html=True)
with st.form("chat_form", clear_on_submit=True):
    col_inp, col_send = st.columns([8, 1])
    with col_inp:
        user_input = st.text_input("", placeholder="Ask about any stock, sector or market condition...", label_visibility="collapsed")
    with col_send:
        submitted = st.form_submit_button("Send ➤", width="stretch")

if submitted and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.spinner("IntelStock AI is thinking..."):
        time.sleep(0.6)
    response = build_ai_response(user_input)
    st.session_state.messages.append({"role": "assistant", "content": response['content'], "report": response['report']})
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
