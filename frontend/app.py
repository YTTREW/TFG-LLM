import streamlit as st
from api_client import get_chats, create_chat, get_messages, send_message, delete_chat

st.set_page_config(page_title="Chat Student", layout="wide")

#Estilos 
st.markdown(
    """
    <style>
    /* Fondo de toda la app con gradiente */
    .stApp {
        background: linear-gradient(135deg, #0b1d3a, #0f2a55, #0d3b70);
        color: white;  /* Texto blanco */
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #0d2a50, #102f70, #1a3b90);
        color: white;
    }

    /* Botones primarios */
    button[kind="primary"] {
        background-color: #1a3a5c;
        color: white;
        border-radius: 8px;
        border: none;
    }

    /* Inputs de texto */
    .stTextInput>div>div>input {
        background-color: #0f2a55;
        color: white;
        border: 1px solid #1a3a5c;
        border-radius: 4px;
    }

    /* Scrollbars opcionales */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-thumb {
        background-color: #1a3a5c;
        border-radius: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- AUTH ----------
if "token" not in st.session_state:
    token_param = st.query_params.get("token")

    if token_param:
        st.session_state["token"] = token_param
    else:
        st.error("No authentication token provided")
        st.stop()

# ---------- INIT SESSION ----------

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []


# ---------- SIDEBAR ----------

if st.sidebar.button("🚪 Sign out"):
    st.session_state.clear()
    st.query_params.clear() 
    st.markdown(
        '<meta http-equiv="refresh" content="0; url=http://localhost:8000/logout">',
        unsafe_allow_html=True
    )
    st.stop()

if st.sidebar.button("➕ New chat"):
    chat = create_chat()
    st.session_state.current_chat_id = chat["id"]
    st.session_state.messages = []
    st.rerun()

st.sidebar.divider()


st.sidebar.title("💬 Chats")

chats = get_chats()

for chat in chats:
    col1, col2 = st.sidebar.columns([4, 1])

    # 👉 Botón para ABRIR chat
    with col1:
        if st.button(chat["title"], key=f"open_{chat['id']}"):
            st.session_state.current_chat_id = chat["id"]
            msgs = get_messages(chat["id"])
            st.session_state.messages = msgs
            st.rerun()

    # 👉 Botón para BORRAR chat
    with col2:
        if st.button("🗑️", key=f"delete_{chat['id']}"):
            delete_chat(chat["id"])

            # Si borras el chat actual, limpiamos la vista
            if st.session_state.get("current_chat_id") == chat["id"]:
                st.session_state.current_chat_id = None
                st.session_state.messages = []

            st.rerun()

# ---------- MAIN ----------
st.title("🧠 CognitiveLab – Student Chat")

if st.session_state.current_chat_id is None:
    st.info("Choose or create a new chat")
    st.stop()

# Mostrar mensajes
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
user_input = st.chat_input("Write your message...")

if user_input:
    chat_id = st.session_state.current_chat_id

# 1. Mostramos el mensaje del usuario en pantalla inmediatamente
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Llamamos al Backend para que haga su magia
    with st.spinner("Pensando respuesta clínica..."):
        # El backend guarda el mensaje, llama a Ollama, guarda la respuesta y nos la devuelve
        ai_response = send_message(chat_id, user_input)

    # 3. Guardamos y pintamos la respuesta de la IA
    st.session_state.messages.append(ai_response)
    with st.chat_message("assistant"):
        st.markdown(ai_response["content"])

