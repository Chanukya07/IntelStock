"""Portfolio Analyzer page with advanced analytics."""
import csv
import io
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
    """Fetch portfolio holdings from backend.

    GET /portfolio answers with an envelope — {"user_id":…, "portfolio":[…],
    "total_value":…} — so the holdings list has to be unwrapped here. Returning
    the raw body made the render loop below slice a dict and blow up the page.
    """
    try:
        response = requests.get(f"{API_ROOT}/portfolio", params={"user_id": USER_ID}, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, dict):
            holdings = payload.get("portfolio") or []
            return (holdings if isinstance(holdings, list) else []), float(payload.get("total_value") or 0)
        return (payload or []), 0.0
    except Exception as e:
        st.warning(f"Failed to load holdings: {str(e)}")
        return [], 0.0


def holdings_to_csv(holdings):
    """Serialise holdings to CSV text for the export button."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["symbol", "quantity", "avg_price", "current_price", "market_value", "gain_loss", "return_pct"])
    for holding in holdings:
        qty = holding.get("quantity", 0)
        avg_price = holding.get("avg_price", 0)
        current_price = holding.get("current_price", 0)
        invested = qty * avg_price
        market_value = holding.get("market_value", qty * current_price)
        gain_loss = holding.get("gain_loss", market_value - invested)
        writer.writerow([
            holding.get("symbol", "N/A"),
            qty,
            round(avg_price, 2),
            round(current_price, 2),
            round(market_value, 2),
            round(gain_loss, 2),
            round(gain_loss / invested * 100, 2) if invested > 0 else 0.0,
        ])
    return buffer.getvalue()


def render_metric(label, value, status_text=None, suffix="", fallback_delta=""):
    """Render a metric, or an explicit em dash when it could not be computed.

    The analytics service returns None for any metric it cannot honestly
    derive (rather than a plausible-looking placeholder), so every consumer
    has to handle None. Formatting None with :.2f raises TypeError and takes
    the whole page down, so the None branch is the important one here.
    """
    if value is None:
        st.metric(label, "—", delta=status_text or "Unavailable", delta_color="off")
    else:
        st.metric(label, f"{value:.2f}{suffix}", delta=fallback_delta, delta_color="off")


analytics = fetch_analytics()
portfolio, portfolio_total_value = fetch_portfolio()

if analytics:
    metrics = analytics.get("metrics", {})
    # Per-metric provenance: lets the UI say *why* a value is missing.
    status = metrics.get("metric_status", {}) or {}

    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_val = metrics.get("total_value", 0)
        # No literal "+": Streamlit colours the delta by sign, and hardcoding it
        # rendered losses as "+-1.2k".
        st.metric("Total Value", f"₹{total_val/1e5:.2f}L", delta=f"{metrics.get('total_gain_loss', 0)/1e4:.1f}k")
    with col2:
        ret = metrics.get("total_return_pct", 0)
        st.metric("Total Return", f"{ret:.2f}%", delta="Since inception", delta_color="off")
    with col3:
        render_metric(
            "XIRR", metrics.get("xirr"), status.get("xirr"),
            suffix="%", fallback_delta="Annualized",
        )
    with col4:
        st.metric("Invested", f"₹{metrics.get('total_invested', 0)/1e5:.2f}L", delta="Base amount", delta_color="off")

    st.markdown("<br>", unsafe_allow_html=True)

    # Risk metrics
    st.markdown("<h3 style='color:#e2e8f0;'>Risk Metrics</h3>", unsafe_allow_html=True)
    if not metrics.get("risk_metrics_available", False):
        st.caption(
            "Volatility, Sharpe and max drawdown are time-series measures and need "
            "price history, which isn't recorded yet — they're shown as — rather "
            "than filled with an estimate."
        )
    risk_col1, risk_col2, risk_col3, risk_col4 = st.columns(4)
    with risk_col1:
        render_metric(
            "Volatility", metrics.get("volatility"), status.get("volatility"),
            suffix="%", fallback_delta="Annual standard deviation",
        )
    with risk_col2:
        render_metric(
            "Sharpe Ratio", metrics.get("sharpe_ratio"), status.get("sharpe_ratio"),
            fallback_delta="Risk-adjusted return",
        )
    with risk_col3:
        render_metric(
            "Max Drawdown", metrics.get("max_drawdown"), status.get("max_drawdown"),
            suffix="%", fallback_delta="Worst peak-to-trough",
        )
    with risk_col4:
        # Concentration is cross-sectional, so it is always computable.
        conc = metrics.get("concentration_risk") or 0
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
                        # "Top" is only relative — an all-red portfolio still fills
                        # this tab, so the sign has to follow the number.
                        st.markdown(f"""
                        <div style='display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);'>
                            <span style='color:#e2e8f0;font-weight:600;'>{item.get("symbol", "N/A")}</span>
                            <span style='color:#34d399;font-weight:600;'>{ret_pct:+.2f}%</span>
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

    if portfolio:
        st.markdown(
            f"<div style='color:#64748b;font-size:0.78rem;margin-bottom:12px;'>"
            f"{len(portfolio)} position(s) · Market value ₹{portfolio_total_value/1e5:.2f}L"
            f"{' · showing top 10, export CSV for all' if len(portfolio) > 10 else ''}</div>",
            unsafe_allow_html=True,
        )
        for holding in portfolio[:10]:
            sym = holding.get("symbol", "N/A")
            qty = holding.get("quantity", 0)
            avg_price = holding.get("avg_price", 0)
            current_price = holding.get("current_price", 0)
            invested = qty * avg_price
            # The backend already marks each row to market; recomputing here would
            # let the page drift from the numbers in the downloaded statement.
            value = holding.get("market_value", qty * current_price)
            pnl = holding.get("gain_loss", value - invested)
            ret_pct = (pnl / invested * 100) if invested > 0 else 0

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
                <div style='font-size:0.75rem;font-weight:600;color:{pnl_color};'>{'+' if pnl >= 0 else '-'}₹{abs(pnl)/1e4:.1f}k ({ret_pct:+.2f}%)</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No holdings data available")
