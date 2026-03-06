"""Task runner — manages task initialisation and lifecycle transitions.

Responsibilities:
- Validate that a task exists in the library
- Create a task_run record in the database
- Configure the simulation state for the task
- Transition task status (pending → running → completed / failed)
"""

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session as DbSession

from app.models.task import Task
from app.models.task_run import TaskRun
from app.models.session import Session
from app.tasks.task_definitions import TASK_LIBRARY
from app.tasks.task_state import TaskState


def create_task_run(
    db: DbSession,
    session_id: str,
    task_id: str,
) -> dict:
    """Initialise a new task run for a candidate session.

    1. Validate session exists
    2. Validate task exists in library
    3. Seed task definition into DB if not present
    4. Create task_run record
    5. Return task info for the candidate
    """
    # --- Validate session ---
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # --- Validate task definition ---
    definition = TASK_LIBRARY.get(task_id)
    if not definition:
        raise HTTPException(status_code=404, detail="Task not found in library")

    # --- Build simulation_config from definition ---
    sim_config = {
        "failure_mode": definition["failure_mode"],
    }
    # Merge any extra simulation params from the definition
    for key in ("retrieval_k", "chunk_size", "prompt_template", "tool_config"):
        if key in definition:
            sim_config[key] = definition[key]

    # --- Ensure task row exists in DB ---
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        task = Task(
            id=task_id,
            name=definition["name"],
            description=definition["description"],
            capability_target=definition["capability_target"],
            task_type=definition["task_type"],
            simulation_type=definition["simulation_type"],
            failure_mode=definition["failure_mode"],
            simulation_config=sim_config,
        )
        db.add(task)
        db.commit()
        db.refresh(task)

    # --- Compute attempt number ---
    prior_attempts = (
        db.query(TaskRun)
        .filter(TaskRun.session_id == session_id, TaskRun.task_id == task_id)
        .count()
    )
    attempt_number = prior_attempts + 1

    # --- Create task run ---
    task_run = TaskRun(
        session_id=session_id,
        task_id=task_id,
        attempt_number=attempt_number,
        status="running",
    )
    db.add(task_run)
    db.commit()
    db.refresh(task_run)

    return {
        "task_run_id": task_run.id,
        "task_id": task_id,
        "description": definition["description"],
        "simulation_type": definition["simulation_type"],
        "failure_mode": definition["failure_mode"],
    }


def get_task_run(db: DbSession, task_run_id: str) -> TaskRun:
    """Retrieve a task run by ID or raise 404."""
    task_run = db.query(TaskRun).filter(TaskRun.id == task_run_id).first()
    if not task_run:
        raise HTTPException(status_code=404, detail="Task run not found")
    return task_run


def complete_task_run(
    db: DbSession,
    task_run_id: str,
    solution: str | None = None,
) -> TaskRun:
    """Mark a task run as completed."""
    task_run = get_task_run(db, task_run_id)

    if task_run.status == "completed":
        raise HTTPException(status_code=400, detail="Task already completed")

    task_run.status = "completed"
    task_run.completed_at = datetime.now(timezone.utc)
    if solution:
        task_run.solution = solution

    db.commit()
    db.refresh(task_run)
    return task_run
