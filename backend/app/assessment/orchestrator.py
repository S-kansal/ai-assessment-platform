from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.assessment.sequencer import build_task_sequence
from app.core.exceptions import ConflictError, NotFoundError
from app.evaluation.engine import evaluate_task_run
from app.models.assessment import Assessment
from app.models.task import Task
from app.models.task_run import TaskRun
from app.scoring.engine import compute_scoring_result
from app.tasks.definitions import list_task_definitions
from app.tasks.lifecycle import (
    complete_status,
    get_assessment_expiry,
    start_status,
    timeout_status,
)


def tenant_task_id(organization_id: str, definition_id: str) -> str:
    return f"{organization_id.split('-', 1)[0]}:{definition_id}"


def ensure_task_catalog(db: Session, organization_id: str) -> None:
    existing_task_ids = {
        task.id
        for task in db.scalars(
            select(Task).where(Task.organization_id == organization_id)
        )
    }
    for definition in list_task_definitions():
        scoped_task_id = tenant_task_id(organization_id, definition["id"])
        if scoped_task_id in existing_task_ids:
            continue
        db.add(
            Task(
                id=scoped_task_id,
                organization_id=organization_id,
                title=definition["title"],
                task_type=definition["task_type"],
                failure_modes=definition["failure_modes"],
                expected_diagnostic_path=definition["expected_diagnostic_path"],
                scoring_rubric=definition["rubric"],
                scenario_key=definition["scenario_key"],
            )
        )
    db.flush()


def create_assessment(
    db: Session,
    organization_id: str,
    candidate_id: str,
    title: str,
    order_mode: str,
    browser_session_id: str,
) -> Assessment:
    ensure_task_catalog(db, organization_id)
    task_ids = [
        tenant_task_id(organization_id, definition_id)
        for definition_id in build_task_sequence(order_mode)
    ]
    assessment = Assessment(
        organization_id=organization_id,
        candidate_id=candidate_id,
        title=title,
        order_mode=order_mode,
        task_ids=task_ids,
        browser_session_id=browser_session_id,
        status="created",
        expires_at=get_assessment_expiry(),
    )
    db.add(assessment)
    db.flush()
    return assessment


def start_assessment(db: Session, assessment: Assessment) -> TaskRun:
    if assessment.status not in {"created", "active"}:
        raise ConflictError("Assessment cannot be started from its current state")
    assessment.status = "active"
    assessment.started_at = assessment.started_at or datetime.now(timezone.utc)
    return start_next_task_run(db, assessment)


def start_next_task_run(db: Session, assessment: Assessment) -> TaskRun:
    if assessment.current_task_index >= len(assessment.task_ids):
        raise ConflictError("Assessment has no remaining tasks")
    task_id = assessment.task_ids[assessment.current_task_index]
    task_run = TaskRun(
        organization_id=assessment.organization_id,
        assessment_id=assessment.id,
        candidate_id=assessment.candidate_id,
        task_id=task_id,
        sequence_index=assessment.current_task_index,
        status=start_status(),
        expires_at=assessment.expires_at,
    )
    db.add(task_run)
    db.flush()
    return task_run


def submit_task_run(
    db: Session,
    task_run: TaskRun,
    final_prompt: str,
    final_query: str,
    submitted_root_cause: str,
    submitted_fix_summary: str,
) -> TaskRun:
    task_run.final_prompt = final_prompt
    task_run.final_query = final_query
    task_run.submitted_root_cause = submitted_root_cause
    task_run.submitted_fix_summary = submitted_fix_summary
    task_run.status = complete_status()
    task_run.completed_at = datetime.now(timezone.utc)
    db.flush()
    return task_run


def finalize_task_and_advance(
    db: Session,
    assessment: Assessment,
    task_run: TaskRun,
) -> tuple[TaskRun | None, bool]:
    task = db.scalar(
        select(Task).where(
            Task.id == task_run.task_id,
            Task.organization_id == task_run.organization_id,
        )
    )
    if task is None:
        raise NotFoundError("Task not found for task run")

    evaluate_task_run(db, task_run, task)
    assessment.current_task_index += 1
    if assessment.current_task_index >= len(assessment.task_ids):
        assessment.status = "completed"
        assessment.completed_at = datetime.now(timezone.utc)
        compute_scoring_result(db, assessment.id, assessment.organization_id)
        db.flush()
        return None, True

    next_task_run = start_next_task_run(db, assessment)
    db.flush()
    return next_task_run, False


def timeout_assessment(assessment: Assessment) -> None:
    assessment.status = timeout_status()
    assessment.completed_at = datetime.now(timezone.utc)
