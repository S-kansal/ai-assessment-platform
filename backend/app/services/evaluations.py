from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.evaluation.engine import evaluate_task_run, get_evaluation_or_raise
from app.models.task import Task
from app.models.task_run import TaskRun


def run_evaluation(
    db: Session,
    organization_id: str,
    task_run_id: str,
):
    task_run = db.scalar(
        select(TaskRun).where(
            TaskRun.id == task_run_id,
            TaskRun.organization_id == organization_id,
        )
    )
    if task_run is None:
        raise NotFoundError("Task run not found")
    task = db.scalar(
        select(Task).where(
            Task.id == task_run.task_id,
            Task.organization_id == organization_id,
        )
    )
    if task is None:
        raise NotFoundError("Task not found")
    return evaluate_task_run(db, task_run, task)


def get_evaluation(db: Session, organization_id: str, task_run_id: str):
    return get_evaluation_or_raise(db, organization_id, task_run_id)
