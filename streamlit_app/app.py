import streamlit as st
from streamlit_chat import message
from chat import Chatbot

st.set_page_config(page_title="Chat Estudiante")

if "chatbot" not in st.session_state:
    st.session_state.chatbot = Chatbot()
    st.session_state.messages = []

st.title("Chat Estudiante")

for msg, is_user in st.session_state.messages:
    with st.chat_message("user" if is_user else "assistant"):
        st.markdown(msg)

user_input = st.chat_input("Escribe tu mensaje...")

if user_input:
    st.session_state.messages.append((user_input, True))

    with st.spinner("Pensando..."):
        response = st.session_state.chatbot.ask(user_input)

    # 🔍 DEBUG
    st.write("DEBUG respuesta:", response)

    st.session_state.messages.append((response, False))
    st.rerun()
