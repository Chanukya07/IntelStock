"""Stock Research page."""
import streamlit as st
import numpy as np

from backend.services.insight_service import InsightService
from backend.services.market_data_service import MarketDataService
from frontend.sidebar import inject_styles, render_sidebar
from frontend.charts.price_chart import build_price_chart
from frontend.animations import inject_animations, animated_header, stat_badges

st.set_page_config(page_title="Stock Research — IntelStock", layout="wide")

inject_styles()
inject_animations()

st.markdown("""
<style>
.quick-chip{display:inline-block;border:1px solid rgba(255,255,255,0.08);border-radius:999px;padding:6px 12px;margin:0 8px 8px 0;color:#cbd5e1;font-size:0.74rem;}
</style>
""", unsafe_allow_html=True)

render_sidebar()

market_data_service = MarketDataService()
insight_service = InsightService()

animated_header("Stock Research", "Enter any NSE symbol for AI-powered analysis")

stat_badges("RELIANCE", "TCS", "INFY", "HDFC", "NIFTY")

col_in, col_btn = st.columns([3, 1])
with col_in:
    symbol = st.text_input("", placeholder="Enter NSE symbol (e.g. RELIANCE, TCS, INFY)", label_visibility="collapsed")
with col_btn:
    search = st.button("🔍  Analyze", width="stretch")

if symbol or search:
    sym = symbol.strip().upper()
    if sym:
        quote = market_data_service.fetch_live_quote(sym)
        report = insight_service.generate_report(sym)
        pnl_color = "#34d399" if quote["change_pct"] > 0 else "#f87171"
        sent_rgb = "52,211,153" if quote["sentiment"] == "Bullish" else "248,113,113" if quote["sentiment"] == "Bearish" else "100,116,139"
        sent_color = "#34d399" if quote["sentiment"] == "Bullish" else "#f87171" if quote["sentiment"] == "Bearish" else "#94a3b8"

        st.markdown(
            f"""
            <div style='animation:slideInUp 0.6s ease-out;display:flex;align-items:center;gap:16px;margin:20px 0 8px;'>
              <div>
                <div style='font-size:1.2rem;font-weight:700;color:#e2e8f0;animation:slideInLeft 0.5s ease-out;'>{quote['symbol']} <span style='font-size:0.9rem;font-weight:400;color:#64748b;'>· {quote['name']}</span></div>
                <div style='font-size:2rem;font-weight:700;color:#e2e8f0;font-family:"JetBrains Mono",monospace;animation:slideInLeft 0.7s ease-out;'>₹{quote['price']:,} <span style='font-size:1rem;color:{pnl_color};'>{'+' if quote['change_pct'] > 0 else ''}{quote['change_pct']}%</span></div>
              </div>
              <div style='margin-left:auto;background:rgba({sent_rgb},0.15);color:{sent_color};padding:6px 16px;border-radius:999px;font-weight:600;font-size:0.8rem;animation:scaleIn 0.5s ease-out;'>{quote['sentiment']} · {report['confidence']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='margin:20px 0;'></div>", unsafe_allow_html=True)
        k1, k2, k3, k4, k5 = st.columns(5)
        with k1:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Sector", quote["sector"])
            st.markdown("</div>", unsafe_allow_html=True)
        with k2:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Volume", quote["volume"])
            st.markdown("</div>", unsafe_allow_html=True)
        with k3:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Support", f"₹{quote['support']:,}")
            st.markdown("</div>", unsafe_allow_html=True)
        with k4:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Resistance", f"₹{quote['resistance']:,}")
            st.markdown("</div>", unsafe_allow_html=True)
        with k5:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Signal", quote["sentiment"])
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_chart, col_ai = st.columns([3, 2])

        with col_chart:
            st.markdown("<div class='intel-card-animated chart-container'><h3 style='color:#e2e8f0;margin-bottom:16px;'>📈 Price Chart — 1 Month</h3>", unsafe_allow_html=True)
            days = list(range(22))
            prices = [quote["price"] * (1 + 0.004 * i + 0.006 * np.sin(i * 0.5)) for i in days]
            prices = [round(p - 80 + 20 * np.random.rand(), 2) for p in prices]
            prices[-1] = quote["price"]
            fig = build_price_chart(
                timestamps=[str(d) for d in days],
                prices=prices,
                support=quote.get("support"),
                resistance=quote.get("resistance"),
                title=quote["symbol"]
            )
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        with col_ai:
            st.markdown(
                f"""
                <div class='intel-card-animated'>
                  <h3 style='color:#00d4aa;margin-bottom:12px;animation:slideInRight 0.5s ease-out;'>🤖 AI Analysis</h3>
                  <p style='color:#cbd5e1;font-size:0.85rem;line-height:1.7;animation:fadeIn 0.8s ease-out;'>{report['summary']}</p>
                  <p style='color:#e2e8f0;font-size:0.82rem;font-weight:600;margin-top:12px;animation:slideInRight 0.6s ease-out;'>Recommendation: <span style='color:#00d4aa;'>{report['recommendation']}</span></p>
                  <p style='color:#64748b;font-size:0.75rem;margin-top:8px;animation:slideInRight 0.7s ease-out;'>✨ Catalyst: {report['catalysts'][0]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
else:
    st.markdown("""
    <div style='text-align:center;padding:60px 20px;color:#334155;'>
      <div style='font-size:3rem;margin-bottom:16px;'>🔍</div>
      <div style='font-size:1rem;font-weight:600;color:#64748b;'>Enter an NSE symbol to get started</div>
      <div style='font-size:0.8rem;color:#334155;margin-top:8px;'>Try: RELIANCE · TCS · HDFC · INFY · NIFTY</div>
    </div>
    """, unsafe_allow_html=True)
