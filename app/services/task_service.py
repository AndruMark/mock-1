from sqlalchemy.orm import Session

from app.models.task_model import Task
from app.schemas.task_schema import TaskCreate, TaskUpdate


class TaskService:
    @staticmethod
    def get_all(
        db: Session, owner_id: int, skip: int = 0, limit: int = 100
    ) -> list[Task]:
        return (
            db.query(Task)
            .filter(Task.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_id(db: Session, task_id: int, owner_id: int) -> Task | None:
        return (
            db.query(Task).filter(Task.id == task_id, Task.owner_id == owner_id).first()
        )

    @staticmethod
    def create(db: Session, task_data: TaskCreate, owner_id: int) -> Task:
        new_task = Task(
            title=task_data.title,
            description=task_data.description,
            completed=task_data.completed,
            owner_id=owner_id,
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return new_task

    @staticmethod
    def update(
        db: Session, task_id: int, task_data: TaskUpdate, owner_id: int
    ) -> Task | None:
        task = TaskService.get_by_id(db, task_id=task_id, owner_id=owner_id)
        if not task:
            return None

        update_dict = task_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(task, key, value)

        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def delete(db: Session, task_id: int, owner_id: int) -> bool:
        task = TaskService.get_by_id(db, task_id=task_id, owner_id=owner_id)
        if not task:
            return False

        db.delete(task)
        db.commit()
        return True
