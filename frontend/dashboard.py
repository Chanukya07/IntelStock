"""Streamlit entrypoint for IntelStock dashboard."""

import streamlit as st

st.set_page_config(page_title="IntelStock", layout="wide")
st.title("IntelStock")
st.caption("AI-Powered Stock Intelligence Agent")

st.markdown(
    """
    ### Core Views
    - Overview
    - Stock Research
    - Sentiment Dashboard
    - Portfolio Analyzer
    - AI Chat
    """
)
