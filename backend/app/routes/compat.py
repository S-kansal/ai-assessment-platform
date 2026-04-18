import re
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.assessment.orchestrator import (
    create_assessment,
    start_assessment,
)
from app.core.dependencies import envelope, get_current_user, get_db, require_roles
from app.core.exceptions import NotFoundError, ValidationError
from app.models.assessment import Assessment
from app.models.candidate import Candidate
from app.models.organization import Organization
from app.models.task_run import TaskRun
from app.services.auth import login_user, register_user
from app.services.candidates import create_candidate, get_candidate
from app.services.dashboard import (
    get_candidate_dashboard_profile,
    get_dashboard_candidates,
)
from app.services.evaluations import run_evaluation
from app.services.scores import compute_scores
from app.services.simulations import create_simulation_run
from app.services.tasks import get_task, get_task_run
from app.services.telemetry import create_telemetry_event


router = APIRouter(tags=["compat"])


def _slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", value.strip().lower()).strip("-")


@router.post("/organizations", status_code=status.HTTP_201_CREATED)
def create_organization_compat(
    body: dict = Body(...),
    db: Session = Depends(get_db),
) -> dict:
    name = str(body.get("name", "")).strip()
    if not name:
        raise ValidationError("Organization name is required")
    base_slug = _slugify(name) or "organization"
    slug = base_slug
    suffix = 1
    while db.scalar(select(Organization).where(Organization.slug == slug)) is not None:
        suffix += 1
        slug = f"{base_slug}-{suffix}"

    organization = Organization(name=name, slug=slug)
    db.add(organization)
    db.flush()
    db.commit()
    return envelope(
        {
            "organization_id": organization.id,
            "id": organization.id,
            "name": organization.name,
            "slug": organization.slug,
        }
    )


@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
def register_user_compat(
    body: dict = Body(...),
    db: Session = Depends(get_db),
) -> dict:
    user = register_user(
        db,
        str(body.get("organization_id", "")).strip(),
        str(body.get("email", "")).strip(),
        str(body.get("password", "")).strip(),
        str(body.get("role", "reviewer")).strip().lower(),
    )
    db.commit()
    return envelope(
        {
            "id": user.id,
            "organization_id": user.organization_id,
            "email": user.email,
            "role": user.role,
        }
    )


@router.post("/auth/login")
def login_compat(
    body: dict = Body(...),
    db: Session = Depends(get_db),
) -> dict:
    result = login_user(db, str(body.get("email", "")), str(body.get("password", "")))
    return envelope(result)


