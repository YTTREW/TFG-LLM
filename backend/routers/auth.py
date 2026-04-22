from aiohttp import request
from fastapi import APIRouter, Request, Form, Header, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from backend.core.database import SessionLocal
from backend.core.security import verify_password, get_password_hash
from backend.models.users import Student, Professor, Administrator, SessionToken

import secrets

router = APIRouter(tags=["Autenticación"])
templates = Jinja2Templates(directory="backend/templates")

# Verificar credenciales de usuario
def authenticate_user(username: str, password: str, db):
    professor = db.query(Professor).filter_by(username=username).first()
    if professor and verify_password(password, professor.password_hash):
        return "professor"

    student = db.query(Student).filter_by(username=username).first()
    if student and verify_password(password, student.password_hash):
        return "student"
    
    admin = db.query(Administrator).filter_by(username=username).first()
    if admin and verify_password(password, admin.password_hash):
        return "admin"

    return None

############################################
#                                          #
# ENDPOINTS DE AUTENTICACIÓN Y REGISTROS   #
#                                          #
############################################
# Endpoint GET para redirigir a la página principal
@router.get("/", response_class=RedirectResponse)
def root():
    return RedirectResponse(url="/login", status_code=303)

# Endpoint GET para mostrar la página de login 
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

# Endpoint POST para autenticar al usuario y cargar su dashboard
@router.post("/login", response_class=HTMLResponse)
def login(  request: Request, username: str = Form(...), password: str = Form(...)):
    db = SessionLocal()
    try:
        role = authenticate_user(username, password, db)
        if not role:
            return templates.TemplateResponse("auth/login.html", {
                "request": request,
                "error": "Incorrect username or password",
                "username": username  
            }, status_code=401)
        
        token = secrets.token_hex(16)
        
        request.session["user"] = username
        request.session["role"] = role
        request.session["token"] = token

        db.add(SessionToken(token=token, username=username))
        db.commit()

        if role == "student":
            return RedirectResponse(
                url=f"http://localhost:8501?token={token}",
                status_code=303
            )
        elif role == "admin":
            return RedirectResponse("/dashboard-admin", status_code=303)
        else:
            return RedirectResponse("/dashboard-professor", status_code=303)

    finally:
        db.close()

# Endpoint GET para cerrar sesión
@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)

# Endpoint GET para cargar página de registro
@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})

# Endpoint POST para registrar un nuevo usuario
@router.post("/register")
def register_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    surname: str = Form(...),
):
    db = SessionLocal()
    try:
        existing_user = db.query(Student).filter_by(username=username).first()
        if existing_user:
            return templates.TemplateResponse("auth/register.html", {
                "request": request,
                "error": "Username already exists."
            }, status_code=400)
        
        hashed = get_password_hash(password)

        student = Student(
                username=username,
                password_hash=hashed,
                name=name,
                surname=surname,
                role="student"
            )
        db.add(student)
        db.commit()
    finally:
        db.close() 

    return RedirectResponse("/login", status_code=303)

# Endpoint GET para cargar formulario de edición de perfil
@router.get("/edit-profile", response_class=HTMLResponse)
def edit_profile_form(request: Request):
    role = request.session.get("role")

    if role not in ["professor", "student"]: 
        return RedirectResponse("/login")
    
    current_username = request.session.get("user")
    
    db = SessionLocal()
    model = Professor if role == "professor" else Student
    user_obj = db.query(model).filter_by(username=current_username).first()
    db.close()
    
    if not user_obj:
        return RedirectResponse("/login")
    
    if role == "professor":
        back_url = "/dashboard-professor"
        back_text = "Back to Dashboard"
    else:
        token = request.session.get("token")
        back_url = f"http://localhost:8501?token={token}"
        back_text = "Back to Menu"

    return templates.TemplateResponse("auth/edit_profile.html", {
        "request": request, 
        "user": user_obj,
        "action_url": "/edit-profile",
        "back_url": back_url,
        "back_text": back_text
    })

# Endpoint POST para actualizar el perfil del usuario
@router.post("/edit-profile")
def edit_profile_post(
    request: Request,
    new_username: str = Form(...),
    new_password: str = Form(None)
):
    role = request.session.get("role")
    if role not in ["professor", "student"]: 
        return RedirectResponse("/login", status_code=303)
    
    db = SessionLocal()
    new_data = False  
    
    try:
        current_username = request.session.get("user")

        model = Professor if role == "professor" else Student
        user = db.query(model).filter_by(username=current_username).first()
        
        if not user:
            return RedirectResponse("/login", status_code=303)

        if new_username != current_username:
            existing_user = db.query(model).filter_by(username=new_username).first()
            if existing_user:
                if role == "professor":
                    back_url = "/dashboard-professor"
                else:
                    token = request.session.get("token")
                    back_url = f"http://localhost:8501?token={token}"

                return templates.TemplateResponse("auth/edit_profile.html", {
                    "request": request, 
                    "current_username": current_username,
                    "error": "This username is already taken.",
                    "action_url": "/edit-profile",
                    "back_url": back_url,
                    "back_text": "Back to Menu" if role == "student" else "Back to Dashboard"
                }, status_code=400)
            
            user.username = new_username
            request.session["user"] = new_username
            new_data = True  

        if new_password and new_password.strip() != "":
            user.password_hash = get_password_hash(new_password)
            new_data = True  
            
        db.commit()
    finally:
        db.close()

    if new_data:
        request.session.clear() 
        return RedirectResponse("/login", status_code=303)
    else:
        if role == "professor":
            return RedirectResponse("/dashboard-professor", status_code=303)
        else:
            token = request.session.get("token")
            return RedirectResponse(f"http://localhost:8501?token={token}", status_code=303)