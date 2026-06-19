import streamlit as st

st.title("AI Chat")
query = st.text_input("Ask about a stock")
if query:
    st.info(f"Research assistant placeholder response for: {query}")
