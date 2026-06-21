from datetime import datetime
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from backend.core.database import SessionLocal
from backend.models import Student, Chat, Message, ClinicalCase, Professor
from backend.core.security import get_password_hash
from backend.services.llm_service import LLMService

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

# Endpoint GET para mostrar el formulario de evaluación de un chat
@router.get("/professor/chat/{chat_id}/evaluate") 
def show_evaluation_form(
    chat_id: int, 
    request: Request
):
    if request.session.get("role") != "professor":
        return RedirectResponse("/login", status_code=303)

    db = SessionLocal()
    try:
        chat = db.query(Chat).filter_by(id=chat_id).first()
        if not chat:
            return HTMLResponse("Chat not found", status_code=404)
        
        return templates.TemplateResponse(
            "professor/evaluate_chat.html", 
            {"request": request, "chat": chat}
        )
    finally:
        db.close() 

# Endpoint POST para procesar calcular la nota
@router.post("/professor/chat/{chat_id}/submit-evaluation")
def submit_evaluation(
    request: Request,
    chat_id: int,
    q1: int = Form(...),
    q2: int = Form(...),
    q3: int = Form(...),
    q4: int = Form(...),
    q5: int = Form(...),
    q6: int = Form(...),
    q7: int = Form(...),
    q8: int = Form(...),
    q9: int = Form(...),
    q10: int = Form(...),
    q11: int = Form(...),
    q12: int = Form(...),
    q13: int = Form(...),
    q14: int = Form(...),
    q15: int = Form(...),
    q16: int = Form(...),
    global_feedback: str = Form(None)
):
    if request.session.get("role") != "professor":
        return RedirectResponse("/login", status_code=303)

    db = SessionLocal()
    try:
        chat = db.query(Chat).filter_by(id=chat_id).first()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        respuestas = [q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16]
        media = sum(respuestas) / len(respuestas)

 
        nota_final = round((media - 1) * 2.5, 1)

        if nota_final.is_integer():
            nota_final = int(nota_final)

        chat.grade = nota_final
        chat.feedback = global_feedback
        
        db.commit()

        return RedirectResponse(
            url=f"/professor/student/{chat.student_id}/chats", 
            status_code=303
        )

    finally:
        db.close()

# Endpoint POST para usar el chat de prueba del profesor
@router.post("/professor/test-chat")
def professor_test_chat(
    request: Request,
    case_id: int = Form(...),
    history: str = Form(...)  
):

    import json
    historial_lista = json.loads(history)

    class MessageDictToObject:
        def __init__(self, role, content):
            self.role = role
            self.content = content

    db = SessionLocal()
    try:
        clinical_case = db.query(ClinicalCase).filter_by(id=case_id).first()
        if not clinical_case:
            raise HTTPException(status_code=404, detail="Clinical case not found")

        history_objects = [
            MessageDictToObject(msg["role"], msg["content"]) 
            for msg in historial_lista 
            if msg.get("role") != "system"
        ]

        llm_service = LLMService()

        ai_content = llm_service.get_response(
            chat_history=history_objects,
            patient_name=clinical_case.patient_name,
            age=clinical_case.age,
            problem_description=clinical_case.problem_description
        )

        return {"role": "assistant", "content": ai_content}

    except Exception as e:
        return {"role": "assistant", "content": f"⚠️ LLM Error: {str(e)}"}
    finally:
        db.close()