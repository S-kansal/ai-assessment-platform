from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import (
    AuthContext,
    envelope,
    get_current_user,
    get_db,
    require_candidate_self,
)
from app.services.tasks import get_task, get_task_run


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/{task_run_id}")
def get_task_run_route(
    task_run_id: str,
    user: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    task_run = get_task_run(db, user.organization_id, task_run_id)
    require_candidate_self(task_run.candidate_id, user)
    task = get_task(db, user.organization_id, task_run.task_id)
    return envelope(
        {
            "task_run": {
                "id": task_run.id,
                "assessment_id": task_run.assessment_id,
                "task_id": task_run.task_id,
                "sequence_index": task_run.sequence_index,
                "status": task_run.status,
                "started_at": task_run.started_at.isoformat(),
                "completed_at": task_run.completed_at.isoformat() if task_run.completed_at else None,
            },
            "task": {
                "id": task.id,
                "title": task.title,
                "task_type": task.task_type,
                "failure_modes": task.failure_modes,
                "expected_diagnostic_path": task.expected_diagnostic_path,
            },
        }
    )
