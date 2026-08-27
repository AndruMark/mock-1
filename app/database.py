import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

# URL de conexión para SQLite local
# Si existe DATABASE_URL en el entorno (Docker/PostgreSQL), la usa; si no, usa SQLite local
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mock1.db")

# SQLite requiere check_same_thread=False, PostgreSQL no lo soporta
connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# connect_args={"check_same_thread": False} es obligatorio solo en SQLite para permitir concurrencia de FastAPI
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)

# Fabrica de sesiones de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para todos los modelos ORM
Base = declarative_base()


# Dependencia de FastAPI: abre la sesión al recibir la request y la cierra automáticamente al terminar
def get_db() -> Generator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
