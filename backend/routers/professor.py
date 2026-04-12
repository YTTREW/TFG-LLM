from datetime import datetime
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from backend.core.database import SessionLocal
from backend.models import Student, Chat, Message, ClinicalCase, Professor
from backend.core.security import get_password_hash

router = APIRouter(tags=["Profesor"])
templates = Jinja2Templates(directory="backend/templates")

############################################
#                                          #
#        ENDPOINTS DE PROFESORES           #
#                                          #
############################################

# Endpoint GET para cargar dashboard del profesor
@router.get("/dashboard-professor", response_class=HTMLResponse)
def dashboard_professor(request: Request):
    if "user" not in request.session:
        return RedirectResponse("/login", status_code=303)

    if request.session.get("role") != "professor":
        return RedirectResponse("/login", status_code=303)

    return templates.TemplateResponse(
        "professor/dashboard_professor.html",
        {
            "request": request,
            "username": request.session.get("user")
        }
    )

# Endpoint GET para listar estudiantes con chats enviados
@router.get("/professor/student/{student_id}/chats", response_class=HTMLResponse)
def view_student_chats(student_id: int, request: Request):
    if request.session.get("role") != "professor":
        return RedirectResponse("/login", status_code=303)
    
    db = SessionLocal()
    try:
        student = db.query(Student).filter_by(id=student_id).first()
        if not student:
            return HTMLResponse("Student not found", status_code=404)
        
        chats = db.query(Chat).filter_by(student_id=student_id, is_submitted=True).all()
    finally:
        db.close()
    
    return templates.TemplateResponse(
        "professor/student_chats.html",
        {
            "request": request,
            "student": student,
            "chats": chats,
            "role": "professor"
        }
    )

# Endpoint POST para crear un nuevo caso clínico
@router.get("/professor/student/{student_id}/chat/{chat_id}")
def open_chat(
    request: Request,
    student_id: int,
    chat_id: int
):
    if request.session.get("role") != "professor":
        return RedirectResponse("/login", status_code=303)

    db = SessionLocal()
    try:
        chat = db.query(Chat).filter_by(
            id=chat_id,
            student_id=student_id,
        ).first()

        if not chat:
            return {"error": "Chat not found", "status_code": 404}

        messages = db.query(Message).filter_by(
            chat_id=chat.id
        ).order_by(Message.id.asc()).all()

        return templates.TemplateResponse(
            "professor/chat_messages.html",
            {
                "request": request,
                "chat": chat,
                "messages": messages,
                "grade": chat.grade
            }
        )

    finally:
        db.close()

# Endpoint POST para asignar nota y feedback a un chat
@router.post("/professor/chat/{chat_id}/grade")
def assign_grade(
    request: Request,
    chat_id: int,
    grade: float = Form(...),
    feedback: str = Form(None)
):
    if request.session.get("role") != "professor":
        return RedirectResponse("/login", status_code=303)

    db = SessionLocal()
    try:
        chat = db.query(Chat).filter_by(id=chat_id).first()

        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        if grade < 0 or grade > 10:
            raise HTTPException(status_code=400, detail="Invalid grade")

        chat.grade = grade
        chat.feedback = feedback
        db.commit()

        return RedirectResponse(
            url=f"/professor/student/{chat.student_id}/chat/{chat.id}",
            status_code=303
        )

    finally:
        db.close()

# Endpoint GET para listar estudiantes con chats enviados
@router.get("/professor/create-case", response_class=HTMLResponse)
def create_case_form(request: Request):
    if request.session.get("role") != "professor": 
        return RedirectResponse("/login", status_code=303)
    
    return templates.TemplateResponse(
        "professor/create_case.html", 
        {
            "request": request
        }
    )

