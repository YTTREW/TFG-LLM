from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from backend.core.database import SessionLocal
from backend.models import Estudiante, Chat, Message

router = APIRouter(tags=["Profesor"])
templates = Jinja2Templates(directory="backend/templates")

############################################
#                                          #
#        ENDPOINTS DE PROFESORES           #
#                                          #
############################################

# Endpoint GET para cargar dashboard del profesor
@router.get("/dashboard-profesor", response_class=HTMLResponse)
def dashboard_profesor(request: Request):
    if "user" not in request.session:
        return RedirectResponse("/login")

    if request.session.get("role") != "profesor":
        return RedirectResponse("/login")

    return templates.TemplateResponse(
        "dashboard_profesor.html",
        {
            "request": request,
            "username": request.session.get("user")
        }
    )

@router.get("/professor/student/{student_id}/chats", response_class=HTMLResponse)
def view_student_chats(student_id: int, request: Request):
    if request.session.get("role") != "profesor":
        return RedirectResponse("/login")
    
    db = SessionLocal()
    try:
        student = db.query(Estudiante).filter_by(id=student_id).first()
        if not student:
            return HTMLResponse("Student not found", status_code=404)
        
        chats = db.query(Chat).filter_by(estudiante_id=student_id).all()
    finally:
        db.close()
    
    return templates.TemplateResponse(
        "student_chats.html",
        {
            "request": request,
            "student": student,
            "chats": chats,
            "role": "profesor"
        }
    )

@router.get("/professor/student/{student_id}/chat/{chat_id}")
def open_chat(
    request: Request,
    student_id: int,
    chat_id: int
):
    if request.session.get("role") != "profesor":
        return RedirectResponse("/login", status_code=303)

    db = SessionLocal()
    try:
        chat = db.query(Chat).filter_by(
            id=chat_id,
            estudiante_id=student_id
        ).first()


        if not chat:
            return {"error": "Chat not found"}

        messages = db.query(Message).filter_by(
            chat_id=chat.id
        ).order_by(Message.id.asc()).all()

        return templates.TemplateResponse(
            "chat_messages.html",
            {
                "request": request,
                "chat": chat,
                "messages": messages,
                "grade": chat.grade
            }
        )

    finally:
        db.close()

@router.post("/professor/chat/{chat_id}/grade")
def assign_grade(
    request: Request,
    chat_id: int,
    grade: float = Form(...)
):
    if request.session.get("role") != "profesor":
        return RedirectResponse("/login", status_code=303)

    db = SessionLocal()
    try:
        chat = db.query(Chat).filter_by(id=chat_id).first()

        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        if grade < 0 or grade > 10:
            raise HTTPException(status_code=400, detail="Invalid grade")

        chat.grade = grade
        db.commit()

        return RedirectResponse(
            url=f"/professor/student/{chat.estudiante_id}/chat/{chat.id}",
            status_code=303
        )

    finally:
        db.close()
