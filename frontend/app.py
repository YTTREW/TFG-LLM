import streamlit as st
from api_client import get_cases, get_chats, create_chat, get_messages, send_message, delete_chat, submit_chat
from datetime import datetime

st.set_page_config(page_title="Chat Student", layout="wide")

# Styles 
st.markdown(
    """
    <style>
    /* App background with gradient */
    .stApp {
        background: linear-gradient(135deg, #0b1d3a, #0f2a55, #0d3b70);
        color: white;  /* White text */
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #0d2a50, #102f70, #1a3b90);
        color: white;
    }

    /* Primary buttons */
    button[kind="primary"] {
        background-color: #1a3a5c;
        color: white;
        border-radius: 8px;
        border: none;
    }

    /* Text inputs */
    .stTextInput>div>div>input {
        background-color: #0f2a55;
        color: white;
        border: 1px solid #1a3a5c;
        border-radius: 4px;
    }

    /* Optional scrollbars */
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

col_profile, col_logout = st.sidebar.columns(2)

with col_profile:
    if st.button("👤"):
        st.markdown('<meta http-equiv="refresh" content="0; url=http://localhost:8000/edit-profile">', unsafe_allow_html=True)

with col_logout:
    if st.button("🚪"):
        st.session_state.clear()
        st.query_params.clear() 
        st.markdown(
            '<meta http-equiv="refresh" content="0; url=http://localhost:8000/logout">',
            unsafe_allow_html=True
        )
        st.stop()

st.sidebar.title("🩺 Clinical Cases")

# --- OPTIMIZATION: Fetch from API only if not in memory ---
if "cases" not in st.session_state:
    st.session_state.cases = get_cases()

# Use a 'refresh_chats' flag to force reload when needed
if "chats" not in st.session_state or st.session_state.get("refresh_chats", False):
    st.session_state.chats = get_chats()
    st.session_state.refresh_chats = False # Turn off flag after reload

cases = st.session_state.cases
chats = st.session_state.chats

if not cases:
    st.sidebar.info("There are no clinical cases available yet.")
else:
    for case in cases:
        # Note: 'es_evaluable', 'fecha_entrega', and 'nombre_paciente' are kept in Spanish 
        # because they are the exact keys coming from the database/API response.
        badge = "🔴 Evaluable" if case["es_evaluable"] else "🟢 Practice"

        if case.get("fecha_entrega"):
            parts = case["fecha_entrega"].split("-")
            deadline_str = f" | Deadline: {parts[2]}/{parts[1]}/{parts[0]}"
        else:
            deadline_str = ""

        st.sidebar.markdown(f"### {case['nombre_paciente']} <span style='font-size:12px; color:#ccc;'>({badge}{deadline_str})</span>", unsafe_allow_html=True)
        
        if st.sidebar.button("➕ New Simulation", key=f"new_chat_{case['id']}"):
            new_chat = create_chat(case["id"])
            st.session_state.current_chat_id = new_chat["id"]
            st.session_state.messages = []
            st.session_state.refresh_chats = True  
            st.rerun()

        case_chats = [c for c in chats if c.get("caso_id") == case["id"]]
        
        for chat in case_chats:
            col1, col2 = st.sidebar.columns([4, 1])

            try:
                # Extract and format the chat creation date
                date_obj = datetime.fromisoformat(chat["created_at"])
                creation_date_str = date_obj.strftime("%d/%m/%Y")
            except:
                creation_date_str = ""

# --- NUEVA LÓGICA DE ICONOS DE ESTADO ---
            if chat.get("grade") is not None:
                status_prefix = "⭐ "  # Icono de nota puesta
                status_label = " (Graded)"
            elif chat.get("enviado"):
                status_prefix = "✅ "  # Enviado pero no corregido
                status_label = " (Submitted)"
            else:
                status_prefix = "💬 "  # Chat en progreso
                status_label = ""
            button_title = f"{chat['title']} ({creation_date_str})"
            
            with col1:
                if st.button(button_title, key=f"open_{chat['id']}"):
                    st.session_state.current_chat_id = chat["id"]
                    msgs = get_messages(chat["id"])
                    st.session_state.messages = msgs
                    st.rerun()

            with col2:
                if st.button("🗑️", key=f"delete_{chat['id']}"):
                    delete_chat(chat["id"])

                    if st.session_state.get("current_chat_id") == chat["id"]:
                        st.session_state.current_chat_id = None
                        st.session_state.messages = []
                    st.session_state.refresh_chats = True 
                    st.rerun()
        
        st.sidebar.divider()

# ---------- MAIN ----------

# Dynamic logic for the "Virtual Patient: [Name]" title
if st.session_state.current_chat_id is None:
    st.title("🧠 CognitiveLab")
    st.info("Choose a clinical case on the left to start a simulation.")
    st.stop()

current_chat = next((c for c in st.session_state.chats if c["id"] == st.session_state.current_chat_id), None)

if current_chat:
    title_parts = current_chat["title"].split(": ")
    patient_name = title_parts[-1] if len(title_parts) > 1 else current_chat["title"]

# 1. Buscamos a qué caso pertenece el chat actual
    caso_id_actual = current_chat.get("caso_id")
    
    # 2. Comprobamos si ALGÚN chat de ESTE CASO ya está marcado como enviado
    chats_del_mismo_caso = [c for c in st.session_state.chats if c.get("caso_id") == caso_id_actual]
    chat_ya_enviado = next((c for c in chats_del_mismo_caso if c.get("enviado") == True), None)

    col_titulo, col_boton = st.columns([3, 1])
    with col_titulo:
        st.title(f"🧠 Virtual Patient: {patient_name}")
            
    with col_boton:
        # Damos un poco de margen para alinear con el título
        st.write("") 
        st.write("")
        if current_chat.get("enviado"):
            st.success("✅ Submitted for Evaluation")
            # CASO B: El alumno NO ha enviado este, pero SÍ ha enviado otro de este mismo paciente
        elif chat_ya_enviado:
            st.info("🔒 Submitted in another chat")
        else:
            if st.button("📤 Submit to Professor", use_container_width=True):
                submit_chat(current_chat["id"])
                st.session_state.refresh_chats = True
                st.rerun()
else:
    st.title("🧠 Virtual Patient")

if current_chat and current_chat.get("grade") is not None:
    st.success(f"### 🏆 Grade: {current_chat['grade']} / 10")
    if current_chat.get("feedback"):
        with st.expander("📝 Check feedback", expanded=True):
            st.write(current_chat["feedback"])
    
# Display messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
chat_bloqueado = current_chat.get("enviado", False) if current_chat else False

# 2. Cambiamos el texto del input dependiendo de si está bloqueado o no
texto_input = "🔒 Chat submitted for evaluation. You cannot send more messages." if chat_bloqueado else "Write your message..."
user_input = st.chat_input(texto_input, disabled=chat_bloqueado)

if user_input:
    chat_id = st.session_state.current_chat_id

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Generating clinical response..."):
        ai_response = send_message(chat_id, user_input)

    st.session_state.messages.append(ai_response)
    with st.chat_message("assistant"):
        st.markdown(ai_response["content"])