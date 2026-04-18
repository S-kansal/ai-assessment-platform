from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import envelope, get_db, require_roles
from app.services.dashboard import (
    get_candidate_dashboard_profile,
    get_candidate_task_runs,
    get_dashboard_candidates,
    get_session_replay,
)


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/candidates")
def get_dashboard_candidates_route(
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
                "created_at": candidate.created_at.isoformat(),
            }
            for candidate in candidates
        ]
    )


@router.get("/candidates/{candidate_id}/profile")
def get_dashboard_profile_route(
    candidate_id: str,
    user=Depends(require_roles("admin", "reviewer")),
    db: Session = Depends(get_db),
) -> dict:
    profile = get_candidate_dashboard_profile(db, user.organization_id, candidate_id)
    candidate = profile["candidate"]
    score = profile["score"]
    assessments = profile["assessments"]
    return envelope(
        {
            "candidate": {
                "id": candidate.id,
                "name": candidate.name,
                "email": candidate.email,
                "created_at": candidate.created_at.isoformat(),
            },
            "score": None
            if score is None
            else {
                "aggregate_score": score.aggregate_score,
                "raw_scores": score.raw_scores,
                "normalized_scores": score.normalized_scores,
            },
            "assessments": [
                {
                    "id": assessment.id,
                    "status": assessment.status,
                    "title": assessment.title,
                    "task_ids": assessment.task_ids,
                }
                for assessment in assessments
            ],
        }
    )


@router.get("/candidates/{candidate_id}/task-runs")
def get_dashboard_task_runs_route(
    candidate_id: str,
    user=Depends(require_roles("admin", "reviewer")),
    db: Session = Depends(get_db),
) -> dict:
    rows = get_candidate_task_runs(db, user.organization_id, candidate_id)
    return envelope(
        [
            {
                "task_run": {
                    "id": row["task_run"].id,
                    "task_id": row["task_run"].task_id,
                    "status": row["task_run"].status,
                    "started_at": row["task_run"].started_at.isoformat(),
                    "completed_at": row["task_run"].completed_at.isoformat()
                    if row["task_run"].completed_at
                    else None,
                },
                "evaluation": None
                if row["evaluation"] is None
                else {
                    "dimension_scores": row["evaluation"].dimension_scores,
                    "total_score": row["evaluation"].total_score,
                },
                "latest_simulation": None
                if row["latest_simulation"] is None
                else {
                    "response_text": row["latest_simulation"].response_text,
                    "confidence_score": row["latest_simulation"].confidence_score,
                },
            }
            for row in rows
        ]
    )


@router.get("/task-runs/{task_run_id}/replay")
def get_dashboard_replay_route(
    task_run_id: str,
    user=Depends(require_roles("admin", "reviewer")),
    db: Session = Depends(get_db),
) -> dict:
    replay = get_session_replay(db, user.organization_id, task_run_id)
    return envelope(
        {
            "events": [
                {
                    "id": event.id,
                    "event_type": event.event_type,
                    "monotonic_timestamp_ms": event.monotonic_timestamp_ms,
                    "payload": event.payload,
                    "created_at": event.created_at.isoformat(),
                }
                for event in replay["events"]
            ],
            "simulation_runs": [
                {
                    "id": run.id,
                    "query_text": run.query_text,
                    "prompt_text": run.prompt_text,
                    "response_text": run.response_text,
                    "retrieved_chunks": run.retrieved_chunks,
                    "debug_logs": run.debug_logs,
                    "confidence_score": run.confidence_score,
                }
                for run in replay["simulation_runs"]
            ],
            "evaluation": None
            if replay["evaluation"] is None
            else {
                "dimension_scores": replay["evaluation"].dimension_scores,
                "formulas": replay["evaluation"].formulas,
                "total_score": replay["evaluation"].total_score,
            },
        }
    )
