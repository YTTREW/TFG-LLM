from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from backend.core.database import get_db
from backend.models import Student, Chat, Message, SessionToken, ClinicalCase
from backend.services.llm_service import LLMService

router = APIRouter(prefix="/api/chats", tags=["API de Chats"])

llm_model = LLMService()

class MessageCreate(BaseModel):
    content: str

class ChatCreate(BaseModel):
    clinical_case_id: int

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

    student = db.query(Student).filter_by(username=session.username).first()
    if not student:
        raise HTTPException(status_code=401, detail="User not found")

    return student

############################################
#                                          #
# ENDPOINTS DE CHATS                       #
#                                          #
############################################

# Endpoint para obtener todos los casos clínicos disponibles
@router.get("/cases")
def get_cases(db: Session = Depends(get_db), student: Student = Depends(get_current_student)):
    cases = db.query(ClinicalCase).filter(ClinicalCase.is_visible == True).all()

    result = []
    for case in cases:
        result.append({
            "id": case.id,
            "patient_name": case.patient_name,
            "is_evaluable": case.is_evaluable,
            "delivery_date": case.deadline.isoformat() if case.deadline else None
        })
    return result

# Endpoint para obtener todos los chats del estudiante
@router.get("/")
def get_chats(db: Session = Depends(get_db), student: Student = Depends(get_current_student)):
    chats = db.query(Chat).filter_by(student_id=student.id).order_by(Chat.created_at.desc()).all()
    return [
        {
            "id": chat.id, 
            "title": chat.title,
            "clinical_case_id": chat.clinical_case_id,
            "created_at": chat.created_at, 
            "is_submitted": chat.is_submitted, 
            "grade": chat.grade, 
            "feedback": chat.feedback
        } for chat in chats
    ]

# Endpoint para marcar un chat como enviado
@router.post("/{chat_id}/submit")
def submit_chat(chat_id: int, db: Session = Depends(get_db), student: Student = Depends(get_current_student)):
    chat_to_submit = db.query(Chat).filter(Chat.id == chat_id, Chat.student_id == student.id).first()

    if not chat_to_submit:
        raise HTTPException(status_code=404, detail="Chat not found")

    db.query(Chat).filter(
        Chat.student_id == student.id,
        Chat.clinical_case_id == chat_to_submit.clinical_case_id,
        Chat.id != chat_id 
    ).update({"is_submitted": False})

    chat_to_submit.is_submitted = True
    db.commit()

    return {"message": "Chat submitted successfully"}


# Endpoint para crear un nuevo chat basado en un caso clínico específico
@router.post("/")
def create_chat(chat_data: ChatCreate, db: Session = Depends(get_db), student: Student = Depends(get_current_student)):
    clinical_case = db.query(ClinicalCase).filter_by(id=chat_data.clinical_case_id).first()
    if not clinical_case:
        raise HTTPException(status_code=404, detail="Caso clínico no encontrado")

    prefix = "Evaluable: " if clinical_case.is_evaluable else "Simulation: "
    chat_title = f"{prefix}{clinical_case.patient_name}"

    new_chat = Chat(student_id=student.id, clinical_case_id=clinical_case.id, title=chat_title)
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)

    return {"id": new_chat.id, "title": new_chat.title, "clinical_case_id": new_chat.clinical_case_id}

# Endpoint para obtener los mensajes de un chat específico
@router.get("/{chat_id}")
def get_chat_messages(chat_id: int, db: Session = Depends(get_db), student: Student = Depends(get_current_student)):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.student_id == student.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    return [{"role": msg.role, "content": msg.content, "created_at": msg.created_at.isoformat()} for msg in chat.messages]

# Endpoint para enviar un mensaje en un chat específico 
@router.post("/{chat_id}/messages")
def send_message(chat_id: int, message: MessageCreate, db: Session = Depends(get_db), student: Student = Depends(get_current_student)):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.student_id == student.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    user_msg = Message(chat_id=chat.id, role="user", content=message.content)
    db.add(user_msg)
    db.commit()

    chat_history = db.query(Message).filter(Message.chat_id == chat.id).order_by(Message.id.asc()).all()
    
    clinical_case = db.query(ClinicalCase).filter(ClinicalCase.id == chat.clinical_case_id).first()

    ia_response_text = llm_model.get_response(
        chat_history=chat_history,
        patient_name=clinical_case.patient_name,
        age=clinical_case.age,
        problem_description=clinical_case.problem_description
    )

    ia_msg = Message(chat_id=chat.id, role="assistant", content=ia_response_text)
    db.add(ia_msg)
    db.commit()

    return {"role": ia_msg.role, "content": ia_msg.content, "created_at": ia_msg.created_at.isoformat()}

# Endpoint para eliminar un chat específico
@router.delete("/{chat_id}")
def delete_chat(chat_id: int, db: Session = Depends(get_db), student: Student = Depends(get_current_student)):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.student_id == student.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    db.query(Message).filter(Message.chat_id == chat.id).delete()
    db.delete(chat)
    db.commit()

    return {"message": "Chat deleted successfully"}