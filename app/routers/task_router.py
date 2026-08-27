from fastapi import APIRouter, HTTPException, status

from app.dependencies import CurrentUserDep, SessionDep
from app.schemas.task_schema import TaskCreate, TaskResponse, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/", response_model=list[TaskResponse])
def read_tasks(
    db: SessionDep, current_user: CurrentUserDep, skip: int = 0, limit: int = 100
):
    """Obtener lista paginada de tareas del usuario autenticado."""
    return TaskService.get_all(db, owner_id=current_user.id, skip=skip, limit=limit)


@router.get("/{task_id}", response_model=TaskResponse)
def read_task(task_id: int, db: SessionDep, current_user: CurrentUserDep):
    """Obtener una tarea específica del usuario autenticado."""
    task = TaskService.get_by_id(db, task_id=task_id, owner_id=current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return task


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task_in: TaskCreate, db: SessionDep, current_user: CurrentUserDep):
    """Crear una nueva tarea vinculada al usuario autenticado."""
    return TaskService.create(db, task_data=task_in, owner_id=current_user.id)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: SessionDep,
    current_user: CurrentUserDep,
):
    """Actualizar parcialmente una tarea del usuario autenticado."""
    updated_task = TaskService.update(
        db, task_id=task_id, task_data=task_in, owner_id=current_user.id
    )
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return updated_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: SessionDep, current_user: CurrentUserDep):
    """Eliminar una tarea del usuario autenticado."""
    success = TaskService.delete(db, task_id=task_id, owner_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
