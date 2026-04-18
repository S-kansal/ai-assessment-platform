from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.task import Task
from app.models.task_run import TaskRun


def get_task_run(db: Session, organization_id: str, task_run_id: str) -> TaskRun:
    task_run = db.scalar(
        select(TaskRun).where(
            TaskRun.id == task_run_id,
            TaskRun.organization_id == organization_id,
        )
    )
    if task_run is None:
        raise NotFoundError("Task run not found")
    return task_run


def get_task(db: Session, organization_id: str, task_id: str) -> Task:
    task = db.scalar(
        select(Task).where(
            Task.id == task_id,
            Task.organization_id == organization_id,
        )
    )
    if task is None:
        raise NotFoundError("Task not found")
    return task
