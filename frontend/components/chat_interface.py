"""Streamlit chat interface with streaming support."""

import streamlit as st
import requests


def render_chat_interface(api_base_url: str = "http://localhost:8000") -> None:
    """Render interactive chat interface with streaming responses."""
    st.markdown("### 💬 AI Stock Analyst Chat")
    st.markdown("Ask questions about Indian stocks (NSE/BSE) and get AI-powered insights.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    chat_input = st.chat_input("Ask about a stock (e.g., 'What's the outlook for TCS?')")

    if chat_input:
        st.session_state.chat_history.append({"role": "user", "content": chat_input})

        with st.chat_message("user"):
            st.write(chat_input)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""

            try:
                response = requests.post(
                    f"{api_base_url}/chat/stream",
                    json={"query": chat_input},
                    stream=True,
                    timeout=30,
                )
                response.raise_for_status()

                for chunk in response.iter_content(decode_unicode=True):
                    if chunk:
                        full_response += chunk
                        placeholder.markdown(full_response + "▌")

                placeholder.markdown(full_response)
            except requests.exceptions.RequestException as e:
                st.error(f"Error getting response: {str(e)}")
                placeholder.markdown("Failed to get response from server.")

            if full_response:
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": full_response}
                )

    if st.session_state.chat_history:
        st.divider()
        st.markdown("### Chat History")
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()
