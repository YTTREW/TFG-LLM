import streamlit as st
from api_client import get_cases, get_chats, create_chat, get_messages, send_message, delete_chat, submit_chat
from datetime import datetime

st.set_page_config(page_title="Chat Student", layout="wide")

st.markdown("""
    <style>
    /* 1. FONDO GLOBAL */
    .stApp {
        background: linear-gradient(135deg, #dbeafe 0%, #93c5fd 100%);
    }

    /* 2. TÍTULOS PRINCIPALES (Forzamos el color oscuro sí o sí) */
    div.block-container h1, 
    div.block-container h2, 
    div.block-container h3 {
        color: #0f172a !important;
        font-weight: 800 !important;
    }

    /* 3. NOTA DE EVALUACIÓN (Grade) - Fondo verde claro, letra verde oscura */
    div[data-testid="stAlert"] {
        background-color: #dcfce7 !important;
        border: 1px solid #16a34a !important;
        border-radius: 10px !important;
    }
    div[data-testid="stAlert"] * {
        color: #14532d !important;
        font-weight: 700 !important;
    }

/* 4. EXPANDER DE FEEDBACK (Área principal - Blanco) */
    div.block-container details[data-testid="stExpander"] {
        background-color: #ffffff !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 10px !important;
        overflow: hidden;
    }
    div.block-container details[data-testid="stExpander"] summary,
    div.block-container details[data-testid="stExpander"] summary p,
    div.block-container details[data-testid="stExpander"] summary span {
        background-color: #f8fafc !important;
        color: #0f172a !important;
        font-weight: 700 !important;
    }
    div.block-container div[data-testid="stExpanderDetails"] {
        background-color: #ffffff !important;
        color: #1e293b !important;
    }

    /* 5. SIDEBAR Y SUS DESPLEGABLES (Oscuro) */
    section[data-testid="stSidebar"] {
        background-color: #1e293b !important;
    }
    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    /* Estilo específico para los desplegables de los Casos Clínicos */
    section[data-testid="stSidebar"] details[data-testid="stExpander"] {
        background-color: #0f172a !important; /* Un azul ligeramente más oscuro que la sidebar */
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        margin-bottom: 10px !important; /* Separación entre casos */
    }
    section[data-testid="stSidebar"] details[data-testid="stExpander"] summary,
    section[data-testid="stSidebar"] details[data-testid="stExpander"] summary p {
        background-color: transparent !important;
        font-size: 20px !important; 
        font-weight: 800 !important;
    }
    /* Reducir el espacio interior del desplegable en la sidebar */
    section[data-testid="stSidebar"] div[data-testid="stExpanderDetails"] {
        background-color: transparent !important;
        padding-top: 0.5rem !important; 
        padding-bottom: 0.5rem !important;
    }

    /* 6. CHAT BUBBLES - Burbujas blancas, texto oscuro */
    div[data-testid="stChatMessage"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 15px !important;
    }
    div[data-testid="stChatMessage"] * {
        color: #0f172a !important;
    }

/* 7. BOTONES PRINCIPALES (Normales) */
    button[kind="secondary"] {
        background: #2563eb !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        border: 1px solid #1d4ed8 !important;
    }

    /* 8. BOTONES DESTACADOS (Graded - Verdes y con animación) */
    button[kind="primary"] {
        background: linear-gradient(45deg, #16a34a, #22c55e) !important;
        color: white !important;
        font-weight: 800 !important;
        border-radius: 10px !important;
        border: none !important;
        animation: pulse_green 2s infinite !important;
    }

    /* Animación de latido (Pulso) para los evaluados */
    @keyframes pulse_green {
        0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); }
        100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
    }
            
    /* Estilo para los recuadros de estado dentro del expander */
    .status-box {
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 15px;
        border: 1px solid #334155;
    }
    .status-evaluable {
        background-color: #450a0a !important; /* Rojo muy oscuro */
        border-left: 5px solid #ef4444 !important;
    }
    .status-practice {
        background-color: #064e3b !important; /* Verde muy oscuro */
        border-left: 5px solid #10b981 !important;
    }
    .status-box p {
        margin: 0 !important;
        font-size: 14px !important;
    }
    </style>
    """, unsafe_allow_html=True)

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
col_margin1, col_profile, col_spacer, col_logout, col_margin2 = st.sidebar.columns([0.5, 3, 1.5, 3, 0.5])

with col_profile:
    if st.button("👤 ", use_container_width=True):
        st.markdown('<meta http-equiv="refresh" content="0; url=http://localhost:8000/edit-profile">', unsafe_allow_html=True)

with col_logout:
    if st.button("🚪 ", use_container_width=True):
        st.session_state.clear()
        st.query_params.clear() 
        st.markdown(
            '<meta http-equiv="refresh" content="0; url=http://localhost:8000/logout">',
            unsafe_allow_html=True
        )
        st.stop()

