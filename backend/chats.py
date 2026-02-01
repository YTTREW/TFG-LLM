from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models import Estudiante, Chat, Message, SessionToken
from fastapi import Depends, Header, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/chats", tags=["Chats"])
class MessageCreate(BaseModel):
    role: str
    content: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from fastapi import Header, HTTPException

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
def save_message(
    chat_id: int,
    message: MessageCreate,
    db: Session = Depends(get_db),
    student: Estudiante = Depends(get_current_student)
):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.estudiante_id == student.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    new_msg = Message(chat_id=chat.id, role=message.role, content=message.content)
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)

    return {
        "id": new_msg.id,
        "chat_id": new_msg.chat_id,
        "role": new_msg.role,
        "content": new_msg.content
    }