from sqlalchemy.orm import Session

from app.models.task_model import Task
from app.schemas.task_schema import TaskCreate, TaskUpdate


class TaskService:
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Task]:
        return db.query(Task).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, task_id: int) -> Task | None:
        return db.query(Task).filter(Task.id == task_id).first()

    @staticmethod
    def create(db: Session, task_data: TaskCreate) -> Task:
        new_task = Task(
            title=task_data.title,
            description=task_data.description,
            completed=task_data.completed,
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return new_task

    @staticmethod
    def update(db: Session, task_id: int, task_data: TaskUpdate) -> Task | None:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None

        update_dict = task_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(task, key, value)

        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def delete(db: Session, task_id: int) -> bool:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return False

        db.delete(task)
        db.commit()
        return True
