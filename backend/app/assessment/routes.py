"""Assessment API routes."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session as DbSession

from app.database import get_db
from app.models.candidate import Candidate
from app.models.session import Session
from app.assessment.orchestrator import (
    start_assessment,
    advance_assessment,
    get_assessment_status,
)

router = APIRouter(prefix="/assessments", tags=["assessments"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class StartRequest(BaseModel):
    candidate_id: str


class StartResponse(BaseModel):
    assessment_id: str
    status: str
    first_task: str
    task_run_id: str
    description: str
    total_tasks: int
    current_task_index: int


class AdvanceRequest(BaseModel):
    task_run_id: str
    solution: Optional[str] = None


class StatusTaskItem(BaseModel):
    task_id: str
    task_run_id: Optional[str] = None
    order_index: int
    status: str


class StatusResponse(BaseModel):
    assessment_id: str
    candidate_id: str
    status: str
    current_task: Optional[str] = None
    current_task_run_id: Optional[str] = None
    completed_tasks: int
    total_tasks: int
    tasks: List[StatusTaskItem]


# ---------------------------------------------------------------------------
# POST /assessments/start
# ---------------------------------------------------------------------------

@router.post("/start")
def start_assessment_endpoint(body: StartRequest, db: DbSession = Depends(get_db)):
    """Start a new multi-task assessment for a candidate.

    Creates candidate session, assessment, and begins first task.
    Inherits organization_id from the candidate record.
    """
    # Get org_id from candidate
    from app.models.candidate import Candidate
    candidate = db.query(Candidate).filter(Candidate.id == body.candidate_id).first()
    org_id = candidate.organization_id if candidate else None

    # Auto-create session for the assessment
    session = Session(candidate_id=body.candidate_id, organization_id=org_id)
    db.add(session)
    db.commit()
    db.refresh(session)

    result = start_assessment(db, body.candidate_id, session.id, org_id=org_id)
    return result


# ---------------------------------------------------------------------------
# GET /assessments/{assessment_id}
# ---------------------------------------------------------------------------

@router.get("/assessments/{assessment_id}")
def get_status_endpoint(assessment_id: str, db: DbSession = Depends(get_db)):
    """Get current assessment progress."""
    return get_assessment_status(db, assessment_id)


# ---------------------------------------------------------------------------
# POST /assessments/{assessment_id}/advance
# ---------------------------------------------------------------------------

@router.post("/{assessment_id}/advance")
def advance_endpoint(
    assessment_id: str,
    body: AdvanceRequest,
    db: DbSession = Depends(get_db),
):
    """Complete current task and advance to the next one.

    This endpoint:
    1. Completes the current task
    2. Runs evaluation
    3. Starts the next task (or completes the assessment)
    """
    return advance_assessment(db, assessment_id, body.task_run_id, body.solution)
