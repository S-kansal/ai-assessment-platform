"""Task service — high-level operations consumed by API routes.

This thin service layer delegates to the task runner and provides a
clean interface for routes to call without knowing internal details.
"""

from sqlalchemy.orm import Session as DbSession

from app.tasks.task_runner import create_task_run, get_task_run, complete_task_run
from app.tasks.task_definitions import TASK_LIBRARY


def start_task(db: DbSession, session_id: str, task_id: str) -> dict:
    """Start a task for a candidate session."""
    return create_task_run(db, session_id, task_id)


def fetch_task_status(db: DbSession, task_run_id: str) -> dict:
    """Return current status of a task run."""
    task_run = get_task_run(db, task_run_id)
    return {
        "task_run_id": task_run.id,
        "task_id": task_run.task_id,
        "session_id": task_run.session_id,
        "status": task_run.status,
        "started_at": task_run.started_at.isoformat() if task_run.started_at else None,
        "completed_at": (
            task_run.completed_at.isoformat() if task_run.completed_at else None
        ),
    }


def finish_task(db: DbSession, task_run_id: str, solution: str | None = None) -> dict:
    """Complete a task run and optionally store the candidate's solution."""
    task_run = complete_task_run(db, task_run_id, solution)
    return {
        "task_run_id": task_run.id,
        "status": task_run.status,
        "completed_at": task_run.completed_at.isoformat(),
    }


def list_tasks() -> dict:
    """Return the full task library for reference."""
    return TASK_LIBRARY
