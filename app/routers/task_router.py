from fastapi import APIRouter, BackgroundTasks, HTTPException, status

from app.core.cache import CacheService
from app.dependencies import CurrentUserDep, SessionDep
from app.schemas.task_schema import TaskCreate, TaskResponse, TaskUpdate
from app.services.audit_service import AuditService
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/", response_model=list[TaskResponse])
def read_tasks(
    db: SessionDep, current_user: CurrentUserDep, skip: int = 0, limit: int = 100
):
    """Obtener tareas con estrategia Cache-Aside por usuario."""
    cache_key = f"user:{current_user.id}:tasks"

    # 1. Cache-Aside: Intentar lectura desde Redis (solo si es consulta estandar)
    if skip == 0 and limit == 100:
        cached_data = CacheService.get(cache_key)
        if cached_data is not None:
            return cached_data

    # 2. Consulta a base de datos relacional
    tasks = TaskService.get_all(db, owner_id=current_user.id, skip=skip, limit=limit)

    # 3. Guardar en cache con TTL de 300 segundos
    if skip == 0 and limit == 100:
        serialized_tasks = [
            TaskResponse.model_validate(task).model_dump(mode="json") for task in tasks
        ]
        CacheService.set(cache_key, serialized_tasks, ttl=300)

    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
def read_task(task_id: int, db: SessionDep, current_user: CurrentUserDep):
    """Obtener una tarea especifica del usuario autenticado."""
    task = TaskService.get_by_id(db, task_id=task_id, owner_id=current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return task


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_in: TaskCreate,
    db: SessionDep,
    current_user: CurrentUserDep,
    background_tasks: BackgroundTasks,
):
    """Crear tarea, invalidar cache del usuario y despachar auditoria en background."""
    new_task = TaskService.create(db, task_data=task_in, owner_id=current_user.id)

    # Invalidacion de cache del inquilino
    CacheService.invalidate_user_tasks(current_user.id)

    # Despacho en segundo plano
    background_tasks.add_task(
        AuditService.log_task_event,
        action="create",
        task_id=new_task.id,
        user_email=current_user.email,
    )

    return new_task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: SessionDep,
    current_user: CurrentUserDep,
    background_tasks: BackgroundTasks,
):
    """Actualizar tarea, invalidar cache y auditar en segundo plano."""
    updated_task = TaskService.update(
        db, task_id=task_id, task_data=task_in, owner_id=current_user.id
    )
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    # Invalida cache del usuario
    CacheService.invalidate_user_tasks(current_user.id)

    # Tarea en background
    background_tasks.add_task(
        AuditService.log_task_event,
        action="update",
        task_id=updated_task.id,
        user_email=current_user.email,
    )

    return updated_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: SessionDep,
    current_user: CurrentUserDep,
    background_tasks: BackgroundTasks,
):
    """Eliminar tarea, purgar cache y auditar en background."""
    success = TaskService.delete(db, task_id=task_id, owner_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    # Purgar cache
    CacheService.invalidate_user_tasks(current_user.id)

    # Tarea en background
    background_tasks.add_task(
        AuditService.log_task_event,
        action="delete",
        task_id=task_id,
        user_email=current_user.email,
    )
