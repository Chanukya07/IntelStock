"""IntelStock — Main Streamlit entry point."""
import os
import sys
import streamlit as st
import plotly.graph_objects as go

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.market_data_service import MarketDataService
from frontend.sidebar import inject_styles, render_sidebar

st.set_page_config(
    page_title="IntelStock",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_styles()

st.markdown("""
<style>
.intel-card h3{color:#e2e8f0;font-size:0.875rem;font-weight:600;margin-bottom:4px;}
.intel-card .sub{color:#64748b;font-size:0.75rem;margin-bottom:16px;}
.ticker-wrap{background:#0d1117;border-bottom:1px solid rgba(255,255,255,0.07);padding:8px 0;overflow:hidden;white-space:nowrap;margin-bottom:24px;}
.ticker-content{display:inline-block;animation:ticker 30s linear infinite;font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#64748b;}
.ticker-content .up{color:#34d399;}
.ticker-content .dn{color:#f87171;}
@keyframes ticker{0%{transform:translateX(100vw)}100%{transform:translateX(-100%)}}
.live-dot{display:inline-block;width:7px;height:7px;background:#f87171;border-radius:50%;margin-right:6px;animation:pulse-r 1.5s infinite;}
.cached-dot{display:inline-block;width:7px;height:7px;background:#64748b;border-radius:50%;margin-right:6px;}
@keyframes pulse-r{0%,100%{opacity:1}50%{opacity:0.3}}
</style>
""", unsafe_allow_html=True)

render_sidebar()

# ── Data ──────────────────────────────────────────────────────────────────────
# Only symbols with a real MarketProfile are tracked here: MarketDataService
# synthesises a "<SYM> Holdings" profile for anything else, which offline would be
# more fictional than showing fewer rows.
TRACKED = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "WIPRO"]


@st.cache_resource(show_spinner=False)
def _market() -> MarketDataService:
    return MarketDataService()


@st.cache_data(ttl=60, show_spinner=False)
def _load_indices() -> dict:
    try:
        return _market().fetch_index_values()
    except Exception:  # network/parse failures must not blank the landing page
        return {}


@st.cache_data(ttl=60, show_spinner=False)
def _load_quotes() -> list[dict]:
    quotes = []
    for sym in TRACKED:
        try:
            quotes.append(_market().fetch_live_quote(sym))
        except Exception:
            continue
    return quotes


@st.cache_data(ttl=60, show_spinner=False)
def _load_sectors() -> list[dict]:
    try:
        return _market().fetch_sector_performance()
    except Exception:
        return []


idx = _load_indices()
quotes = _load_quotes()
sectors = _load_sectors()

# Same live/cached convention as pages/overview.py.
badge = lambda s: " 🟢 LIVE" if s == "live" else " ⚪ cached"


def ival(key, field, default=0.0):
    return idx.get(key, {}).get(field, default)


statuses = [d.get("status") for d in idx.values()] + [q.get("status") for q in quotes]
all_live = bool(statuses) and all(s == "live" for s in statuses)

# ── Ticker ────────────────────────────────────────────────────────────────────
ticker_items = []
for q in quotes:
    cls = "up" if q["change_pct"] >= 0 else "dn"
    arrow = "▲" if q["change_pct"] >= 0 else "▼"
    ticker_items.append(
        f'<span class="{cls}">{arrow} {q["symbol"]} {q["price"]:,.2f} ({q["change_pct"]:+.2f}%)</span>'
    )
for key, label in (("NIFTY", "NIFTY"), ("SENSEX", "SENSEX")):
    if key in idx:
        pct = ival(key, "change_pct")
        cls = "up" if pct >= 0 else "dn"
        arrow = "▲" if pct >= 0 else "▼"
        ticker_items.append(
            f'<span class="{cls}">{arrow} {label} {ival(key, "value"):,.0f} ({pct:+.2f}%)</span>'
        )
ticker_html = " &nbsp;·&nbsp; ".join(ticker_items) or '<span>Market data unavailable</span>'
st.markdown(
    f'<div class="ticker-wrap"><div class="ticker-content">&nbsp;&nbsp;&nbsp;{ticker_html}</div></div>',
    unsafe_allow_html=True,
)

# ── Header ────────────────────────────────────────────────────────────────────
col_title, col_live = st.columns([6, 1])
with col_title:
    st.markdown("<h1 style='color:#e2e8f0;font-size:1.6rem;font-weight:700;letter-spacing:-0.02em;margin:0;'>Dashboard</h1>", unsafe_allow_html=True)
with col_live:
    if all_live:
        st.markdown("<div style='text-align:right;padding-top:8px;'><span class='live-dot'></span><span style='font-size:0.7rem;color:#f87171;font-weight:600;'>LIVE</span></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align:right;padding-top:8px;'><span class='cached-dot'></span><span style='font-size:0.7rem;color:#64748b;font-weight:600;'>CACHED</span></div>", unsafe_allow_html=True)
