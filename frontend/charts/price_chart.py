"""Plotly chart builders shared across dashboard pages.

Centralizing chart construction keeps the dark theme consistent and avoids
duplicating figure styling in every Streamlit page.
"""

from __future__ import annotations

import plotly.graph_objects as go

ACCENT = "#00d4aa"
BG = "#0d1117"
GRID = "rgba(255,255,255,0.06)"
TEXT = "#e2e8f0"


def _apply_dark_theme(fig: go.Figure, height: int = 360) -> go.Figure:
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=BG,
        font=dict(color=TEXT, family="Inter, sans-serif", size=12),
        margin=dict(l=40, r=20, t=30, b=30),
        height=height,
        xaxis=dict(gridcolor=GRID, zeroline=False),
        yaxis=dict(gridcolor=GRID, zeroline=False),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    return fig


def build_price_chart(timestamps: list[str], prices: list[float], support: float | None = None, resistance: float | None = None, title: str = "Price") -> go.Figure:
    """Build a styled line chart with optional support/resistance bands."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=timestamps,
            y=prices,
            mode="lines",
            line=dict(color=ACCENT, width=2),
            fill="tozeroy",
            fillcolor="rgba(0,212,170,0.08)",
            name=title,
        )
    )
    if support is not None:
        fig.add_hline(y=support, line_dash="dot", line_color="#64748b", annotation_text="Support")
    if resistance is not None:
        fig.add_hline(y=resistance, line_dash="dot", line_color="#f87171", annotation_text="Resistance")
    return _apply_dark_theme(fig)


def build_sentiment_gauge(bullish_score: float, label: str = "Sentiment") -> go.Figure:
    """Build a 0-1 gauge for a bullish sentiment score."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=round(bullish_score, 2),
            title={"text": label, "font": {"size": 14, "color": TEXT}},
            gauge={
                "axis": {"range": [0, 1], "tickcolor": TEXT},
                "bar": {"color": ACCENT},
                "bgcolor": BG,
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 0.4], "color": "rgba(248,113,113,0.25)"},
                    {"range": [0.4, 0.6], "color": "rgba(100,116,139,0.25)"},
                    {"range": [0.6, 1], "color": "rgba(0,212,170,0.25)"},
                ],
            },
        )
    )
    return _apply_dark_theme(fig, height=260)
