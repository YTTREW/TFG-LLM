import streamlit as st
from api_client import get_cases, get_chats, create_chat, get_messages, send_message, delete_chat

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

st.sidebar.title("🩺 Clinical Cases")

# --- OPTIMIZACIÓN: Solo pedimos a la API si no lo tenemos ya en memoria ---
if "casos" not in st.session_state:
    st.session_state.casos = get_cases()

# Usamos una bandera 'refresh_chats' para saber cuándo forzar la recarga
if "chats" not in st.session_state or st.session_state.get("refresh_chats", False):
    st.session_state.chats = get_chats()
    st.session_state.refresh_chats = False # Apagamos la bandera tras recargar

casos = st.session_state.casos
chats = st.session_state.chats

if not casos:
    st.sidebar.info("There are no clinical cases available yet.")
else:
    for caso in casos:
        badge = "🔴 Evaluable" if caso["es_evaluable"] else "🟢 Practice"
        st.sidebar.markdown(f"### {caso['nombre_paciente']} <span style='font-size:12px; color:#ccc;'>({badge})</span>", unsafe_allow_html=True)
        
        if st.sidebar.button("➕ New Simulation", key=f"new_chat_{caso['id']}"):
            nuevo_chat = create_chat(caso["id"])
            st.session_state.current_chat_id = nuevo_chat["id"]
            st.session_state.messages = []
            st.session_state.refresh_chats = True  
            st.rerun()

        chats_del_caso = [c for c in chats if c.get("caso_id") == caso["id"]]
        
        for chat in chats_del_caso:
            col1, col2 = st.sidebar.columns([4, 1])

            with col1:
                if st.button(chat["title"], key=f"open_{chat['id']}"):
                    st.session_state.current_chat_id = chat["id"]
                    msgs = get_messages(chat["id"])
                    st.session_state.messages = msgs
                    st.rerun()

            with col2:
                if st.button("🗑️", key=f"delete_{chat['id']}"):
                    delete_chat(chat["id"])

                    # Si borras el chat actual, limpiamos la vista
                    if st.session_state.get("current_chat_id") == chat["id"]:
                        st.session_state.current_chat_id = None
                        st.session_state.messages = []
                    st.session_state.refresh_chats = True # <--- AÑADE ESTA LÍNEA
                    st.rerun()
        
        st.sidebar.divider()

# ---------- MAIN ----------
st.title("🧠 CognitiveLab – Student Chat")

if st.session_state.current_chat_id is None:
    st.info("Choose a clinical case on the left to start a simulation.")
    st.stop()

# Mostrar mensajes
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
user_input = st.chat_input("Write your message...")

if user_input:
    chat_id = st.session_state.current_chat_id

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Pensando respuesta clínica..."):
        ai_response = send_message(chat_id, user_input)

    st.session_state.messages.append(ai_response)
    with st.chat_message("assistant"):
        st.markdown(ai_response["content"])