@router.post("/candidates", status_code=status.HTTP_201_CREATED)
def create_candidate_compat(
    body: dict = Body(...),
    user=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> dict:
    password = str(body.get("password") or f"{secrets.token_urlsafe(10)}A1!")
    candidate = create_candidate(
        db,
        user.organization_id,
        str(body.get("name", "")).strip(),
        str(body.get("email", "")).strip(),
        password,
    )
    db.commit()
    return envelope(
        {
            "candidate_id": candidate.id,
            "id": candidate.id,
            "name": candidate.name,
            "email": candidate.email,
            "temporary_password": password,
        }
    )


@router.get("/candidates/{candidate_id}")
def get_candidate_compat(
    candidate_id: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    candidate = get_candidate(db, user.organization_id, candidate_id)
    return envelope(
        {
            "id": candidate.id,
            "name": candidate.name,
            "email": candidate.email,
        }
    )


@router.post("/assessments", status_code=status.HTTP_201_CREATED)
def create_assessment_compat(
    body: dict = Body(...),
    user=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> dict:
    candidate_id = str(body.get("candidate_id", "")).strip()
    candidate = db.scalar(
        select(Candidate).where(
            Candidate.id == candidate_id,
            Candidate.organization_id == user.organization_id,
        )
    )
    if candidate is None:
        raise NotFoundError("Candidate not found")
    assessment = create_assessment(
        db,
        user.organization_id,
        candidate_id,
        str(body.get("title") or "AI Engineering Assessment"),
        str(body.get("order_mode") or "fixed"),
        str(body.get("browser_session_id") or f"browser-{candidate_id[:8]}"),
    )
    db.commit()
    return envelope(
        {
            "assessment_id": assessment.id,
            "id": assessment.id,
            "status": assessment.status,
            "candidate_id": assessment.candidate_id,
        }
    )


@router.post("/assessments/{assessment_id}/start")
def start_assessment_compat(
    assessment_id: str,
    user=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> dict:
    assessment = db.scalar(
        select(Assessment).where(
            Assessment.id == assessment_id,
            Assessment.organization_id == user.organization_id,
        )
    )
    if assessment is None:
        raise NotFoundError("Assessment not found")
    active_task_run = start_assessment(db, assessment)
    db.commit()
    return envelope(
        {
            "assessment_id": assessment.id,
            "task_run_id": active_task_run.id,
            "first_task_run_id": active_task_run.id,
            "task_id": active_task_run.task_id,
            "status": assessment.status,
        }
    )


@router.post("/simulations")
def run_simulation_compat(
    body: dict = Body(...),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    task_run = get_task_run(db, user.organization_id, str(body.get("task_run_id", "")).strip())
    task = get_task(db, user.organization_id, task_run.task_id)
    prompt_text = str(body.get("prompt") or body.get("prompt_text") or "").strip()
    query_text = str(body.get("query") or body.get("query_text") or "").strip()
    simulation_run = create_simulation_run(db, task_run, task, prompt_text, query_text)
    create_telemetry_event(
        db,
        user.organization_id,
        task_run.id,
        "simulation_run",
        int(datetime.now(timezone.utc).timestamp() * 1000),
        {
            "simulation_run_id": simulation_run.id,
            "prompt_text": prompt_text,
            "query_text": query_text,
        },
    )
    db.commit()
    return envelope(
        {
            "simulation_run_id": simulation_run.id,
            "id": simulation_run.id,
            "simulation_output": simulation_run.response_text,
            "response_text": simulation_run.response_text,
            "retrieved_chunks": simulation_run.retrieved_chunks,
            "debug_logs": simulation_run.debug_logs,
            "failure_mode_indicator": task.failure_modes,
            "confidence_score": simulation_run.confidence_score,
        }
    )


@router.post("/telemetry", status_code=status.HTTP_201_CREATED)
def create_telemetry_compat(
    body: dict = Body(...),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    task_run_id = str(body.get("task_run_id", "")).strip()
    payload = dict(body.get("payload") or {})
    if "prompt_text" in body:
        payload["prompt_text"] = body["prompt_text"]
    if "query_text" in body:
        payload["query_text"] = body["query_text"]
    monotonic_timestamp_ms = int(body.get("monotonic_timestamp_ms") or int(datetime.now(timezone.utc).timestamp() * 1000))
    event = create_telemetry_event(
        db,
        user.organization_id,
        task_run_id,
        str(body.get("event_type", "")).strip(),
        monotonic_timestamp_ms,
        payload,
    )
    db.commit()
    return envelope({"id": event.id, "status": "recorded"})


@router.post("/task-runs/{task_run_id}/submit")
def submit_task_run_compat(
    task_run_id: str,
    body: dict = Body(...),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    task_run = db.scalar(
        select(TaskRun).where(
            TaskRun.id == task_run_id,
            TaskRun.organization_id == user.organization_id,
        )
    )
    if task_run is None:
        raise NotFoundError("Task run not found")
    assessment = db.scalar(
        select(Assessment).where(
            Assessment.id == task_run.assessment_id,
            Assessment.organization_id == user.organization_id,
        )
    )
    if assessment is None:
        raise NotFoundError("Assessment not found")
    task_run.final_prompt = str(body.get("final_prompt") or body.get("prompt") or body.get("solution") or "")
    task_run.final_query = str(body.get("final_query") or body.get("query") or "")
    task_run.submitted_root_cause = str(
        body.get("submitted_root_cause") or body.get("root_cause") or ""
    )
    task_run.submitted_fix_summary = str(
        body.get("submitted_fix_summary") or body.get("solution") or ""
    )
    task_run.status = "completed"
    task_run.completed_at = datetime.now(timezone.utc)
    db.flush()
    db.commit()
    return envelope(
        {
            "task_run_id": task_run.id,
            "assessment_id": assessment.id,
            "status": task_run.status,
        }
    )


@router.post("/evaluations")
def run_evaluation_compat(
    body: dict = Body(...),
    user=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> dict:
    evaluation = run_evaluation(db, user.organization_id, str(body.get("task_run_id", "")).strip())
    db.commit()
    return envelope(
        {
            "id": evaluation.id,
            "task_run_id": evaluation.task_run_id,
            "diagnostic_accuracy": evaluation.dimension_scores.get("diagnostic_accuracy", 0.0),
            "solution_success": evaluation.dimension_scores.get("solution_success", 0.0),
            "efficiency": evaluation.dimension_scores.get("efficiency", 0.0),
            "iteration_quality": evaluation.dimension_scores.get("iteration_quality", 0.0),
            "dimension_scores": evaluation.dimension_scores,
            "total_score": evaluation.total_score,
        }
    )


@router.post("/scores")
def compute_scores_compat(
    body: dict = Body(...),
    user=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> dict:
    result = compute_scores(db, user.organization_id, str(body.get("assessment_id", "")).strip())
    db.commit()
    return envelope(
        {
            "id": result.id,
            "assessment_id": result.assessment_id,
            "capability_profile": {
                "rag_debugging": result.normalized_scores.get("rag_debugging_skill", 0.0),
                "prompt_engineering": result.normalized_scores.get("prompt_engineering_skill", 0.0),
                "diagnostic_reasoning": result.normalized_scores.get("systematic_diagnostic_reasoning", 0.0),
                "efficiency_under_ambiguity": result.normalized_scores.get("efficiency_under_ambiguity", 0.0),
            },
            "raw_scores": result.raw_scores,
            "normalized_scores": result.normalized_scores,
            "aggregate_score": result.aggregate_score,
        }
    )


@router.get("/dashboard/candidates")
def dashboard_candidates_compat(
    user=Depends(require_roles("admin", "reviewer")),
    db: Session = Depends(get_db),
) -> dict:
    candidates = get_dashboard_candidates(db, user.organization_id)
    return envelope(
        [
            {
                "id": candidate.id,
                "name": candidate.name,
                "email": candidate.email,
            }
            for candidate in candidates
        ]
    )


@router.get("/dashboard/candidates/{candidate_id}")
def dashboard_candidate_profile_compat(
    candidate_id: str,
    user=Depends(require_roles("admin", "reviewer")),
    db: Session = Depends(get_db),
) -> dict:
    profile = get_candidate_dashboard_profile(db, user.organization_id, candidate_id)
    score = profile["score"]
    return envelope(
        {
            "candidate": {
                "id": profile["candidate"].id,
                "name": profile["candidate"].name,
                "email": profile["candidate"].email,
            },
            "capability_scores": None
            if score is None
            else {
                "rag_debugging": score.normalized_scores.get("rag_debugging_skill", 0.0),
                "prompt_engineering": score.normalized_scores.get("prompt_engineering_skill", 0.0),
                "diagnostic_reasoning": score.normalized_scores.get("systematic_diagnostic_reasoning", 0.0),
                "efficiency_under_ambiguity": score.normalized_scores.get("efficiency_under_ambiguity", 0.0),
            },
            "task_performance": [
                {
                    "assessment_id": assessment.id,
                    "title": assessment.title,
                    "status": assessment.status,
                }
                for assessment in profile["assessments"]
            ],
        }
    )
