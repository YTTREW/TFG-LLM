from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from backend.core.config import SECRET_KEY
from backend.core.database import engine
from backend.core.database import Base

from backend.routers.auth import router as auth_router
from backend.routers.admin import router as admin_router
from backend.routers.professor import router as professor_router
from backend.routers.api_chats import router as api_chats_router

# Inicializar las tablas en PostgreSQL
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CognitiveLab API", version="1.0.0")

# Middleware para sesiones de usuario
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Archivos estáticos (CSS, imágenes)
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

# Incluir todas las rutas separadas
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(professor_router)
app.include_router(api_chats_router)
