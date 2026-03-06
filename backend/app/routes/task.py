from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session as DbSession

from app.database import get_db
from app.tasks.task_service import start_task, fetch_task_status, finish_task

router = APIRouter(prefix="/tasks", tags=["tasks"])


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class TaskStartRequest(BaseModel):
    session_id: str
    task_id: str


class TaskStartResponse(BaseModel):
    task_run_id: str
    task_id: str
    description: str
    simulation_type: str
    failure_mode: str


class TaskStatusResponse(BaseModel):
    task_run_id: str
    task_id: str
    session_id: str
    status: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class TaskCompleteRequest(BaseModel):
    task_run_id: str
    solution: Optional[str] = None


class TaskCompleteResponse(BaseModel):
    task_run_id: str
    status: str
    completed_at: str


# ---------------------------------------------------------------------------
# POST /tasks/start
# ---------------------------------------------------------------------------

@router.post("/start", response_model=TaskStartResponse)
def start_task_endpoint(
    body: TaskStartRequest,
    db: DbSession = Depends(get_db),
):
    """Start a new task for a candidate session."""
    result = start_task(db, body.session_id, body.task_id)
    return TaskStartResponse(**result)


# ---------------------------------------------------------------------------
# GET /tasks/{task_run_id}
# ---------------------------------------------------------------------------

@router.get("/{task_run_id}", response_model=TaskStatusResponse)
def get_task_status(
    task_run_id: str,
    db: DbSession = Depends(get_db),
):
    """Get the current status of a task run."""
    result = fetch_task_status(db, task_run_id)
    return TaskStatusResponse(**result)


# ---------------------------------------------------------------------------
# POST /tasks/complete
# ---------------------------------------------------------------------------

@router.post("/complete", response_model=TaskCompleteResponse)
def complete_task_endpoint(
    body: TaskCompleteRequest,
    db: DbSession = Depends(get_db),
):
    """Mark a task run as completed."""
    result = finish_task(db, body.task_run_id, body.solution)
    return TaskCompleteResponse(**result)
