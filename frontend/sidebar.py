"""Shared sidebar for IntelStock Streamlit pages."""

from __future__ import annotations

import streamlit as st


SIDEBAR_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300..700&family=JetBrains+Mono:wght@400;500&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;}
#MainMenu,footer,header{visibility:hidden;}
.stApp{background:#080c12!important;}
section[data-testid="stSidebarNav"], nav[data-testid="stSidebarNav"] {display:none !important;}
[data-testid="stSidebar"]{background:#0d1117!important;border-right:1px solid rgba(255,255,255,0.07)!important;}
[data-testid="stSidebar"] *{color:#e2e8f0!important;}
</style>
"""


def inject_styles() -> None:
    st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            """
            <div style="padding:8px 0 24px;">
              <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                  <rect width="32" height="32" rx="8" fill="rgba(0,212,170,0.12)"/>
                  <path d="M8 22 L12 16 L16 19 L20 12 L24 14" stroke="#00d4aa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <circle cx="24" cy="14" r="2.5" fill="#00d4aa"/>
                </svg>
                <span style="font-size:1.2rem;font-weight:700;color:#e2e8f0;">Intel<span style="color:#00d4aa;">Stock</span></span>
              </div>
              <div style="font-size:0.7rem;color:#64748b;letter-spacing:0.05em;">AI STOCK INTELLIGENCE</div>
            </div>
            <hr style="border-color:rgba(255,255,255,0.07);margin-bottom:16px;">
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div style='font-size:0.65rem;color:#334155;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;'>NAVIGATION</div>",
            unsafe_allow_html=True,
        )
        st.page_link("dashboard.py", label="🏠  Home")
        st.page_link("pages/overview.py", label="📊  Overview")
        st.page_link("pages/stock_research.py", label="🔍  Stock Research")
        st.page_link("pages/sentiment_dashboard.py", label="🧠  Sentiment")
        st.page_link("pages/portfolio_analyzer.py", label="💼  Portfolio")
        st.page_link("pages/ai_chat.py", label="💬  AI Chat")

        st.markdown("<hr style='border-color:rgba(255,255,255,0.07);margin:16px 0;'>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="display:flex;align-items:center;gap:10px;padding:4px 0;">
              <div style="width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#00d4aa,#60a5fa);display:grid;place-items:center;font-size:0.65rem;font-weight:700;color:#fff;">CK</div>
              <div>
                <div style="font-size:0.8rem;font-weight:600;color:#e2e8f0;">Chanukya</div>
                <div style="font-size:0.7rem;color:#64748b;">Pro Trader</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )