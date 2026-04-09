from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["Estudiantes"])
templates = Jinja2Templates(directory="backend/templates")

############################################
#                                          #
#        ENDPOINT DE ESTUDIANTES           #
#                                          #
############################################

# Endpoint GET para cargar dashboard del estudiante
@router.get("/dashboard-estudiante", response_class=HTMLResponse)
def dashboard_estudiante(request: Request):
    if "user" not in request.session or request.session.get("role") != "estudiante":
        return RedirectResponse("/login", status_code=303)

    username = request.session.get("user", "Student")

    return templates.TemplateResponse(
        "dashboard_estudiante.html",
        {"request": request, "username": username}
    )