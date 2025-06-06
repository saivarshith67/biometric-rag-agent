# frontend/app.py

import streamlit as st
from frontend.components.chat_ui import display_chat
from frontend.utils.api import chat_with_bot, start


st.set_page_config(page_title="Chatbot", layout="centered")

start()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("💬 Biometric Chatbot")

user_input = st.chat_input("Type your question...")

if user_input:
    st.session_state.chat_history.append(("user", user_input))
    with st.spinner("Thinking..."):
        bot_response = chat_with_bot(user_input)
    st.session_state.chat_history.append(("bot", bot_response))

display_chat(st.session_state.chat_history)
