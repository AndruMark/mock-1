from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.middleware import RequestTracingMiddleware
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

# 1. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Middleware de Trazabilidad y Request ID
app.add_middleware(RequestTracingMiddleware)

# 3. Instrumentación de Métricas Prometheus
instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    excluded_handlers=["/metrics", "/docs", "/openapi.json"],
)
instrumentator.instrument(app).expose(app, endpoint="/metrics", tags=["Observability"])

# 4. Montaje de Routers
app.include_router(auth_router.router)
app.include_router(task_router.router)
app.include_router(ws_router.router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "Mock-1 API", "version": "1.0.0"}
