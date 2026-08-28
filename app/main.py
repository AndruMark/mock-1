from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth_router, task_router, ws_router

# Inicialización del esquema de base de datos
# NO (Alembic)

app = FastAPI(
    title="Mock-1 REST API",
    description="Microservicio backend modular con FastAPI, SQLAlchemy y Pydantic v2",
    version="1.0.0",
)

# Configuración de CORS para permitir peticiones desde el cliente React
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de controladores de ruta
app.include_router(auth_router.router)
app.include_router(task_router.router)
app.include_router(ws_router.router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "Mock-1 API", "version": "1.0.0"}
