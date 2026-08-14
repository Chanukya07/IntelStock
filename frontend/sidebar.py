"""Shared sidebar for IntelStock Streamlit pages."""

from __future__ import annotations

import streamlit as st


SIDEBAR_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300..700&family=JetBrains+Mono:wght@400;500&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;}
#MainMenu,footer{visibility:hidden;}
header{background:transparent!important;}
.stApp{background:#080c12!important;}
section[data-testid="stSidebarNav"], nav[data-testid="stSidebarNav"] {display:none !important;}
[data-testid="stSidebar"]{background:#0d1117!important;border-right:1px solid rgba(255,255,255,0.07)!important;}
[data-testid="stSidebar"] *{color:#e2e8f0!important;}
[data-testid="collapsedControl"] {background-color:#0d1117!important;border-right:1px solid rgba(255,255,255,0.07)!important;}
[data-testid="collapsedControl"] button, [data-testid="collapsedControl"] svg {color:#64748b!important;stroke:#64748b!important;}
[data-testid="collapsedControl"]:hover button, [data-testid="collapsedControl"]:hover svg {color:#00d4aa!important;stroke:#00d4aa!important;}
[data-testid="stSidebar"] [data-testid="stPageLink"] a {
  display:flex!important;align-items:center!important;gap:10px!important;
  padding:9px 16px!important;border-radius:8px!important;margin:2px 8px!important;
  font-size:0.85rem!important;font-weight:500!important;color:#94a3b8!important;
  text-decoration:none!important;transition:all 180ms ease!important;
  background:transparent!important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {background:rgba(255,255,255,0.05)!important;color:#e2e8f0!important;}
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] {
  background:rgba(0,212,170,0.1)!important;color:#00d4aa!important;
  border:1px solid rgba(0,212,170,0.2)!important;
}
[data-testid="metric-container"]{background:#0d1117;border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:20px;}
[data-testid="stMetricValue"]{font-family:'JetBrains Mono',monospace!important;font-size:1.4rem!important;font-weight:700!important;color:#e2e8f0!important;}
[data-testid="stMetricLabel"]{color:#64748b!important;font-size:0.75rem!important;}
[data-testid="stMetricDelta"]{font-size:0.75rem!important;}
.intel-card{background:#0d1117;border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:20px 24px;margin-bottom:16px;}
.stButton>button{background:rgba(0,212,170,0.1)!important;border:1px solid rgba(0,212,170,0.3)!important;color:#00d4aa!important;border-radius:8px!important;font-weight:600!important;transition:all 0.2s ease!important;}
.stButton>button:hover{background:rgba(0,212,170,0.2)!important;border-color:#00d4aa!important;}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:#64748b!important;border-bottom:2px solid transparent!important;}
.stTabs [aria-selected="true"]{color:#00d4aa!important;border-bottom-color:#00d4aa!important;}
.stTextInput>div>div>input,.stSelectbox>div>div{background:#0d1117!important;border:1px solid rgba(255,255,255,0.1)!important;color:#e2e8f0!important;border-radius:8px!important;}
.stTextInput>div>div>input:focus{border-color:rgba(0,212,170,0.5)!important;box-shadow:0 0 0 3px rgba(0,212,170,0.12)!important;}
.stDataFrame{border-radius:12px!important;overflow:hidden!important;}
/* Mobile optimizations */
@media (max-width: 768px) {
  [data-testid="stSidebar"]{width:100%!important;min-width:100%!important;}
  .element-container{padding:0 4px!important;}
  [data-testid="metric-container"]{padding:12px!important;}
  [data-testid="stMetricValue"]{font-size:1.1rem!important;}
  .intel-card{padding:12px 16px!important;}
}
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
        st.page_link("pages/alerts.py", label="🔔  Alerts")

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