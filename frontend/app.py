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

    /* 4. EXPANDER DE FEEDBACK (Arreglo del fondo negro) */
    /* La caja principal */
    details[data-testid="stExpander"] {
        background-color: #ffffff !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 10px !important;
        overflow: hidden; /* Evita que el fondo sobresalga */
    }
    
    /* La barra donde haces clic (Check feedback) */
    details[data-testid="stExpander"] summary,
    details[data-testid="stExpander"] summary p,
    details[data-testid="stExpander"] summary span {
        background-color: #f8fafc !important; /* Un gris muuuy clarito */
        color: #0f172a !important;
        font-weight: 700 !important;
    }
    
    /* El área interior donde está el texto del feedback */
    div[data-testid="stExpanderDetails"], 
    div[data-testid="stExpanderDetails"] p {
        background-color: #ffffff !important; /* Blanco puro */
        color: #1e293b !important; /* Texto oscuro */
    }

    /* 5. SIDEBAR OSCURA */
    section[data-testid="stSidebar"] {
        background-color: #1e293b !important;
    }
    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.2) !important;
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

    /* 7. BOTONES PRINCIPALES */
    .stButton>button {
        background: #2563eb !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
    }

    .footer-text {
        text-align: center;
        color: #475569;
        font-size: 14px;
        margin-top: 40px;
        font-weight: 700;
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
        badge = "🔴 Evaluable" if case["is_evaluable"] else "🟢 Practice"

        if case.get("deadline"):
            parts = case["deadline"].split("-")
            deadline_str = f" | Deadline: {parts[2]}/{parts[1]}/{parts[0]}"
        else:
            deadline_str = ""

        st.sidebar.markdown(f"### {case['patient_name']} <span style='font-size:12px; color:#ccc;'>({badge}{deadline_str})</span>", unsafe_allow_html=True)
        
        if st.sidebar.button("➕ New Simulation", key=f"new_chat_{case['id']}"):
            new_chat = create_chat(case["id"])
            st.session_state.current_chat_id = new_chat["id"]
            st.session_state.messages = []
            st.session_state.refresh_chats = True  
            st.rerun()

        case_chats = [c for c in chats if c.get("clinical_case_id") == case["id"]]
        
        for chat in case_chats:
            col1, col2 = st.sidebar.columns([4, 1])

            try:
                date_obj = datetime.fromisoformat(chat["created_at"])
                creation_date_str = date_obj.strftime("%d/%m/%Y")
            except:
                creation_date_str = ""

            if chat.get("grade") is not None:
                status_prefix = "⭐ "  
                status_label = " (Graded)"
            elif chat.get("enviado"):
                status_prefix = "✅ "  
                status_label = " (Submitted)"
            else:
                status_prefix = "💬 " 
                status_label = ""
            button_title = f"{status_prefix}{chat['title']} ({creation_date_str}){status_label}"
            
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
