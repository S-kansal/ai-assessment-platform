from sqlalchemy import select
from sqlalchemy.orm import Session

from app.assessment.orchestrator import (
    create_assessment,
    finalize_task_and_advance,
    start_assessment as start_assessment_run,
    submit_task_run,
    timeout_assessment,
)
from app.core.exceptions import ConflictError, NotFoundError
from app.models.assessment import Assessment
from app.models.task_run import TaskRun


def create_and_start_assessment(
    db: Session,
    organization_id: str,
    candidate_id: str,
    title: str,
    order_mode: str,
    browser_session_id: str,
) -> tuple[Assessment, TaskRun]:
    assessment = create_assessment(
        db,
        organization_id,
        candidate_id,
        title,
        order_mode,
        browser_session_id,
    )
    task_run = start_assessment_run(db, assessment)
    return assessment, task_run


def get_assessment(db: Session, organization_id: str, assessment_id: str) -> Assessment:
    assessment = db.scalar(
        select(Assessment).where(
            Assessment.id == assessment_id,
            Assessment.organization_id == organization_id,
        )
    )
    if assessment is None:
        raise NotFoundError("Assessment not found")
    return assessment


def get_active_task_run(
    db: Session,
    organization_id: str,
    assessment_id: str,
) -> TaskRun | None:
    return db.scalar(
        select(TaskRun).where(
            TaskRun.organization_id == organization_id,
            TaskRun.assessment_id == assessment_id,
            TaskRun.status == "active",
        )
    )


def submit_assessment_task(
    db: Session,
    organization_id: str,
    assessment_id: str,
    task_run_id: str,
    final_prompt: str,
    final_query: str,
    submitted_root_cause: str,
    submitted_fix_summary: str,
) -> tuple[Assessment, TaskRun | None]:
    assessment = get_assessment(db, organization_id, assessment_id)
    task_run = db.scalar(
        select(TaskRun).where(
            TaskRun.id == task_run_id,
            TaskRun.organization_id == organization_id,
            TaskRun.assessment_id == assessment_id,
        )
    )
    if task_run is None:
        raise NotFoundError("Task run not found")
    if task_run.status != "active":
        raise ConflictError("Task run is not active")

    submit_task_run(
        db,
        task_run,
        final_prompt,
        final_query,
        submitted_root_cause,
        submitted_fix_summary,
    )
    next_task_run, _completed = finalize_task_and_advance(db, assessment, task_run)
    return assessment, next_task_run


def timeout_expired_assessment(
    db: Session,
    organization_id: str,
    assessment_id: str,
) -> Assessment:
    assessment = get_assessment(db, organization_id, assessment_id)
    timeout_assessment(assessment)
    return assessment
