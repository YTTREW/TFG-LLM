from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .auth import authenticate_user, pwd_context
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import User, Base
import os

app = FastAPI()

templates = Jinja2Templates(directory="backend/templates")
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

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

# Endpoints
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/login")
def login_json(username: str = Form(...), password: str = Form(...)):
    role = authenticate_user(username, password)

    if role == "profesor":
        return {"success": True, "redirect": "/dashboard-profesor"}
    if role == "estudiante":
        return {"success": True, "redirect": "/dashboard-estudiante"}

    return {"success": False, "error": "Usuario o contraseña incorrectos"}

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
def register_user(
    username: str = Form(...),
    password: str = Form(...),
    nombre: str = Form(...),
    apellidos: str = Form(...),
):
    # 1. Comprobar si ya existe
    db = SessionLocal()
    try:
        # 1. Comprobar si ya existe
        existing_user = db.query(User).filter_by(username=username).first()
        if existing_user:
            return {"error": "Usuario ya existe"}

        # 2. Crear hash de la contraseña
        hashed = pwd_context.hash(password)

        # 3. Crear usuario y guardar
        user = User(
            username=username,
            password_hash=hashed,
            role="estudiante",
            nombre=nombre,
            apellidos=apellidos
        )
        db.add(user)
        db.commit()
    finally:
        db.close() 

    return {"success": "Usuario creado correctamente"}



@app.get("/dashboard-profesor", response_class=HTMLResponse)
def dashboard_profesor(request: Request):
    return templates.TemplateResponse("dashboard_profesor.html", {"request": request})

@app.get("/dashboard-estudiante", response_class=HTMLResponse)
def dashboard_estudiante(request: Request):
    return templates.TemplateResponse("dashboard_estudiante.html", {"request": request})

@app.get("/")
def root():
    return RedirectResponse(url="/login")
