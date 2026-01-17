from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .auth import authenticate_user

app = FastAPI()

templates = Jinja2Templates(directory="backend/templates")
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

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

@app.get("/dashboard-profesor", response_class=HTMLResponse)
def dashboard_profesor(request: Request):
    return templates.TemplateResponse("dashboard_profesor.html", {"request": request})

@app.get("/dashboard-estudiante", response_class=HTMLResponse)
def dashboard_estudiante(request: Request):
    return templates.TemplateResponse("dashboard_estudiante.html", {"request": request})

@app.get("/")
def root():
    return RedirectResponse(url="/login")