st.sidebar.write("")
st.sidebar.title("🩺 Clinical Cases")

if "cases" not in st.session_state:
    st.session_state.cases = get_cases()

if "chats" not in st.session_state or st.session_state.get("refresh_chats", False):
    st.session_state.chats = get_chats()
    st.session_state.refresh_chats = False 

cases = st.session_state.cases
chats = st.session_state.chats

if not cases:
    st.sidebar.info("There are no clinical cases available yet.")
else:
    for case in cases:
        is_eval = case.get("is_evaluable", False)

        if case.get("deadline"):
            parts = case["deadline"].split("-")
            deadline_date = f"{parts[2]}/{parts[1]}/{parts[0]}"
        else:
            deadline_date = "No deadline"

        expander_title = f"📂 {case['patient_name']}"
        
        with st.sidebar.expander(expander_title):
            if is_eval:
                st.markdown(f"""
                    <div class="status-box status-evaluable">
                        <p style="color: #fca5a5; font-weight: bold;">⚠️ EVALUABLE</p>
                        <p style="color: #ffffff;">📅 Deadline: {deadline_date}</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="status-box status-practice">
                        <p style="color: #6ee7b7; font-weight: bold;">🟢 PRACTICE</p>
                        
                    </div>
                """, unsafe_allow_html=True)

            st.write("") 
            
            if st.button("➕ New Simulation", key=f"new_chat_{case['id']}", use_container_width=True):
                new_chat = create_chat(case["id"])
                st.session_state.current_chat_id = new_chat["id"]
                st.session_state.messages = []
                st.session_state.refresh_chats = True  
                st.rerun()

            case_chats = [c for c in chats if c.get("clinical_case_id") == case["id"]]
            if case_chats:
                st.markdown("<div style='margin: 10px 0px; border-bottom: 1px solid #334155;'></div>", unsafe_allow_html=True)
            for chat in case_chats:
                col1, col2 = st.columns([4, 1])

                try:
                    date_obj = datetime.fromisoformat(chat["created_at"])
                    creation_date_str = date_obj.strftime("%d/%m/%Y")
                except:
                    creation_date_str = ""

                is_graded = chat.get("grade") is not None
                is_submitted = chat.get("is_submitted") or chat.get("enviado")

                if chat.get("grade") is not None:
                    btn_type = "primary"
                elif chat.get("enviado"):
                    btn_type = "secondary"
                else:
                    status_label = ""
                    btn_type = "secondary"
                
                button_title = f"{chat['title']} ({creation_date_str}){status_label}"
                
                with col1:
                    if st.button(button_title, key=f"open_{chat['id']}", use_container_width=True, type=btn_type):
                        st.session_state.current_chat_id = chat["id"]
                        msgs = get_messages(chat["id"])
                        st.session_state.messages = msgs
                        st.rerun()

                with col2:
                    disable_delete = is_submitted or is_graded
                    help_msg = "Cannot delete: already submitted" if disable_delete else "Delete simulation"
                    if st.button("🗑️", key=f"delete_{chat['id']}", use_container_width=True, disabled=disable_delete, help=help_msg):
                        delete_chat(chat["id"])

                        if st.session_state.get("current_chat_id") == chat["id"]:
                            st.session_state.current_chat_id = None
                            st.session_state.messages = []
                        st.session_state.refresh_chats = True 
                        st.rerun()

# ---------- MAIN ----------

if st.session_state.current_chat_id is None:
    st.title("🧠 CognitiveLab")
    st.info("Choose a clinical case on the left to start a simulation.")
    st.stop()

current_chat = next((c for c in st.session_state.chats if c["id"] == st.session_state.current_chat_id), None)

if current_chat:
    title_parts = current_chat["title"].split(": ")
    patient_name = title_parts[-1] if len(title_parts) > 1 else current_chat["title"]

    current_case_id = current_chat.get("clinical_case_id")
    
    chats_case = [c for c in st.session_state.chats if c.get("clinical_case_id") == current_case_id]
    chat_submitted = next((c for c in chats_case if c.get("is_submitted") == True), None)

    col_titulo, col_boton = st.columns([3, 1])
    with col_titulo:
        st.title(f"🧠 Virtual Patient: {patient_name}")
            
    with col_boton:
        st.write("") 
        st.write("")
        if current_chat.get("is_submitted"):
            st.success("✅ Submitted for Evaluation")
        elif chat_submitted:
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
    
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

chat_locked = current_chat.get("is_submitted", False) if current_chat else False

texto_input = "🔒 Chat submitted for evaluation. You cannot send more messages." if chat_locked else "Write your message..."
user_input = st.chat_input(texto_input, disabled=chat_locked)

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
