"""Animated UI components and transitions for IntelStock dashboards."""

import streamlit as st

ANIMATIONS_CSS = """
<style>
@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
}

@keyframes glow {
  0%, 100% {
    box-shadow: 0 0 5px rgba(0,212,170,0.3);
  }
  50% {
    box-shadow: 0 0 15px rgba(0,212,170,0.6);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-8px);
  }
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.animated-card {
  animation: slideInUp 0.6s ease-out;
}

.metric-card {
  animation: scaleIn 0.5s ease-out;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,212,170,0.2);
}

.metric-highlight {
  animation: pulse 2s ease-in-out infinite;
}

.chart-container {
  animation: fadeIn 0.8s ease-out;
}

.header-title {
  animation: slideInLeft 0.5s ease-out;
}

.header-subtitle {
  animation: slideInLeft 0.7s ease-out;
}

.intel-card-animated {
  background:#0d1117;
  border:1px solid rgba(255,255,255,0.07);
  border-radius:12px;
  padding:20px 24px;
  margin-bottom:16px;
  animation: slideInUp 0.6s ease-out;
  transition: all 0.3s ease;
}

.intel-card-animated:hover {
  border-color: rgba(0,212,170,0.3);
  box-shadow: 0 8px 32px rgba(0,212,170,0.1);
  transform: translateY(-2px);
}

.stat-badge {
  animation: scaleIn 0.4s ease-out backwards;
  display: inline-block;
  background: rgba(0,212,170,0.12);
  color: #00d4aa;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
}

.stat-badge:nth-child(1) { animation-delay: 0.1s; }
.stat-badge:nth-child(2) { animation-delay: 0.2s; }
.stat-badge:nth-child(3) { animation-delay: 0.3s; }
.stat-badge:nth-child(4) { animation-delay: 0.4s; }

.button-hover {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.button-hover:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,212,170,0.2);
}

.gradient-bg {
  background: linear-gradient(135deg, rgba(0,212,170,0.05) 0%, rgba(0,212,170,0.02) 100%);
  animation: fadeIn 0.8s ease-out;
}

.number-animate {
  font-variant-numeric: tabular-nums;
  font-weight: 700;
  font-size: 1.8rem;
}

[data-testid="stMetricContainer"] {
  animation: scaleIn 0.5s ease-out;
}

.stTabs [role="tab"] {
  transition: all 0.3s ease;
}

.stTabs [role="tab"][aria-selected="true"] {
  animation: slideInUp 0.3s ease-out;
}
</style>
"""


def inject_animations() -> None:
    """Inject animation CSS into Streamlit app."""
    st.markdown(ANIMATIONS_CSS, unsafe_allow_html=True)


def animated_header(title: str, subtitle: str = "") -> None:
    """Render animated header with title and optional subtitle."""
    st.markdown(
        f"""
        <div class='header-title' style='color:#e2e8f0;font-size:1.8rem;font-weight:700;margin-bottom:8px;'>
            {title}
        </div>
        """,
        unsafe_allow_html=True,
    )
    if subtitle:
        st.markdown(
            f"""
            <div class='header-subtitle' style='color:#64748b;font-size:0.9rem;margin-bottom:24px;'>
                {subtitle}
            </div>
            """,
            unsafe_allow_html=True,
        )


def animated_card(content: str, title: str = "") -> None:
    """Render animated card container."""
    title_html = f"<h3 style='color:#e2e8f0;margin-bottom:16px;'>{title}</h3>" if title else ""
    st.markdown(
        f"""
        <div class='intel-card-animated'>
            {title_html}
            <div style='color:#cbd5e1;'>
                {content}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def stat_badges(*badges: str) -> None:
    """Render animated stat badges in a row."""
    badge_html = "".join(f"<span class='stat-badge'>{badge}</span>" for badge in badges)
    st.markdown(
        f"""
        <div style='display:flex;gap:8px;flex-wrap:wrap;margin:12px 0;'>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def loading_spinner(text: str = "Loading...") -> None:
    """Show animated loading spinner."""
    st.markdown(
        f"""
        <div style='display:flex;align-items:center;gap:12px;color:#64748b;'>
            <div style='width:20px;height:20px;border:2px solid rgba(0,212,170,0.3);border-top-color:#00d4aa;border-radius:50%;animation:spin 1s linear infinite;'></div>
            <span>{text}</span>
        </div>
        <style>
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
