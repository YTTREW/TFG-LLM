import streamlit as st
from api_client import get_cases, get_chats, create_chat, get_messages, send_message, delete_chat, submit_chat
from datetime import datetime

st.set_page_config(page_title="Chat Student", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #dbeafe 0%, #93c5fd 100%);
    }

    div.block-container h1, 
    div.block-container h2, 
    div.block-container h3 {
        color: #0f172a !important;
        font-weight: 800 !important;
    }

    div[data-testid="stAlert"] {
        background-color: #dcfce7 !important;
        border: 1px solid #16a34a !important;
        border-radius: 10px !important;
    }
    div[data-testid="stAlert"] * {
        color: #14532d !important;
        font-weight: 700 !important;
    }

    .status-text-evaluable {
        color: #f87171 !important;
        font-weight: 900 !important;
        font-size: 15px !important;
    }
    .status-text-practice {
        color: #4ade80 !important;
        font-weight: 900 !important;
        font-size: 15px !important;
    }
    
    .main [data-testid="stExpander"] {
        border: 2px solid #3b82f6 !important;
        border-radius: 8px !important;
        background-color: #ffffff !important;
        margin-bottom: 20px !important;
        overflow: hidden !important;
    }

    .main [data-testid="stExpander"] summary {
        background-color: #bfdbfe !important; 
        padding: 10px 15px !important;
    }

    .main [data-testid="stExpander"] summary,
    .main [data-testid="stExpander"] summary p,
    .main [data-testid="stExpander"] summary span,
    .main [data-testid="stExpander"] summary svg {
        color: #0f172a !important;
        fill: #0f172a !important; 
        font-weight: 800 !important;
        font-size: 16px !important;
        background-color: transparent !important; 
    }

    .main [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        background-color: #ffffff !important;
        padding: 15px !important;
    }

    .main [data-testid="stExpander"] [data-testid="stExpanderDetails"] * {
        color: #1e293b !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #1e293b !important;
    }
    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] details[data-testid="stExpander"] {
        background-color: #0f172a !important; 
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        margin-bottom: 10px !important; 
    }
    
    section[data-testid="stSidebar"] [data-testid="stExpander"] summary p,
    section[data-testid="stSidebar"] [data-testid="stExpander"] summary span,
    section[data-testid="stSidebar"] details summary * {
        font-size: 18px !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        line-height: 1.5 !important;
    }
    
    section[data-testid="stSidebar"] div[data-testid="stExpanderDetails"] {
        background-color: transparent !important;
        padding-top: 0.5rem !important; 
        padding-bottom: 0.5rem !important;
    }

    div[data-testid="stChatMessage"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 15px !important;
    }
    div[data-testid="stChatMessage"] * {
        color: #0f172a !important;
    }

    button[kind="secondary"] {
        background: #581c87 !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        border: 1px solid #3b0764 !important;
        transition: all 0.2s ease-in-out !important;
    }
    
    button[kind="secondary"]:hover {
        background: #6b21a8 !important; 
        transform: scale(1.02) !important; 
        box-shadow: 0 6px 10px rgba(107, 33, 168, 0.3) !important; 
    }
            
    button[kind="primary"] {
        background: linear-gradient(45deg, #16a34a, #22c55e) !important;
        color: white !important;
        font-weight: 800 !important;
        border-radius: 10px !important;
        border: 1px solid #14532d !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2) !important; 
        transition: all 0.2s ease-in-out !important;
    }

    button[kind="primary"]:hover {
        transform: scale(1.02) !important; 
        box-shadow: 0 6px 10px rgba(0,0,0,0.3) !important;
    }
            
.status-box {
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 15px;
        background-color: transparent !important; 
    }
    .status-evaluable {
        border: 2px solid #ef4444 !important; 
    }
    .status-practice {
        border: 2px solid #10b981 !important; 
    }
    .status-box p {
        margin: 0 !important;
        font-size: 14px !important;
    }

    div[data-testid="stExpanderDetails"] button[kind="secondary"] {
        background: transparent !important;
        border: 2px dashed #94a3b8 !important; 
        color: #475569 !important; 
        font-weight: 700 !important;
        border-radius: 10px !important;
        box-shadow: none !important;
        transition: all 0.2s ease-in-out !important;
    }

    div[data-testid="stExpanderDetails"] button[kind="secondary"]:hover {
        border-color: #3b82f6 !important;
        color: #3b82f6 !important;
        background: transparent !important; /* <--- AHORA SE QUEDA TRANSPARENTE */
        transform: translateY(-1px) !important;
    }

    div[data-testid="stExpanderDetails"] div[data-testid="column"]:nth-child(1) button[kind="secondary"] {
        background: #581c87 !important; 
        color: white !important;
        border: 1px solid #3b0764 !important;
        border-style: solid !important; 
        box-shadow: none !important;
    }
    
    div[data-testid="stExpanderDetails"] div[data-testid="column"]:nth-child(1) button[kind="secondary"]:hover {
        background: #6b21a8 !important; 
        color: white !important;
        transform: scale(1.02) !important; 
        box-shadow: 0 6px 10px rgba(107, 33, 168, 0.3) !important; 
    }

    div[data-testid="stExpanderDetails"] div[data-testid="column"]:nth-child(1) button[kind="secondary"]:disabled {
        opacity: 1 !important;
        box-shadow: inset 0 4px 8px rgba(0, 0, 0, 0.5) !important; 
        filter: brightness(0.85) !important; 
    }

    div[data-testid="stExpanderDetails"] div[data-testid="column"]:nth-child(2) button {
        background: linear-gradient(135deg, #ef4444, #dc2626) !important; 
        color: white !important;
        border: 1px solid #450a0a !important;
        border-style: solid !important;
        border-radius: 10px !important;
        transition: all 0.2s ease-in-out !important;
    }

    div[data-testid="stExpanderDetails"] div[data-testid="column"]:nth-child(2) button:hover:not(:disabled) {
        background: linear-gradient(145deg, #991b1b, #b91c1c) !important; 
        border-color: #7f1d1d !important;
        transform: scale(1.05) !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2) !important;
        color: white !important;
    }

    div[data-testid="stExpanderDetails"] div[data-testid="column"]:nth-child(2) button:disabled {
        background: #292524 !important; 
        border: 1px solid #44403c !important;
        color: #78716c !important;
        opacity: 0.6 !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]:first-of-type button {
        padding: 15px 0px !important; 
        font-size: 28px !important; 
        line-height: 1 !important;
        border-radius: 12px !important;
        transition: all 0.2s ease-in-out !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="column"]:nth-child(2):nth-last-child(4) button {
        background: linear-gradient(135deg, #3b82f6, #2563eb) !important; 
        border: 1px solid #60a5fa !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
    }
    
    section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="column"]:nth-child(2):nth-last-child(4) button:hover {
        background: linear-gradient(135deg, #60a5fa, #3b82f6) !important; 
        transform: scale(1.08) !important; 
    }

    section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="column"]:nth-last-child(2) button {
        background: linear-gradient(135deg, #ef4444, #dc2626) !important; 
        border: 1px solid #f87171 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="column"]:nth-last-child(2) button:hover {
        background: linear-gradient(135deg, #f87171, #ef4444) !important; 
        transform: scale(1.08) !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ====================================
# Interfaz del Profesor
# ====================================
if "preview_case_id" in st.query_params:
    case_id = int(st.query_params["preview_case_id"])
    
    if st.session_state.get("last_preview_id") != case_id:
        st.session_state.preview_messages = []
        st.session_state.last_preview_id = case_id

    if "preview_messages" not in st.session_state:
        st.session_state.preview_messages = []
    
    col_margin1, col_back, col_margin2 = st.sidebar.columns([0.5, 6, 0.5])
    
    with col_back:
        if st.button("🔙 Back to Cases", use_container_width=True):
            st.markdown(
                '<meta http-equiv="refresh" content="0; url=http://localhost:8000/professor/cases">',
                unsafe_allow_html=True
            )
            
    st.sidebar.write("")

    st.title("Case Preview Mode")
    st.info("You are testing this clinical case. This conversation is temporary and will NOT be saved in the database.")

    if "preview_messages" not in st.session_state:
        st.session_state.preview_messages = []

    for msg in st.session_state.preview_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Test the virtual patient..."):
        st.session_state.preview_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Generating response..."):
            from api_client import send_professor_test_message
            
            ai_response = send_professor_test_message(case_id, st.session_state.preview_messages)
            response = ai_response["content"]
            
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.preview_messages.append({"role": "assistant", "content": response})

    st.stop()

# ====================================
# Interfaz del Alumno
# ====================================
# ---------- Autenticacion ----------
if "token" not in st.session_state:
    token_param = st.query_params.get("token")

    if token_param:
        st.session_state["token"] = token_param
    else:
        st.error("No authentication token provided")
        st.stop()

# ---------- Inicio de sesion ----------

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- Barra lateral ----------
col_margin1, col_profile, col_spacer, col_logout, col_margin2 = st.sidebar.columns([0.5, 3, 1.5, 3, 0.5])

with col_profile:
    if st.button("👤 ", use_container_width=True):
        st.markdown('<meta http-equiv="refresh" content="0; url=http://localhost:8000/edit-profile">', unsafe_allow_html=True)

with col_logout:
    if st.button("🔙 ", use_container_width=True):
        st.session_state.clear()
        st.query_params.clear() 
        st.markdown(
            '<meta http-equiv="refresh" content="0; url=http://localhost:8000/logout">',
            unsafe_allow_html=True
        )
        st.stop()

st.sidebar.write("")
st.sidebar.title("Clinical Cases")

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

        expander_title = f"📂 { case['patient_name']}"
        
        with st.sidebar.expander(expander_title):
            if is_eval:
                st.markdown(f"""
                    <div class="status-box status-evaluable">
                        <p class="status-text-evaluable">EVALUABLE</p>
                        <p style="color: #ffffff !important;">Deadline: {deadline_date}</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="status-box status-practice">
                        <p class="status-text-practice">PRACTICE</p>
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

                if is_graded:
                    btn_type = "primary"
                    status_label = "Evaluated - "
                elif is_submitted:
                    btn_type = "secondary"
                    status_label = "Submitted - "
                else:
                    btn_type = "secondary"
                    status_label = ""
                
                button_title = f"{status_label}{chat['title']} ({creation_date_str})"
                
                with col1:
                    is_active = (st.session_state.current_chat_id == chat["id"])
                    
                    if st.button(button_title, key=f"open_{chat['id']}", use_container_width=True, type=btn_type, disabled=is_active):
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
        st.title(f"Virtual Patient: {patient_name}")
            
    with col_boton:
        st.write("") 
        st.write("")
        if current_chat.get("is_submitted"):
            st.success("✅ Submitted for Evaluation")
        elif chat_submitted:
            st.info("🔒 Submitted in another chat")
        else:
            if st.button("Submit to Professor", use_container_width=True):
                submit_chat(current_chat["id"])
                st.session_state.refresh_chats = True
                st.rerun()
else:
    st.title("🧠 Virtual Patient")

if current_chat and current_chat.get("grade") is not None:
    st.success(f"### Grade: {current_chat['grade']} / 10")
    if current_chat.get("feedback"):
        with st.expander("📝 Check feedback", expanded=True):
            st.write(current_chat["feedback"])
    
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

chat_locked = current_chat.get("is_submitted", False) if current_chat else False

texto_input = "Chat submitted for evaluation. You cannot send more messages." if chat_locked else "Write your message..."
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
