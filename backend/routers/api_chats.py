from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.core.database import get_db
from backend.models import Estudiante, Chat, Message, SessionToken
from backend.services import llm_service

router = APIRouter(prefix="/api/chats", tags=["API de Chats"])

class MessageCreate(BaseModel):
    content: str

#Obtener estudiante actual
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

#Listar chats
@router.get("/")
def list_chats(
    student: Estudiante = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    chats = (
        db.query(Chat)
        .filter(Chat.estudiante_id == student.id)
        .order_by(Chat.created_at.desc())
        .all()
    )

    return [
        {
            "id": chat.id,
            "title": chat.title,
            "created_at": chat.created_at.isoformat()
        }
        for chat in chats
    ]

#Crear nuevo chat
@router.post("/")
def create_chat(
    student: Estudiante = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    chat = Chat(
        estudiante_id=student.id,
        title="New chat"
    )

    db.add(chat)
    db.commit()
    db.refresh(chat)

    return {
        "id": chat.id,
        "title": chat.title
    }

@router.get("/{chat_id}")
def get_chat_messages(
    chat_id: int,
    db: Session = Depends(get_db),
    student: Estudiante = Depends(get_current_student)
):
    # Buscar chat del estudiante
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.estudiante_id == student.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Devolver los mensajes
    return [
        {
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at.isoformat()
        }
        for msg in chat.messages
    ]

@router.post("/{chat_id}/messages")
def send_message(
    chat_id: int,
    message: MessageCreate,
    db: Session = Depends(get_db),
    student: Estudiante = Depends(get_current_student)
):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.estudiante_id == student.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    user_msg = Message(chat_id=chat.id, role="user", content=message.content)
    db.add(user_msg)
    db.commit()

    # 2. Recuperar el historial de la conversación (incluyendo el mensaje que acabamos de guardar)
    chat_history = db.query(Message).filter(Message.chat_id == chat.id).order_by(Message.id.asc()).all()

    # 3. Llamar al servicio de LLM pasándole el historial
    ia_response_text = llm_service.get_response(chat_history)

    # 4. Guardar la respuesta de la IA en la Base de Datos
    ia_msg = Message(chat_id=chat.id, role="assistant", content=ia_response_text)
    db.add(ia_msg)
    db.commit()

    return {
        "role": ia_msg.role,
        "content": ia_msg.content,
        "created_at": ia_msg.created_at.isoformat()
    }

@router.delete("/{chat_id}")
def delete_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    student: Estudiante = Depends(get_current_student)
):
    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.estudiante_id == student.id
    ).first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    db.query(Message).filter(Message.chat_id == chat.id).delete()

    db.delete(chat)
    db.commit()

    return {"message": "Chat deleted successfully"}


