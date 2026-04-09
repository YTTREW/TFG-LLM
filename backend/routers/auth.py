from fastapi import APIRouter, Request, Form, Header, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from backend.core.database import SessionLocal
from backend.core.security import verify_password, get_password_hash
from backend.models.users import Estudiante, Profesor, Administrador, SessionToken

import secrets

router = APIRouter(tags=["Autenticación"])
templates = Jinja2Templates(directory="backend/templates")

# Verificar credenciales de usuario
def authenticate_user(username: str, password: str, db):
    profesor = db.query(Profesor).filter_by(username=username).first()
    if profesor and verify_password(password, profesor.password_hash):
        return "profesor"

    estudiante = db.query(Estudiante).filter_by(username=username).first()
    if estudiante and verify_password(password, estudiante.password_hash):
        return "estudiante"
    
    admin = db.query(Administrador).filter_by(username=username).first()
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
    return templates.TemplateResponse("login.html", {"request": request})

# Endpoint POST para autenticar al usuario y cargar su dashboard
@router.post("/login", response_class=HTMLResponse)
def login(  request: Request, username: str = Form(...), password: str = Form(...)):
    db = SessionLocal()
    try:
        role = authenticate_user(username, password, db)
        if not role:
            return templates.TemplateResponse("login.html", {
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

        if role == "estudiante":
            return RedirectResponse(
                url=f"http://localhost:8501?token={token}",
                status_code=303
            )
        elif role == "admin":
            return RedirectResponse("/dashboard-admin", status_code=303)
        else:
            return RedirectResponse("/dashboard-profesor", status_code=303)

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
    return templates.TemplateResponse("register.html", {"request": request})

# Endpoint POST para registrar un nuevo usuario
@router.post("/register")
def register_user(
     request: Request,
    username: str = Form(...),
    password: str = Form(...),
    nombre: str = Form(...),
    apellidos: str = Form(...),
):
    db = SessionLocal()
    try:
        existing_user = db.query(Estudiante).filter_by(username=username).first()
        if existing_user:
            return templates.TemplateResponse("register.html", {
                "request": request,
                "error": "Username already exists."
            }, status_code=400)
        
        hashed = get_password_hash(password)

        estudiante = Estudiante(
                username=username,
                password_hash=hashed,
                nombre=nombre,
                apellidos=apellidos,
                role="estudiante"
            )
        db.add(estudiante)
        db.commit()
    finally:
        db.close() 

    return RedirectResponse("/login", status_code=303)

@router.get("/edit-profile", response_class=HTMLResponse)
def edit_profile_form(request: Request):
    role = request.session.get("role")

    if role not in ["profesor", "estudiante"]: 
        return RedirectResponse("/login")
    
    current_username = request.session.get("user")

    if role == "profesor":
        back_url = "/dashboard-profesor"
        back_text = "Back to Dashboard"
    else:
        token = request.session.get("token")
        back_url = f"http://localhost:8501?token={token}"
        back_text = "Back to Menu"

    return templates.TemplateResponse("edit_profile.html", {
        "request": request, 
        "current_username": current_username,
        "action_url": "/edit-profile",
        "back_url": back_url,
        "back_text": back_text
    })

@router.post("/edit-profile")
def edit_profile_post(
    request: Request,
    new_username: str = Form(...),
    new_password: str = Form(None)
):
    role = request.session.get("role")
    if role not in ["profesor", "estudiante"]: 
        return RedirectResponse("/login", status_code=303)
    
    db = SessionLocal()
    cambios_realizados = False  
    
    try:
        current_username = request.session.get("user")

        Modelo = Profesor if role == "profesor" else Estudiante
        usuario = db.query(Modelo).filter_by(username=current_username).first()
        
        if not usuario:
            return RedirectResponse("/login", status_code=303)

        if new_username != current_username:
            usuario_existente = db.query(Modelo).filter_by(username=new_username).first()
            if usuario_existente:
                if role == "profesor":
                    back_url = "/dashboard-profesor"
                else:
                    token = request.session.get("token")
                    back_url = f"http://localhost:8501?token={token}"

                return templates.TemplateResponse("edit_profile.html", {
                    "request": request, 
                    "current_username": current_username,
                    "error": "This username is already taken.",
                    "action_url": "/edit-profile",
                    "back_url": back_url,
                    "back_text": "Back to Menu" if role == "estudiante" else "Back to Dashboard"
                }, status_code=400)
            
            usuario.username = new_username
            request.session["user"] = new_username
            cambios_realizados = True  # 

        if new_password and new_password.strip() != "":
            usuario.password_hash = get_password_hash(new_password)
            cambios_realizados = True  
            
        db.commit()
    finally:
        db.close()

    if cambios_realizados:
        request.session.clear() 
        return RedirectResponse("/login", status_code=303)
    else:
        if role == "profesor":
            return RedirectResponse("/dashboard-profesor", status_code=303)
        else:
            token = request.session.get("token")
            return RedirectResponse(f"http://localhost:8501?token={token}", status_code=303)