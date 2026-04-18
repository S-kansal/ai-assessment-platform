from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import (
    AuthContext,
    envelope,
    get_current_user,
    get_db,
    require_candidate_self,
    require_roles,
)
from app.core.exceptions import AuthorizationError
from app.schemas.assessment import AssessmentCreateRequest
from app.schemas.assessment import AssessmentSubmitRequest
from app.services.assessments import (
    create_and_start_assessment,
    get_active_task_run,
    get_assessment,
    submit_assessment_task,
    timeout_expired_assessment,
)


router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.post("")
def create_assessment_route(
    body: AssessmentCreateRequest,
    user: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    if user.role == "candidate":
        require_candidate_self(body.candidate_id, user)
    elif user.role != "admin":
        raise AuthorizationError("Only admins or the candidate can start an assessment")

    assessment, active_task_run = create_and_start_assessment(
        db,
        user.organization_id,
        body.candidate_id,
        body.title,
        body.order_mode,
        body.browser_session_id,
    )
    db.commit()
    return envelope(
        {
            "assessment_id": assessment.id,
            "status": assessment.status,
            "candidate_id": assessment.candidate_id,
            "task_ids": assessment.task_ids,
            "active_task_run_id": active_task_run.id,
            "active_task_id": active_task_run.task_id,
        }
    )


@router.get("/{assessment_id}")
def get_assessment_route(
    assessment_id: str,
    user: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    assessment = get_assessment(db, user.organization_id, assessment_id)
    require_candidate_self(assessment.candidate_id, user)
    active_task_run = get_active_task_run(db, user.organization_id, assessment_id)
    return envelope(
        {
            "id": assessment.id,
            "candidate_id": assessment.candidate_id,
            "title": assessment.title,
            "status": assessment.status,
            "order_mode": assessment.order_mode,
            "task_ids": assessment.task_ids,
            "current_task_index": assessment.current_task_index,
            "assigned_at": assessment.assigned_at.isoformat(),
            "started_at": assessment.started_at.isoformat() if assessment.started_at else None,
            "completed_at": assessment.completed_at.isoformat() if assessment.completed_at else None,
            "expires_at": assessment.expires_at.isoformat() if assessment.expires_at else None,
            "active_task_run_id": active_task_run.id if active_task_run else None,
        }
    )


@router.post("/{assessment_id}/submit")
def submit_assessment_route(
    assessment_id: str,
    body: AssessmentSubmitRequest,
    user: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    assessment = get_assessment(db, user.organization_id, assessment_id)
    require_candidate_self(assessment.candidate_id, user)
    assessment, next_task_run = submit_assessment_task(
        db,
        user.organization_id,
        assessment_id,
        body.task_run_id,
        body.final_prompt,
        body.final_query,
        body.submitted_root_cause,
        body.submitted_fix_summary,
    )
    db.commit()
    return envelope(
        {
            "assessment_id": assessment.id,
            "status": assessment.status,
            "next_task_run_id": next_task_run.id if next_task_run else None,
            "next_task_id": next_task_run.task_id if next_task_run else None,
            "completed_at": assessment.completed_at.isoformat() if assessment.completed_at else None,
        }
    )


@router.post("/{assessment_id}/timeout")
def timeout_assessment_route(
    assessment_id: str,
    user: AuthContext = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> dict:
    assessment = timeout_expired_assessment(db, user.organization_id, assessment_id)
    db.commit()
    return envelope(
        {
            "assessment_id": assessment.id,
            "status": assessment.status,
            "completed_at": assessment.completed_at.isoformat() if assessment.completed_at else None,
        }
    )
