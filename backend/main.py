from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from auth import authenticate_user

app = FastAPI()

# Carpeta de templates --> Archivos html en carpeta templates
templates = Jinja2Templates(directory="templates")

# Servir archivos estáticos (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")


# Página de login
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Endpoint POST del login (DEVUELVE JSON)
@app.post("/login")
def login_json(username: str = Form(...), password: str = Form(...)):
    role = authenticate_user(username, password)

    if role == "profesor":
        return {"success": True, "redirect": "/dashboard-profesor"}

    if role == "estudiante":
        return {"success": True, "redirect": "/dashboard-estudiante"}

    return {"success": False, "error": "Usuario o contraseña incorrectos"}


# Dashboard profesor
@app.get("/dashboard-profesor", response_class=HTMLResponse)
def dashboard_profesor(request: Request):
    return templates.TemplateResponse("dashboard_profesor.html", {"request": request})


# Dashboard estudiante
@app.get("/dashboard-estudiante", response_class=HTMLResponse)
def dashboard_estudiante(request: Request):
    return templates.TemplateResponse("dashboard_estudiante.html", {"request": request})


# Ruta raíz redirige al login
@app.get("/")
def root():
    return RedirectResponse(url="/login")
