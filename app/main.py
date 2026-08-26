from fastapi import FastAPI

from app.database import Base, engine
from app.routers import task_router

# Crea automáticamente las tablas en SQLite al arrancar la app
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Mock-1 REST API",
    description="Microservicio backend modular con FastAPI, SQLAlchemy y Pydantic v2",
    version="1.0.0",
)

# Registrar rutas
app.include_router(task_router.router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "Mock-1 API", "version": "1.0.0"}
