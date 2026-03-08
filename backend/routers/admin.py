from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from backend.core.database import SessionLocal
from backend.core.security import get_password_hash
from backend.models import Estudiante, Profesor

router = APIRouter(tags=["Administrador"])
templates = Jinja2Templates(directory="backend/templates")

############################################
#                                          #
#       ENDPOINTS DE ADMINISTRADOR         #
#                                          #
############################################
# Endpoint GET para cargar dashboard del admin
@router.get("/dashboard-admin", response_class=HTMLResponse)
def dashboard_admin(request: Request):
    if "user" not in request.session:
        return RedirectResponse("/login")

    if request.session.get("role") != "admin":
        return RedirectResponse("/login")
    
    return templates.TemplateResponse(
        "dashboard_admin.html",
        {"request": request, "username": request.session.get("user")}
    )

# Endpoint GET para listar estudiantes
@router.get("/students", response_class=HTMLResponse)
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
@router.post("/admin/delete-student/{student_id}")
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
@router.get("/admin/professors", response_class=HTMLResponse)
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
@router.post("/admin/delete-professor/{professor_id}")
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
@router.get("/admin/register", response_class=HTMLResponse)
def create_user_form(request: Request):
    if request.session.get("role") != "admin":
        return RedirectResponse("/login")

    return templates.TemplateResponse(
        "register_users.html",
        {"request": request}
    )

# Endpoint POST para crear un nuevo usuario (profesor o estudiante)
@router.post("/admin/register")
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
        existing_student = db.query(Estudiante).filter_by(username=username).first()

        existing_professor = db.query(Profesor).filter_by(username=username).first()

        if existing_student or existing_professor:
            print("Username already exists")
            return templates.TemplateResponse(
                "register_users.html",
                {
                    "request": request,
                    "error": "Username already exists"
                }
            )

        hashed_password = get_password_hash(password)

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