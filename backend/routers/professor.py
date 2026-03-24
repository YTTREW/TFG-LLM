from datetime import datetime
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from backend.core.database import SessionLocal
from backend.models import Estudiante, Chat, Message, CasoClinico, Profesor
from backend.core.security import get_password_hash

router = APIRouter(tags=["Profesor"])
templates = Jinja2Templates(directory="backend/templates/professor")

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
        
        chats = db.query(Chat).filter_by(estudiante_id=student_id, enviado=True).all()
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
            estudiante_id=student_id,
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
    grade: float = Form(...),
    feedback: str = Form(None)
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
        chat.feedback = feedback
        db.commit()

        return RedirectResponse(
            url=f"/professor/student/{chat.estudiante_id}/chat/{chat.id}",
            status_code=303
        )

    finally:
        db.close()

@router.get("/professor/create-case", response_class=HTMLResponse)
def create_case_form(request: Request):
    if request.session.get("role") != "profesor": 
        return RedirectResponse("/login")
    
    return templates.TemplateResponse(
        "create_case.html", 
        {
            "request": request
        }
    )

@router.post("/professor/create-case")
def create_case_post(
    request: Request, 
    nombre_paciente: str = Form(...), 
    edad: int = Form(...), 
    problema_descripcion: str = Form(...), 
    es_evaluable: bool = Form(False),
    visible: bool = Form(False),      # NUEVO
    fecha_entrega: str = Form(None)
):
    if request.session.get("role") != "profesor": 
        return RedirectResponse("/login")
    
    db = SessionLocal()
    try:
        # 1. Buscamos quién es el profesor que está creando el caso
        username = request.session.get("user")
        profesor = db.query(Profesor).filter_by(username=username).first()
        
        if not profesor:
            return RedirectResponse("/login")
        
        fecha_obj = None
        if fecha_entrega: # Si el profesor ha rellenado la fecha
            fecha_obj = datetime.strptime(fecha_entrega, "%Y-%m-%d").date()

        # 2. Creamos el nuevo caso clínico
        nuevo_caso = CasoClinico(
            profesor_id=profesor.id,
            nombre_paciente=nombre_paciente,
            edad=edad,
            problema_descripcion=problema_descripcion,
            es_evaluable=es_evaluable,
            visible=visible,
            fecha_entrega=fecha_obj
        )
        
        # 3. Lo guardamos en la base de datos
        db.add(nuevo_caso)
        db.commit()
        
        # Redirigimos al panel del profesor
        return RedirectResponse("/dashboard-profesor", status_code=303)
    finally:
        db.close()

@router.get("/professor/cases", response_class=HTMLResponse)
def list_clinical_cases(request: Request):
    if request.session.get("role") != "profesor": 
        return RedirectResponse("/login")
    
    db = SessionLocal()
    try:
        # Buscamos al profesor actual
        username = request.session.get("user")
        profesor = db.query(Profesor).filter_by(username=username).first()
        
        # Obtenemos solo los casos que ha creado este profesor
        casos = db.query(CasoClinico).filter_by(profesor_id=profesor.id).order_by(CasoClinico.created_at.desc()).all()
    finally:
        db.close()
        
    return templates.TemplateResponse(
        "lista_casos.html", 
        {
            "request": request, 
            "casos": casos
        }
    )

@router.post("/professor/delete-case/{caso_id}")
def delete_case(request: Request, caso_id: int):
    if request.session.get("role") != "profesor": 
        return RedirectResponse("/login")
    
    db = SessionLocal()
    try:
        username = request.session.get("user")
        profesor = db.query(Profesor).filter_by(username=username).first()
        
        # Buscamos el caso asegurándonos de que pertenece a este profesor por seguridad
        caso = db.query(CasoClinico).filter_by(id=caso_id, profesor_id=profesor.id).first()
        
        if caso:
            db.delete(caso)
            db.commit()
    finally:
        db.close()
        
    return RedirectResponse("/professor/cases", status_code=303)


@router.get("/professor/edit-case/{caso_id}", response_class=HTMLResponse)
def edit_case_form(caso_id: int, request: Request):
    if request.session.get("role") != "profesor":
        return RedirectResponse("/login")
        
    db = SessionLocal()
    try:
        # Buscamos el caso. (Podríamos verificar también si pertenece al profe logueado por seguridad)
        caso = db.query(CasoClinico).filter(CasoClinico.id == caso_id).first()
        if not caso:
            return HTMLResponse("Clinical case not found", status_code=404)
            
        return templates.TemplateResponse("edit_case.html", {
            "request": request,
            "caso": caso
        })
    finally:
        db.close()

# Endpoint para GUARDAR los cambios
@router.post("/professor/edit-case/{caso_id}")
def edit_case_post(
    caso_id: int,
    request: Request,
    es_evaluable: bool = Form(False),
    visible: bool = Form(False),
    fecha_entrega: str = Form(None)
):
    if request.session.get("role") != "profesor":
        return RedirectResponse("/login")
        
    db = SessionLocal()
    try:
        caso = db.query(CasoClinico).filter(CasoClinico.id == caso_id).first()
        if not caso:
            return HTMLResponse("Clinical case not found", status_code=404)

        # Actualizamos los booleanos
        caso.es_evaluable = es_evaluable
        caso.visible = visible
        
        # Procesamos la fecha
        if fecha_entrega:
            caso.fecha_entrega = datetime.strptime(fecha_entrega, "%Y-%m-%d").date()
        else:
            caso.fecha_entrega = None # Si el profe borra la fecha, la quitamos

        db.commit()
        
        # Devolvemos a la lista de casos
        return RedirectResponse("/professor/cases", status_code=303)
    finally:
        db.close()