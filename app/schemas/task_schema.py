from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# Esquema base con atributos comunes
class TaskBase(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        examples=["Configurar entorno de desarrollo"],
    )
    description: str | None = Field(
        None, max_length=500, examples=["Instalar herramientas con Scoop y uv"]
    )
    completed: bool = Field(default=False)


# Esquema para crear una tarea (el cliente solo envía esto)
class TaskCreate(TaskBase):
    pass


# Esquema para actualizar (todos los campos opcionales)
class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=3, max_length=100)
    description: str | None = None
    completed: bool | None = None


# Esquema de respuesta que devuelve la API hacia afuera
class TaskResponse(TaskBase):
    id: int
    created_at: datetime

    # Configuración Pydantic v2 para leer directo de modelos ORM SQLAlchemy
    model_config = ConfigDict(from_attributes=True)