# Endpoint POST para crear un nuevo caso clínico
@router.post("/professor/create-case")
def create_case_post(
    request: Request, 
    patient_name: str = Form(...), 
    age: int = Form(...), 
    problem_description: str = Form(...), 
    is_evaluable: bool = Form(False),
    is_visible: bool = Form(False),     
    deadline: str = Form(None)
):
    if request.session.get("role") != "professor": 
        return RedirectResponse("/login", status_code=303)
    
    db = SessionLocal()
    try:
        username = request.session.get("user")
        professor = db.query(Professor).filter_by(username=username).first()
        
        if not professor:
            return RedirectResponse("/login", status_code=303)
        
        fecha_obj = None
        if deadline: 
            deadline_obj = datetime.strptime(deadline, "%Y-%m-%d").date()

        new_case = ClinicalCase(
            professor_id=professor.id,
            patient_name=patient_name,
            age=age,
            problem_description=problem_description,
            is_evaluable=is_evaluable,
            is_visible=is_visible,
            deadline=deadline_obj
        )
        
        db.add(new_case)
        db.commit()
        
        return RedirectResponse("/dashboard-professor", status_code=303)
    finally:
        db.close()

# Endpoint GET para listar casos clínicos del profesor
@router.get("/professor/cases", response_class=HTMLResponse)
def list_clinical_cases(request: Request):
    if request.session.get("role") != "professor": 
        return RedirectResponse("/login", status_code=303)
    
    db = SessionLocal()
    try:
        username = request.session.get("user")
        professor = db.query(Professor).filter_by(username=username).first()
        
        clinical_cases = db.query(ClinicalCase).filter_by(professor_id=professor.id).order_by(ClinicalCase.created_at.desc()).all()
    finally:
        db.close()
        
    return templates.TemplateResponse(
        "professor/list_cases.html", 
        {
            "request": request, 
            "cases": clinical_cases
        }
    )

# Endpoint POST para eliminar un caso clínico
@router.post("/professor/delete-case/{case_id}")
def delete_case(request: Request, case_id: int):
    if request.session.get("role") != "professor": 
        return RedirectResponse("/login", status_code=303)
    
    db = SessionLocal()
    try:
        username = request.session.get("user")
        professor = db.query(Professor).filter_by(username=username).first()
        
        clinical_case = db.query(ClinicalCase).filter_by(id=case_id, professor_id=professor.id).first()
        
        if clinical_case:
            db.delete(clinical_case)
            db.commit()
    finally:
        db.close()
        
    return RedirectResponse("/professor/cases", status_code=303)

# Endpoint GET para mostrar el formulario de edición de caso clínico
@router.get("/professor/edit-case/{case_id}", response_class=HTMLResponse)
def edit_case_form(case_id: int, request: Request):
    if request.session.get("role") != "professor":
        return RedirectResponse("/login")
        
    db = SessionLocal()
    try:
        clinical_case = db.query(ClinicalCase).filter(ClinicalCase.id == case_id).first()
        if not clinical_case:
            return HTMLResponse("Clinical case not found", status_code=404)
            
        return templates.TemplateResponse("professor/edit_case.html", {
            "request": request,
            "case": clinical_case
        })
    finally:
        db.close()

# Endpoint POST para GUARDAR los cambios
@router.post("/professor/edit-case/{case_id}")
def edit_case_post(
    case_id: int,
    request: Request,
    is_evaluable: bool = Form(False),
    is_visible: bool = Form(False),
    deadline: str = Form(None)
):
    if request.session.get("role") != "professor":
        return RedirectResponse("/login", status_code=303)
        
    db = SessionLocal()

    try:
        clinical_case = db.query(ClinicalCase).filter(ClinicalCase.id == case_id).first()
        if not clinical_case:
            return HTMLResponse("Clinical case not found", status_code=404)

        clinical_case.is_evaluable = is_evaluable
        clinical_case.is_visible = is_visible
        
        if deadline:
            clinical_case.deadline = datetime.strptime(deadline, "%Y-%m-%d").date()
        else:
            clinical_case.deadline = None 

        db.commit()
        
        return RedirectResponse("/professor/cases", status_code=303)
    finally:
        db.close()