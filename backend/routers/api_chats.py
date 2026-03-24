from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from backend.core.database import get_db
from backend.models import Estudiante, Chat, Message, SessionToken, CasoClinico
from backend.services.llm_service import LLMService

router = APIRouter(prefix="/api/chats", tags=["API de Chats"])

# === AQUÍ ESTÁ LA MAGIA: CREAMOS LA INSTANCIA DE LA IA A NIVEL GLOBAL ===
llm_model = LLMService()

class MessageCreate(BaseModel):
    content: str

class ChatCreate(BaseModel):
    caso_id: int

# --- FUNCIONES DE AUTENTICACIÓN ---
def get_current_student(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = authorization.replace("Bearer ", "")
    session = db.query(SessionToken).filter_by(token=token).first()
    if not session:
        raise HTTPException(status_code=401, detail="Invalid token")

    student = db.query(Estudiante).filter_by(username=session.username).first()
    if not student:
        raise HTTPException(status_code=401, detail="User not found")

    return student

# --- ENDPOINTS ---

@router.get("/cases")
def get_cases(db: Session = Depends(get_db), student: Estudiante = Depends(get_current_student)):
    casos = db.query(CasoClinico).filter(CasoClinico.visible == True).all()

    resultado = []
    for caso in casos:
        resultado.append({
            "id": caso.id,
            "nombre_paciente": caso.nombre_paciente,
            "es_evaluable": caso.es_evaluable,
            "fecha_entrega": caso.fecha_entrega.isoformat() if caso.fecha_entrega else None
        })
    return resultado

@router.get("/")
def get_chats(db: Session = Depends(get_db), student: Estudiante = Depends(get_current_student)):
    chats = db.query(Chat).filter_by(estudiante_id=student.id).order_by(Chat.created_at.desc()).all()
    return [{"id": chat.id, "title": chat.title, "caso_id": chat.caso_id, "created_at": chat.created_at, "enviado": chat.enviado, "grade": chat.grade, "feedback": chat.feedback} for chat in chats]

@router.post("/{chat_id}/submit")
def submit_chat(chat_id: int, db: Session = Depends(get_db), student: Estudiante = Depends(get_current_student)):
    chat_a_enviar = db.query(Chat).filter(Chat.id == chat_id, Chat.estudiante_id == student.id).first()
    if not chat_a_enviar:
        raise HTTPException(status_code=404, detail="Chat not found")

    # 2. MAGIA: Buscamos TODOS los demás chats de este mismo caso y los desmarcamos (enviado = False)
    db.query(Chat).filter(
        Chat.estudiante_id == student.id,
        Chat.caso_id == chat_a_enviar.caso_id,
        Chat.id != chat_id 
    ).update({"enviado": False})

    chat_a_enviar.enviado = True
    db.commit()

    return {"message": "Chat submitted successfully"}




@router.post("/")
def create_chat(chat_data: ChatCreate, db: Session = Depends(get_db), student: Estudiante = Depends(get_current_student)):
    caso = db.query(CasoClinico).filter_by(id=chat_data.caso_id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso clínico no encontrado")

    prefijo = "Evaluable: " if caso.es_evaluable else "Simulación: "
    titulo_chat = f"{prefijo}{caso.nombre_paciente}"

    nuevo_chat = Chat(estudiante_id=student.id, caso_id=caso.id, title=titulo_chat)
    db.add(nuevo_chat)
    db.commit()
    db.refresh(nuevo_chat)

    return {"id": nuevo_chat.id, "title": nuevo_chat.title, "caso_id": nuevo_chat.caso_id}

@router.get("/{chat_id}")
def get_chat_messages(chat_id: int, db: Session = Depends(get_db), student: Estudiante = Depends(get_current_student)):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.estudiante_id == student.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    return [{"role": msg.role, "content": msg.content, "created_at": msg.created_at.isoformat()} for msg in chat.messages]

@router.post("/{chat_id}/messages")
def send_message(chat_id: int, message: MessageCreate, db: Session = Depends(get_db), student: Estudiante = Depends(get_current_student)):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.estudiante_id == student.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    user_msg = Message(chat_id=chat.id, role="user", content=message.content)
    db.add(user_msg)
    db.commit()

    chat_history = db.query(Message).filter(Message.chat_id == chat.id).order_by(Message.id.asc()).all()
    
    caso = db.query(CasoClinico).filter(CasoClinico.id == chat.caso_id).first()

    # === AQUÍ USAMOS LA INSTANCIA GLOBAL ===
    ia_response_text = llm_model.get_response(
        chat_history=chat_history,
        nombre_paciente=caso.nombre_paciente,
        edad=caso.edad,
        problema=caso.problema_descripcion
    )

    ia_msg = Message(chat_id=chat.id, role="assistant", content=ia_response_text)
    db.add(ia_msg)
    db.commit()

    return {"role": ia_msg.role, "content": ia_msg.content, "created_at": ia_msg.created_at.isoformat()}

@router.delete("/{chat_id}")
def delete_chat(chat_id: int, db: Session = Depends(get_db), student: Estudiante = Depends(get_current_student)):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.estudiante_id == student.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    db.query(Message).filter(Message.chat_id == chat.id).delete()
    db.delete(chat)
    db.commit()

    return {"message": "Chat deleted successfully"}