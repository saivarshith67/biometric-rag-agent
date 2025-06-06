# frontend/components/chat_ui.py

import streamlit as st

def display_chat(history):
    for _, (role, text) in enumerate(history):
        if role == "user":
            with st.chat_message("user"):
                st.write(text)
        else:
            with st.chat_message("ai"):
                st.write(text)
