from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.task_schema import TaskCreate, TaskResponse, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])

# Alias con Annotated: inyección de dependencias limpia sin llamadas en valores por defecto
SessionDep = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=list[TaskResponse])
def read_tasks(db: SessionDep, skip: int = 0, limit: int = 100):
    """Obtener lista paginada de tareas."""
    return TaskService.get_all(db, skip=skip, limit=limit)


@router.get("/{task_id}", response_model=TaskResponse)
def read_task(task_id: int, db: SessionDep):
    """Obtener una tarea específica por su ID."""
    task = TaskService.get_by_id(db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return task


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task_in: TaskCreate, db: SessionDep):
    """Crear una nueva tarea."""
    return TaskService.create(db, task_data=task_in)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_in: TaskUpdate, db: SessionDep):
    """Actualizar parcialmente una tarea existente."""
    updated_task = TaskService.update(db, task_id=task_id, task_data=task_in)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return updated_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: SessionDep):
    """Eliminar una tarea por ID."""
    success = TaskService.delete(db, task_id=task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