else:
    st.error("Unable to load portfolio analytics. Please check if the backend is running.")

# Report download section.
#
# The generated bytes live in session_state and the download_button is rendered
# unconditionally from there. Nesting it inside `if st.button(...)` meant the link
# existed for exactly one rerun and disappeared the moment the user touched
# anything — including the link itself.
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<h3 style='color:#e2e8f0;'>Download Reports</h3>", unsafe_allow_html=True)

report_col1, report_col2, report_col3, export_col = st.columns(4)


def generate_report(state_key, url, params, file_name, spinner_text, extra=None):
    """Fetch a report and stash (bytes, filename[, extra]) in session state."""
    with st.spinner(spinner_text):
        try:
            response = requests.get(url, params=params, timeout=REPORT_TIMEOUT)
            response.raise_for_status()
            st.session_state[state_key] = (response.content, file_name, extra)
        except Exception as e:
            # Drop any earlier report so a failed regeneration doesn't leave a
            # stale link sitting there looking fresh.
            st.session_state.pop(state_key, None)
            st.error(f"Report generation failed: {str(e)}")


with report_col1:
    if st.button("📄 Portfolio Report", use_container_width=True):
        generate_report(
            "portfolio_report",
            f"{API_BASE}/reports/portfolio",
            {"user_id": USER_ID},
            f"portfolio_report_{datetime.now().strftime('%Y%m%d')}.html",
            "Generating portfolio report...",
        )
    if st.session_state.get("portfolio_report"):
        data, file_name, _ = st.session_state["portfolio_report"]
        st.download_button(
            label="⬇️ Download HTML Report",
            data=data,
            file_name=file_name,
            mime="text/html",
            use_container_width=True,
            key="dl_portfolio_report",
        )

with report_col2:
    symbol_for_report = st.selectbox("Stock Report For:", ["RELIANCE", "TCS", "INFY", "WIPRO", "HDFCBANK"], label_visibility="collapsed")
    if st.button("📊 Stock Report", use_container_width=True):
        generate_report(
            "stock_report",
            f"{API_BASE}/reports/stock",
            {"symbol": symbol_for_report},
            f"{symbol_for_report}_report_{datetime.now().strftime('%Y%m%d')}.html",
            f"Generating {symbol_for_report} report...",
            extra=symbol_for_report,
        )
    stock_report = st.session_state.get("stock_report")
    # Only offer the file while it still matches the dropdown, otherwise switching
    # to TCS would hand the user a stale RELIANCE report.
    if stock_report and stock_report[2] == symbol_for_report:
        st.download_button(
            label="⬇️ Download HTML Report",
            data=stock_report[0],
            file_name=stock_report[1],
            mime="text/html",
            use_container_width=True,
            key="dl_stock_report",
        )

with report_col3:
    if st.button("🧠 Sentiment Report", use_container_width=True):
        generate_report(
            "sentiment_report",
            f"{API_BASE}/reports/sentiment",
            None,
            f"sentiment_report_{datetime.now().strftime('%Y%m%d')}.html",
            "Generating sentiment report...",
        )
    if st.session_state.get("sentiment_report"):
        data, file_name, _ = st.session_state["sentiment_report"]
        st.download_button(
            label="⬇️ Download HTML Report",
            data=data,
            file_name=file_name,
            mime="text/html",
            use_container_width=True,
            key="dl_sentiment_report",
        )

with export_col:
    # Holdings as CSV so the data can be reconciled in Excel/Sheets or fed into
    # capital-gains workings — an HTML report cannot be.
    if portfolio:
        st.download_button(
            label="📥 Holdings CSV",
            data=holdings_to_csv(portfolio),
            file_name=f"holdings_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
            key="dl_holdings_csv",
        )
    else:
        st.button("📥 Holdings CSV", use_container_width=True, disabled=True, help="No holdings to export")
