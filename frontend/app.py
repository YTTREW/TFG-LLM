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

    /* FORZAR COLORES DE LOS TEXTOS DE ESTADO (Para ganarle al blanco global) */
    .status-text-evaluable {
        color: #f87171 !important; /* Rojo pastel brillante muy visible */
        font-weight: 900 !important;
        font-size: 15px !important;
    }
    .status-text-practice {
        color: #4ade80 !important; /* Verde pastel brillante muy visible */
        font-weight: 900 !important;
        font-size: 15px !important;
    }

/* 4. EXPANDER DE FEEDBACK (Letras oscuras y legibles) */
    
    /* 1. Recuadro general (Borde azul para destacar) */
    .main [data-testid="stExpander"] {
        border: 2px solid #3b82f6 !important; /* Borde azul vibrante */
        border-radius: 8px !important;
        background-color: #ffffff !important;
        margin-bottom: 20px !important;
        overflow: hidden !important;
    }

    /* 2. Fondo de la cabecera (Azul claro para diferenciarlo del chat) */
    .main [data-testid="stExpander"] summary {
        background-color: #bfdbfe !important; 
        padding: 10px 15px !important;
    }

    /* 3. ¡TEXTO OSCURO PARA QUE SE LEA PERFECTAMENTE! */
    .main [data-testid="stExpander"] summary,
    .main [data-testid="stExpander"] summary p,
    .main [data-testid="stExpander"] summary span,
    .main [data-testid="stExpander"] summary svg {
        color: #0f172a !important; /* Azul marino muy oscuro / casi negro */
        fill: #0f172a !important; /* Flecha oscura */
        font-weight: 800 !important;
        font-size: 16px !important;
        background-color: transparent !important; 
    }

    /* 4. Interior del recuadro (Donde va el comentario) */
    .main [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        background-color: #ffffff !important;
        padding: 15px !important;
    }

    /* 5. Texto del comentario del profesor */
    .main [data-testid="stExpander"] [data-testid="stExpanderDetails"] * {
        color: #1e293b !important;
    }

    /* 5. SIDEBAR Y SUS DESPLEGABLES (Oscuro) */
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
    
    /* FORZAR TAMAÑO DEL TÍTULO DE CASOS CLÍNICOS (OPCIÓN BLINDADA) */
    section[data-testid="stSidebar"] [data-testid="stExpander"] summary p,
    section[data-testid="stSidebar"] [data-testid="stExpander"] summary span,
    section[data-testid="stSidebar"] details summary * {
        font-size: 18px !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        line-height: 1.5 !important;
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

    /* 7. BOTONES PRINCIPALES (Secundarios - Morado con efecto Zoom) */
    button[kind="secondary"] {
        background: #581c87 !important; /* Morado oscuro elegante */
        color: white !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        border: 1px solid #3b0764 !important;
        transition: all 0.2s ease-in-out !important;
    }
    
    button[kind="secondary"]:hover {
        background: #6b21a8 !important; /* Se aclara un poco */
        transform: scale(1.02) !important; /* ¡AQUÍ ESTÁ EL EFECTO DE AUMENTO! */
        box-shadow: 0 6px 10px rgba(107, 33, 168, 0.3) !important; /* Sombra para acompañar el zoom */
    }
            
    /* 8. BOTONES DESTACADOS (Graded - Verde fijo, sin animación) */
    button[kind="primary"] {
        background: linear-gradient(45deg, #16a34a, #22c55e) !important;
        color: white !important;
        font-weight: 800 !important;
        border-radius: 10px !important;
        border: 1px solid #14532d !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2) !important; /* Sombra estática para destacar */
        transition: all 0.2s ease-in-out !important;
    }

    button[kind="primary"]:hover {
        transform: scale(1.02) !important; /* Crece un pelín al pasar el ratón */
        box-shadow: 0 6px 10px rgba(0,0,0,0.3) !important;
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
            
    /* 9. BOTÓN DE BORRAR (Papelera en rojo oscuro elegante) */
    /* Apuntamos directamente a los botones de la segunda columna (col2) dentro del desplegable */
    div[data-testid="stExpanderDetails"] div[data-testid="column"]:nth-child(2) button {
        background: linear-gradient(145deg, #7f1d1d, #991b1b) !important; /* Degradado rojo oscuro/cereza */
        color: white !important;
        border: 1px solid #450a0a !important;
        border-radius: 10px !important;
        transition: all 0.2s ease-in-out !important;
    }

    /* Efecto al pasar el ratón (solo se aplica si NO está bloqueado) */
    div[data-testid="stExpanderDetails"] div[data-testid="column"]:nth-child(2) button:hover:not(:disabled) {
        background: linear-gradient(145deg, #991b1b, #b91c1c) !important; /* Rojo un poco más vivo */
        border-color: #7f1d1d !important;
        transform: scale(1.05) !important; /* Hace un pequeñísimo zoom de advertencia */
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2) !important;
    }

    /* Estilo para cuando el botón está deshabilitado (cuando ya está evaluado/enviado) */
    div[data-testid="stExpanderDetails"] div[data-testid="column"]:nth-child(2) button:disabled {
        background: #292524 !important; /* Un gris/marrón muy oscuro y neutro */
        border: 1px solid #44403c !important;
        color: #78716c !important;
        opacity: 0.6 !important;
    }
            
    /* 11. CHAT ACTIVO (Sin vibración y con efecto de hundido) */
    /* Cuando el botón verde (Graded) es el chat actual (está deshabilitado) */
    div[data-testid="stExpanderDetails"] div[data-testid="column"]:nth-child(1) button[kind="primary"]:disabled {
        background: #16a34a !important; /* Verde sólido para que no brille tanto */
        color: white !important;
        opacity: 1 !important; /* Evita que Streamlit lo vuelva transparente */
        box-shadow: inset 0 4px 8px rgba(0, 0, 0, 0.5) !important; /* Sombra interior (botón hundido) */
        border: 1px solid #14532d !important;
    }

    /* Opcional: Hacemos lo mismo para los botones normales/morados por si abres un chat de práctica */
    div[data-testid="stExpanderDetails"] div[data-testid="column"]:nth-child(1) button[kind="secondary"]:disabled {
        opacity: 1 !important;
        box-shadow: inset 0 4px 8px rgba(0, 0, 0, 0.5) !important; /* Efecto hundido */
        filter: brightness(0.85) !important; /* Lo oscurece un poquito para dar sensación de profundidad */
    }
            
    /* 10. BOTONES SUPERIORES (Perfil y Logout - Visibles y Grandes) */
    /* Regla general para hacerlos MÁS GRANDES (Alto y tamaño de emoji) */
    section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]:first-of-type button {
        padding: 15px 0px !important; /* Los hace mucho más altos */
        font-size: 28px !important; /* Hace que el emoji se vea gigante */
        line-height: 1 !important;
        border-radius: 12px !important;
        transition: all 0.2s ease-in-out !important;
    }

    /* Botón de PERFIL (Columna 2) -> Azul vibrante */
    section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="column"]:nth-child(2) button {
        background: linear-gradient(135deg, #3b82f6, #2563eb) !important; /* Azul eléctrico */
        border: 1px solid #60a5fa !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
    }
    
    section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="column"]:nth-child(2) button:hover {
        background: linear-gradient(135deg, #60a5fa, #3b82f6) !important; /* Más claro al pasar el ratón */
        transform: scale(1.08) !important; /* Efecto zoom */
    }

    /* Botón de SALIR (Columna 4) -> Rojo vibrante */
    section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="column"]:nth-child(4) button {
        background: linear-gradient(135deg, #ef4444, #dc2626) !important; /* Rojo vivo */
        border: 1px solid #f87171 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="column"]:nth-child(4) button:hover {
        background: linear-gradient(135deg, #f87171, #ef4444) !important; /* Más claro al pasar el ratón */
        transform: scale(1.08) !important; /* Efecto zoom */
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
            # IMPORTANTE: Importamos la nueva función del api_client
            from api_client import send_professor_test_message
            
            # Mandamos todo el historial acumulado en memoria RAM al backend
            ai_response = send_professor_test_message(case_id, st.session_state.preview_messages)
            response = ai_response["content"]
            
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.preview_messages.append({"role": "assistant", "content": response})

    st.stop()

# ====================================
# Interfaz del Alumno
# ====================================
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
        st.title(f"🧠 Virtual Patient: {patient_name}")
            
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