sub = "NSE · BSE · Real-time intelligence" if all_live else "NSE · BSE · Last cached snapshot — live feed unavailable"
st.markdown(f"<div style='color:#64748b;font-size:0.8rem;margin-bottom:24px;'>{sub}</div>", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
# Portfolio P&L and an "AI sentiment" score used to sit here as literals. Both need
# a user/holdings context this anonymous landing page does not have, so the row now
# only carries index values the service can actually source.
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("NIFTY 50", f"{ival('NIFTY', 'value'):,.0f}",
              f"{ival('NIFTY', 'change'):+,.0f} ({ival('NIFTY', 'change_pct'):+.2f}%){badge(ival('NIFTY', 'status', ''))}")
with c2:
    st.metric("SENSEX", f"{ival('SENSEX', 'value'):,.0f}",
              f"{ival('SENSEX', 'change'):+,.0f} ({ival('SENSEX', 'change_pct'):+.2f}%){badge(ival('SENSEX', 'status', ''))}")
with c3:
    st.metric("NIFTY BANK", f"{ival('BANKNIFTY', 'value'):,.0f}",
              f"{ival('BANKNIFTY', 'change'):+,.0f} ({ival('BANKNIFTY', 'change_pct'):+.2f}%){badge(ival('BANKNIFTY', 'status', ''))}")
with c4:
    st.metric("INDIA VIX", f"{ival('INDIAVIX', 'value'):.2f}",
              f"{ival('INDIAVIX', 'change'):+.2f} ({ival('INDIAVIX', 'change_pct'):+.2f}%){badge(ival('INDIAVIX', 'status', ''))}",
              delta_color="inverse")

st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)

# ── Chart + Movers ────────────────────────────────────────────────────────────
col_chart, col_movers = st.columns([2, 1])

with col_chart:
    idx_status = ival("NIFTY", "status", "")
    st.markdown(
        f"<div class='intel-card'><h3>Indices — Session Change</h3><div class='sub'>Open to last print{badge(idx_status)}</div>",
        unsafe_allow_html=True,
    )
    # MarketDataService exposes no intraday tick history, so the old minute-by-minute
    # line was pure invention. Session change per index is data we actually have.
    order = [("NIFTY", "Nifty 50"), ("SENSEX", "Sensex"), ("BANKNIFTY", "Bank Nifty"), ("INDIAVIX", "India VIX")]
    labels = [name for key, name in order if key in idx]
    changes = [ival(key, "change_pct") for key, _ in order if key in idx]
    if labels:
        fig = go.Figure(go.Bar(
            x=changes, y=labels, orientation="h",
            marker_color=['#34d399' if c >= 0 else '#f87171' for c in changes],
            text=[f"{c:+.2f}%" for c in changes],
            textposition='outside', textfont=dict(size=11, color='#e2e8f0'),
            hovertemplate='<b>%{y}</b><br>%{x:+.2f}%<extra></extra>',
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            height=280, margin=dict(l=0, r=24, t=8, b=0),
            xaxis=dict(showgrid=False, zeroline=True, zerolinecolor='rgba(255,255,255,0.12)', visible=False),
            yaxis=dict(showgrid=False, color='#64748b', tickfont=dict(size=11)),
            showlegend=False,
        )
        st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
    else:
        st.info("Index data unavailable.")
    st.markdown("</div>", unsafe_allow_html=True)

with col_movers:
    mv_status = "live" if quotes and all(q.get("status") == "live" for q in quotes) else "cached"
    st.markdown(
        f"<div class='intel-card'><h3>Top Movers</h3><div class='sub'>{len(quotes)} tracked NSE symbols{badge(mv_status)}</div>",
        unsafe_allow_html=True,
    )
    movers = sorted(quotes, key=lambda q: q["change_pct"], reverse=True)
    if not movers:
        st.info("Quote data unavailable.")
    for m in movers:
        up = m["change_pct"] >= 0
        color = "#34d399" if up else "#f87171"
        arrow = "▲" if up else "▼"
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;padding:10px;border-radius:8px;margin-bottom:4px;border:1px solid rgba(255,255,255,0.05);">
          <div style="width:36px;height:36px;border-radius:8px;background:#111820;border:1px solid rgba(255,255,255,0.07);display:grid;place-items:center;font-size:0.55rem;font-weight:700;color:#64748b;">{m['symbol'][:3]}</div>
          <div style="flex:1;"><div style="font-size:0.82rem;font-weight:600;color:#e2e8f0;">{m['symbol']}</div><div style="font-size:0.7rem;color:#64748b;">{m['sector']}</div></div>
          <div style="text-align:right;"><div style="font-size:0.82rem;font-weight:600;color:#e2e8f0;font-family:'JetBrains Mono',monospace;">₹{m['price']:,.2f}</div><div style="font-size:0.72rem;font-weight:600;color:{color};">{arrow} {m['change_pct']:+.2f}%</div></div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── Sector bar chart ─────────────────────────────────────────────────────────
sec_status = "live" if sectors and all(s.get("status") == "live" for s in sectors) else "cached"
st.markdown(
    f"<div class='intel-card'><h3>Sector Performance</h3><div class='sub'>Session change by Nifty sector index{badge(sec_status)}</div>",
    unsafe_allow_html=True,
)
if sectors:
    # Service returns "Nifty IT" etc; strip the prefix to keep the short x-axis labels.
    sec_names = [s["name"].replace("Nifty ", "") for s in sectors]
    sec_changes = [s["change_pct"] for s in sectors]
    colors = ['#34d399' if c > 0 else '#f87171' for c in sec_changes]
    fig2 = go.Figure(go.Bar(
        x=sec_names, y=sec_changes, marker_color=colors,
        text=[f"{c:+.2f}%" for c in sec_changes],
        textposition='outside', textfont=dict(size=11, color='#e2e8f0')
    ))
    fig2.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=200, margin=dict(l=0, r=0, t=24, b=0),
        xaxis=dict(showgrid=False, color='#64748b', tickfont=dict(size=11)),
        yaxis=dict(showgrid=False, visible=False),
        showlegend=False,
    )
    st.plotly_chart(fig2, width="stretch", config={'displayModeBar': False})
else:
    st.info("Sector data unavailable.")
st.markdown("</div>", unsafe_allow_html=True)
