"""Dashboard read-only API endpoints for hiring managers — tenant-scoped."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session as DbSession

from app.database import get_db
from app.auth.tenant_guard import get_current_user
from app.models.candidate import Candidate
from app.models.session import Session
from app.models.task_run import TaskRun
from app.models.task import Task
from app.models.telemetry import TelemetryEvent
from app.evaluation.models import EvaluationResult
from app.scoring.models import CandidateScore, TaskScore
from app.models.assessment_result import AssessmentResult

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class CandidateListItem(BaseModel):
    id: str
    name: str
    email: str


class CandidateProfileResponse(BaseModel):
    candidate_id: str
    name: str
    email: str
    capabilities: Dict[str, float]
    sample_sizes: Dict[str, int]
    sessions: List[str]


class TaskRunDetail(BaseModel):
    task_run_id: str
    task_id: str
    status: str
    attempt_number: Optional[int] = None
    task_score: Optional[float] = None
    capability: Optional[str] = None
    diagnostic_score: Optional[float] = None
    success_score: Optional[float] = None
    efficiency_score: Optional[float] = None
    iteration_score: Optional[float] = None


class TelemetryEventItem(BaseModel):
    id: str
    event_type: str
    timestamp: str
    payload: Optional[Dict[str, Any]] = None


class EvaluationDetail(BaseModel):
    diagnostic_score: float
    success_score: float
    efficiency_score: float
    iteration_score: float
    simulation_runs: Optional[int] = None
    prompt_edits: Optional[int] = None
    retrieval_inspections: Optional[int] = None
    time_to_solution: Optional[float] = None
    evaluation_trace: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------------------------
# GET /dashboard/candidates  (tenant-scoped)
# ---------------------------------------------------------------------------

@router.get("/candidates", response_model=List[CandidateListItem])
def list_candidates(
    db: DbSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """List candidates belonging to the current organization."""
    org_id = user["organization_id"]
    candidates = (
        db.query(Candidate)
        .filter(Candidate.organization_id == org_id)
        .order_by(Candidate.created_at.desc())
        .all()
    )
    return [CandidateListItem(id=c.id, name=c.name, email=c.email) for c in candidates]


# ---------------------------------------------------------------------------
# GET /dashboard/candidates/{candidate_id}/profile  (tenant-scoped)
# ---------------------------------------------------------------------------

@router.get("/candidates/{candidate_id}/profile", response_model=CandidateProfileResponse)
def get_candidate_profile(
    candidate_id: str,
    db: DbSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Get full capability profile for a candidate (tenant-scoped)."""
    org_id = user["organization_id"]
    candidate = (
        db.query(Candidate)
        .filter(Candidate.id == candidate_id, Candidate.organization_id == org_id)
        .first()
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    scores = (
        db.query(CandidateScore)
        .filter(CandidateScore.candidate_id == candidate_id)
        .all()
    )
    capabilities = {s.capability: s.score for s in scores}
    sample_sizes = {s.capability: s.sample_size for s in scores}

    sessions = db.query(Session).filter(Session.candidate_id == candidate_id).all()
    session_ids = [s.id for s in sessions]

    return CandidateProfileResponse(
        candidate_id=candidate.id,
        name=candidate.name,
        email=candidate.email,
        capabilities=capabilities,
        sample_sizes=sample_sizes,
        sessions=session_ids,
    )


# ---------------------------------------------------------------------------
# GET /dashboard/candidates/{candidate_id}/tasks  (tenant-scoped)
# ---------------------------------------------------------------------------

@router.get("/candidates/{candidate_id}/tasks", response_model=List[TaskRunDetail])
def get_candidate_tasks(
    candidate_id: str,
    db: DbSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Get all task runs for a candidate with scores (tenant-scoped)."""
    org_id = user["organization_id"]
    # Verify candidate belongs to org
    candidate = (
        db.query(Candidate)
        .filter(Candidate.id == candidate_id, Candidate.organization_id == org_id)
        .first()
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    sessions = db.query(Session).filter(Session.candidate_id == candidate_id).all()
    session_ids = [s.id for s in sessions]

    task_runs = (
        db.query(TaskRun)
        .filter(TaskRun.session_id.in_(session_ids))
        .all()
    )

    results = []
    for tr in task_runs:
        ts = db.query(TaskScore).filter(TaskScore.task_run_id == tr.id).first()
        ev = db.query(EvaluationResult).filter(EvaluationResult.task_run_id == tr.id).first()

        results.append(TaskRunDetail(
            task_run_id=tr.id,
            task_id=tr.task_id,
            status=tr.status,
            attempt_number=tr.attempt_number,
            task_score=ts.task_score if ts else None,
            capability=ts.capability if ts else None,
            diagnostic_score=ev.diagnostic_score if ev else None,
            success_score=ev.success_score if ev else None,
            efficiency_score=ev.efficiency_score if ev else None,
            iteration_score=ev.iteration_score if ev else None,
        ))

    return results


# ---------------------------------------------------------------------------
# GET /dashboard/task-runs/{task_run_id}/telemetry
# ---------------------------------------------------------------------------

@router.get("/task-runs/{task_run_id}/telemetry", response_model=List[TelemetryEventItem])
def get_task_run_telemetry(
    task_run_id: str,
    db: DbSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Get telemetry events for a task run."""
    tr = db.query(TaskRun).filter(TaskRun.id == task_run_id).first()
    if not tr:
        raise HTTPException(status_code=404, detail="Task run not found")

    events = (
        db.query(TelemetryEvent)
        .filter(TelemetryEvent.session_id == tr.session_id)
        .order_by(TelemetryEvent.timestamp)
        .all()
    )

    return [
        TelemetryEventItem(
            id=e.id,
            event_type=e.event_type,
            timestamp=e.timestamp.isoformat() if e.timestamp else "",
            payload=e.payload_json if e.payload_json else {},
        )
        for e in events
    ]


# ---------------------------------------------------------------------------
# GET /dashboard/task-runs/{task_run_id}/evaluation
# ---------------------------------------------------------------------------

@router.get("/task-runs/{task_run_id}/evaluation", response_model=EvaluationDetail)
def get_task_run_evaluation(
    task_run_id: str,
    db: DbSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Get evaluation result for a task run."""
    ev = db.query(EvaluationResult).filter(EvaluationResult.task_run_id == task_run_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    return EvaluationDetail(
        diagnostic_score=ev.diagnostic_score,
        success_score=ev.success_score,
        efficiency_score=ev.efficiency_score,
        iteration_score=ev.iteration_score,
        simulation_runs=ev.simulation_runs,
        prompt_edits=ev.prompt_edits,
        retrieval_inspections=ev.retrieval_inspections,
        time_to_solution=ev.time_to_solution,
        evaluation_trace=ev.evaluation_trace,
    )
