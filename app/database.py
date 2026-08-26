from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# URL de conexión para SQLite local
SQLALCHEMY_DATABASE_URL = "sqlite:///./mock1.db"

# connect_args={"check_same_thread": False} es obligatorio solo en SQLite para permitir concurrencia de FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Fabrica de sesiones de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para todos los modelos ORM
Base = declarative_base()


# Dependencia de FastAPI: abre la sesión al recibir la request y la cierra automáticamente al terminar
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
