from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .auth import authenticate_user, pwd_context
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, Estudiante, Profesor, SessionToken
from .database import engine
from starlette.middleware.sessions import SessionMiddleware
from .chats import router as chats_router

import os
import secrets

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    SessionMiddleware,
    secret_key="tg_key_123"
)
templates = Jinja2Templates(directory="backend/templates")
app.mount("/static", StaticFiles(directory="backend/static"), name="static")
app.include_router(chats_router)

# Carga variables del .env
load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(DATABASE_URL)
SessionLocal  = sessionmaker(bind=engine)

############################################
#                                          #
# ENDPOINTS DE AUTENTICACIÓN Y REGISTROS   #
#                                          #
############################################

# Endpoint GET para mostrar la página de login 
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Endpoint POST para autenticar al usuario y cargar su dashboard
@app.post("/login", response_class=HTMLResponse)
def login(  request: Request, username: str = Form(...), password: str = Form(...)):
    role = authenticate_user(username, password)

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

    db = SessionLocal()
    try:
        db.add(SessionToken(token=token, username=username))
        db.commit()
    finally:
        db.close()

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

# Endpoint GET para cerrar sesión
@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login")

# Endpoint GET para redirigir a la página principal
@app.get("/")
def root():
    return RedirectResponse(url="/login")

# Endpoint GET para carga página de registro
@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# Endpoint POST para registrar un nuevo usuario
@app.post("/register")
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
        hashed = pwd_context.hash(password)

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


############################################
#                                          #
#        ENDPOINTS DE PROFESORES           #
#                                          #
############################################

# Endpoint GET para cargar dashboard del profesor
@app.get("/dashboard-profesor", response_class=HTMLResponse)
def dashboard_profesor(request: Request):
    if "user" not in request.session:
        return RedirectResponse("/login")

    if request.session.get("role") != "profesor":
        return RedirectResponse("/login")

    username = request.session.get("user", "Professor")

    return templates.TemplateResponse(
        "dashboard_profesor.html",
        {
            "request": request,
            "username": username
        }
    )

############################################
#                                          #
#        ENDPOINTS DE ESTUDIANTES          #
#                                          #
############################################
@app.get("/dashboard-estudiante", response_class=HTMLResponse)
def dashboard_estudiante(request: Request):
    if "user" not in request.session:
        return RedirectResponse("/login")

    if request.session.get("role") != "estudiante":
        return RedirectResponse("/login")
    
    username = request.session.get("user", "Student")

    return templates.TemplateResponse(
        "dashboard_estudiante.html",
        {"request": request, "username": username}
    )

############################################
#                                          #
#       ENDPOINTS DE ADMINISTRADOR         #
#                                          #
############################################
# Endpoint GET para cargar dashboard del admin
@app.get("/dashboard-admin", response_class=HTMLResponse)
def dashboard_admin(request: Request):
    if "user" not in request.session:
        return RedirectResponse("/login")

    if request.session.get("role") != "admin":
        return RedirectResponse("/login")
    
    username = request.session.get("user", "Admin")

    return templates.TemplateResponse(
        "dashboard_admin.html",
        {"request": request, "username": username}
    )


# Endpoint GET para listar estudiantes
@app.get("/students", response_class=HTMLResponse)
def list_students(request: Request):

    if "user" not in request.session:
        return RedirectResponse("/login")

    role = request.session.get("role")
    if role not in ["profesor", "admin"]:
        return RedirectResponse("/login")

    db = SessionLocal()
    try:
        students = db.query(Estudiante).all()
    finally:
        db.close()

    return templates.TemplateResponse(
        "lista_estudiantes.html",
        {
            "request": request,
            "students": students, 
            "role": role
        }
    )

# Endpoint POST para eliminar estudiante
@app.post("/admin/delete-student/{student_id}")
def delete_student(student_id: int, request: Request):

    if request.session.get("role") != "admin":
        return RedirectResponse("/login")

    db = SessionLocal()
    try:
        student = db.query(Estudiante).filter_by(id=student_id).first()
        if student:
            db.delete(student)
            db.commit()
    finally:
        db.close()

    return RedirectResponse("/students", status_code=303)

# Endpoint GET para listar profesores
@app.get("/admin/professors", response_class=HTMLResponse)
def list_professors(request: Request):

    if "user" not in request.session:
        return RedirectResponse("/login")

    if request.session.get("role") != "admin":
        return RedirectResponse("/login")

    db = SessionLocal()
    try:
        professors = db.query(Profesor).all()
    finally:
        db.close()

    return templates.TemplateResponse(
        "lista_profesores.html",
        {
            "request": request,
            "professors": professors,
            "role": "admin"
        }
    )

# Endpoint POST para eliminar profesor
@app.post("/admin/delete-professor/{professor_id}")
def delete_professor(professor_id: int, request: Request):

    if request.session.get("role") != "admin":
        return RedirectResponse("/login")

    db = SessionLocal()
    try:
        professor = db.query(Profesor).filter_by(id=professor_id).first()
        if professor:
            db.delete(professor)
            db.commit()
    finally:
        db.close()

    return RedirectResponse("/admin/professors", status_code=303)

# Endpoint GET para cargar formulario de creación de usuarios
@app.get("/admin/register", response_class=HTMLResponse)
def create_user_form(request: Request):
    if request.session.get("role") != "admin":
        return RedirectResponse("/login")

    return templates.TemplateResponse(
        "register_users.html",
        {"request": request}
    )

# Endpoint POST para crear un nuevo usuario (profesor o estudiante)
@app.post("/admin/register")
def create_user(
    request: Request,
    nombre: str = Form(...),
    apellidos: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form(...)
):
    if request.session.get("role") != "admin":
        return RedirectResponse("/login")

    db = SessionLocal()
    try:
        hashed_password = pwd_context.hash(password)

        if role == "estudiante":
            user = Estudiante(
                username=username,
                password_hash=hashed_password,
                nombre=nombre,
                apellidos=apellidos,
                role="estudiante"
            )

        elif role == "profesor":
            user = Profesor(
                username=username,
                password_hash=hashed_password,
                nombre=nombre,
                apellidos=apellidos,
                role="profesor"
            )
        else:
            return {"error": "Invalid role"}

        db.add(user)
        db.commit()

    finally:
        db.close()

    return RedirectResponse("/dashboard-admin", status_code=303)
