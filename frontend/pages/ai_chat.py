"""AI Chat page."""
import streamlit as st
import time
import requests
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from backend.services.chat_service import ChatService
from frontend.sidebar import inject_styles, render_sidebar

st.set_page_config(page_title="AI Chat — IntelStock", layout="wide")
inject_styles()

st.markdown(
    """<style>.stButton>button{background:rgba(0,212,170,0.1)!important;border:1px solid rgba(0,212,170,0.25)!important;color:#00d4aa!important;border-radius:8px!important;font-size:0.8rem!important;}
.stTextInput input{background:#0d1117!important;border:1px solid rgba(255,255,255,0.1)!important;color:#e2e8f0!important;border-radius:10px!important;}
.stTextInput input:focus{border-color:rgba(0,212,170,0.5)!important;}
.user-msg{background:rgba(0,212,170,0.08);border:1px solid rgba(0,212,170,0.15);border-radius:12px 12px 4px 12px;padding:12px 16px;margin-left:60px;color:#e2e8f0;font-size:0.875rem;line-height:1.6;}
.ai-msg{background:#0d1117;border:1px solid rgba(255,255,255,0.07);border-radius:12px 12px 12px 4px;padding:12px 16px;margin-right:60px;color:#e2e8f0;font-size:0.875rem;line-height:1.6;}
.msg-meta{font-size:0.65rem;color:#64748b;margin-top:4px;}</style>"""
    , unsafe_allow_html=True
)

render_sidebar()
chat_service = ChatService()

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
    response = chat_service.chat(msg)
    return {"symbol": symbol, "response": response, "content": response.get("message", "")}

# Display messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about stock analysis..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Analyzing..."):
            result = build_ai_response(prompt)
            full_response = result["content"]
            message_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
