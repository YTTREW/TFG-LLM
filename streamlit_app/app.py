import streamlit as st
from api import get_chats, create_chat, get_messages, save_message
from chat import Chatbot

st.set_page_config(page_title="Chat Estudiante", layout="wide")

token = st.query_params.get("token")
if token:
    st.session_state["token"] = token[0]  # token viene en lista
else:
    st.error("No authentication token provided")
    st.stop()

st.session_state["token"] = token

# ---------- INIT SESSION ----------
if "chatbot" not in st.session_state:
    st.session_state.chatbot = Chatbot()

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []


# ---------- SIDEBAR ----------
st.sidebar.title("💬 Tus chats")

if st.sidebar.button("➕ Nuevo chat"):
    chat = create_chat()
    st.session_state.current_chat_id = chat["id"]
    st.session_state.messages = []
    st.session_state.chatbot.history = []
    st.rerun()

chats = get_chats()

for chat in chats:
    if st.sidebar.button(chat["title"], key=chat["id"]):
        st.session_state.current_chat_id = chat["id"]
        msgs = get_messages(chat["id"])
        st.session_state.messages = msgs
        st.session_state.chatbot.load_history(msgs)
        st.rerun()

# ---------- MAIN ----------
st.title("🧠 CognitiveLab – Student Chat")

if st.session_state.current_chat_id is None:
    st.info("Selecciona o crea un chat")
    st.stop()

# Mostrar mensajes
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
user_input = st.chat_input("Escribe tu mensaje...")

if user_input:
    chat_id = st.session_state.current_chat_id

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    save_message(chat_id, "user", user_input)

    with st.spinner("Pensando..."):
        response = st.session_state.chatbot.ask(user_input)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })
    save_message(chat_id, "assistant", response)

    st.rerun()

