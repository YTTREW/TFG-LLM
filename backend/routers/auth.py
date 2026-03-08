from fastapi import APIRouter, Request, Form, Header, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import secrets

# Importamos desde nuestras nuevas carpetas core y models
from backend.core.database import SessionLocal
from backend.core.security import verify_password, get_password_hash
from backend.models.users import Estudiante, Profesor, Administrador, SessionToken

router = APIRouter(tags=["Autenticación"])
templates = Jinja2Templates(directory="backend/templates")

def authenticate_user(username: str, password: str, db):
    # Buscar en profesores
    profesor = db.query(Profesor).filter_by(username=username).first()
    if profesor and verify_password(password, profesor.password_hash):
        return "profesor"

    # Buscar en estudiantes
    estudiante = db.query(Estudiante).filter_by(username=username).first()
    if estudiante and verify_password(password, estudiante.password_hash):
        return "estudiante"
    
    # Buscar en administradores
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
    return RedirectResponse(url="/login")

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
            })
        
        # Generar token de sesión
        token = secrets.token_hex(16)
        
        request.session["user"] = username
        request.session["role"] = role
        request.session["token"] = token

        db.add(SessionToken(token=token, username=username))
        db.commit()

        # Verificar rol
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
    return RedirectResponse("/login")

# Endpoint GET para carga página de registro
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
        # Comprobar si ya existe
        existing_user = db.query(Estudiante).filter_by(username=username).first()
        if existing_user:
            return templates.TemplateResponse("register.html", {
                "request": request,
                "error": "Username already exists."
            })
        # Crear hash de la contraseña
        hashed = get_password_hash(password)

        # Crear usuario y guardar
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