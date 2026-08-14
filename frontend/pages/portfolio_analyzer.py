"""Portfolio Analyzer page with advanced analytics."""
import streamlit as st
import plotly.graph_objects as go
import requests
from datetime import datetime

from frontend.animations import inject_animations, animated_header
from frontend.sidebar import inject_styles, render_sidebar
from frontend.api_config import API_ROOT, API_BASE, REQUEST_TIMEOUT, REPORT_TIMEOUT

st.set_page_config(page_title="Portfolio — IntelStock", layout="wide")

inject_styles()
inject_animations()

render_sidebar()

animated_header("Portfolio Analyzer", "Advanced analytics and risk metrics")

USER_ID = 1

@st.cache_data(ttl=300)
def fetch_analytics():
    """Fetch portfolio analytics from backend."""
    try:
        response = requests.get(f"{API_BASE}/portfolio/analytics", params={"user_id": USER_ID}, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to load analytics: {str(e)}")
        return None

@st.cache_data(ttl=300)
def fetch_portfolio():
    """Fetch portfolio holdings from backend."""
    try:
        response = requests.get(f"{API_ROOT}/portfolio", params={"user_id": USER_ID}, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.warning(f"Failed to load holdings: {str(e)}")
        return []

analytics = fetch_analytics()

if analytics:
    metrics = analytics.get("metrics", {})

    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_val = metrics.get("total_value", 0)
        st.metric("Total Value", f"₹{total_val/1e5:.2f}L", delta=f"+{metrics.get('total_gain_loss', 0)/1e4:.1f}k")
    with col2:
        ret = metrics.get("total_return_pct", 0)
        st.metric("Total Return", f"{ret:.2f}%", delta="Since inception", delta_color="off")
    with col3:
        xirr = metrics.get("xirr", 0)
        st.metric("XIRR", f"{xirr:.2f}%", delta="Annualized", delta_color="off")
    with col4:
        st.metric("Invested", f"₹{metrics.get('total_invested', 0)/1e5:.2f}L", delta="Base amount", delta_color="off")

    st.markdown("<br>", unsafe_allow_html=True)

    # Risk metrics
    st.markdown("<h3 style='color:#e2e8f0;'>Risk Metrics</h3>", unsafe_allow_html=True)
    risk_col1, risk_col2, risk_col3, risk_col4 = st.columns(4)
    with risk_col1:
        vol = metrics.get("volatility", 0)
        st.metric("Volatility", f"{vol:.2f}%", delta="Annual standard deviation", delta_color="off")
    with risk_col2:
        sharpe = metrics.get("sharpe_ratio", 0)
        st.metric("Sharpe Ratio", f"{sharpe:.2f}", delta="Risk-adjusted return", delta_color="off")
    with risk_col3:
        mdd = metrics.get("max_drawdown", 0)
        st.metric("Max Drawdown", f"{mdd:.2f}%", delta="Worst peak-to-trough", delta_color="off")
    with risk_col4:
        conc = metrics.get("concentration_risk", 0)
        st.metric("Concentration", f"{conc:.2f}%", delta="Herfindahl index", delta_color="off")

    st.markdown("<br>", unsafe_allow_html=True)

    col_sector, col_perf = st.columns([1, 1])

    # Sector allocation
    with col_sector:
        st.markdown("<div class='intel-card'><h3 style='color:#e2e8f0;margin-bottom:16px;'>Sector Allocation</h3>", unsafe_allow_html=True)
        sector_alloc = metrics.get("sector_allocation", {})
        if sector_alloc:
            sectors = list(sector_alloc.keys())
            values = list(sector_alloc.values())
            colors = ["#00d4aa", "#60a5fa", "#fbbf24", "#34d399", "#f87171", "#818cf8", "#ec4899"]
            fig = go.Figure(go.Pie(
                labels=sectors, values=values,
                hole=0.72,
                marker=dict(colors=colors[:len(sectors)], line=dict(color='#080c12', width=2)),
                textinfo='label+percent',
                textfont=dict(size=11, color='#e2e8f0'),
                hovertemplate='<b>%{label}</b><br>%{percent}<extra></extra>'
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                height=350,
                margin=dict(l=0, r=0, t=0, b=0),
                legend=dict(font=dict(color='#94a3b8', size=10), bgcolor='rgba(0,0,0,0)', yanchor="middle", y=0.5)
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No sector data available")
        st.markdown("</div>", unsafe_allow_html=True)

    # Top/Bottom performers
    with col_perf:
        st.markdown("<div class='intel-card'><h3 style='color:#e2e8f0;margin-bottom:16px;'>Performance</h3>", unsafe_allow_html=True)

        top_perf = metrics.get("top_performers", [])
        bottom_perf = metrics.get("bottom_performers", [])

        if top_perf or bottom_perf:
            perf_tab1, perf_tab2 = st.tabs(["🚀 Top Performers", "📉 Bottom Performers"])

            with perf_tab1:
                if top_perf:
                    for item in top_perf[:5]:
                        ret_pct = item.get("return_pct", 0)
                        st.markdown(f"""
                        <div style='display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);'>
                            <span style='color:#e2e8f0;font-weight:600;'>{item.get("symbol", "N/A")}</span>
                            <span style='color:#34d399;font-weight:600;'>+{ret_pct:.2f}%</span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No top performers")

            with perf_tab2:
                if bottom_perf:
                    for item in bottom_perf[:5]:
                        ret_pct = item.get("return_pct", 0)
                        st.markdown(f"""
                        <div style='display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);'>
                            <span style='color:#e2e8f0;font-weight:600;'>{item.get("symbol", "N/A")}</span>
                            <span style='color:#f87171;font-weight:600;'>{ret_pct:.2f}%</span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No bottom performers")
        else:
            st.info("No performance data available")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Holdings
    st.markdown("<h3 style='color:#e2e8f0;'>Holdings</h3>", unsafe_allow_html=True)
    portfolio = fetch_portfolio()

    if portfolio:
        for holding in portfolio[:10]:
            sym = holding.get("symbol", "N/A")
            qty = holding.get("quantity", 0)
            avg_price = holding.get("avg_price", 0)
            current_price = holding.get("current_price", 0)
            value = qty * current_price
            pnl = value - (qty * avg_price)
            ret_pct = (pnl / (qty * avg_price) * 100) if qty * avg_price > 0 else 0

            pnl_color = "#34d399" if pnl >= 0 else "#f87171"
            bar_pct = min(abs(ret_pct) * 2, 100)

            st.markdown(f"""
            <div style='display:flex;align-items:center;gap:12px;padding:12px;border:1px solid rgba(255,255,255,0.05);border-radius:8px;margin-bottom:8px;'>
              <div style='width:40px;height:40px;border-radius:8px;background:rgba(0,212,170,0.1);display:grid;place-items:center;font-size:0.6rem;font-weight:700;color:#00d4aa;flex-shrink:0;'>{sym[:4]}</div>
              <div style='flex:1;min-width:0;'>
                <div style='font-size:0.85rem;font-weight:600;color:#e2e8f0;'>{sym}</div>
                <div style='font-size:0.72rem;color:#64748b;'>{qty} shares · Avg ₹{avg_price:.2f}</div>
                <div style='height:4px;background:rgba(255,255,255,0.06);border-radius:2px;margin-top:6px;overflow:hidden;'>
                  <div style='height:100%;width:{bar_pct}%;background:{pnl_color};border-radius:2px;'></div>
                </div>
              </div>
              <div style='text-align:right;'>
                <div style='font-size:0.85rem;font-weight:600;color:#e2e8f0;font-family:"JetBrains Mono",monospace;'>₹{value/1e5:.2f}L</div>
                <div style='font-size:0.75rem;font-weight:600;color:{pnl_color};'>+₹{pnl/1e4:.1f}k ({ret_pct:.2f}%)</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No holdings data available")
else:
    st.error("Unable to load portfolio analytics. Please check if the backend is running.")

# Report download section
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<h3 style='color:#e2e8f0;'>Download Reports</h3>", unsafe_allow_html=True)

report_col1, report_col2, report_col3 = st.columns(3)

with report_col1:
    if st.button("📄 Portfolio Report", use_container_width=True):
        with st.spinner("Generating portfolio report..."):
            try:
                response = requests.get(f"{API_BASE}/reports/portfolio", params={"user_id": USER_ID}, timeout=REPORT_TIMEOUT)
                response.raise_for_status()
                st.download_button(
                    label="⬇️ Download HTML Report",
                    data=response.content,
                    file_name=f"portfolio_report_{datetime.now().strftime('%Y%m%d')}.html",
                    mime="text/html",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"Report generation failed: {str(e)}")

with report_col2:
    symbol_for_report = st.selectbox("Stock Report For:", ["RELIANCE", "TCS", "INFY", "WIPRO", "HDFCBANK"], label_visibility="collapsed")
    if st.button("📊 Stock Report", use_container_width=True):
        with st.spinner(f"Generating {symbol_for_report} report..."):
            try:
                response = requests.get(f"{API_BASE}/reports/stock", params={"symbol": symbol_for_report}, timeout=REPORT_TIMEOUT)
                response.raise_for_status()
                st.download_button(
                    label="⬇️ Download HTML Report",
                    data=response.content,
                    file_name=f"{symbol_for_report}_report_{datetime.now().strftime('%Y%m%d')}.html",
                    mime="text/html",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"Report generation failed: {str(e)}")

with report_col3:
    if st.button("🧠 Sentiment Report", use_container_width=True):
        with st.spinner("Generating sentiment report..."):
            try:
                response = requests.get(f"{API_BASE}/reports/sentiment", timeout=REPORT_TIMEOUT)
                response.raise_for_status()
                st.download_button(
                    label="⬇️ Download HTML Report",
                    data=response.content,
                    file_name=f"sentiment_report_{datetime.now().strftime('%Y%m%d')}.html",
                    mime="text/html",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"Report generation failed: {str(e)}")
