"""Assessment service — CRUD operations for assessments."""

from typing import Dict, List, Optional

from sqlalchemy.orm import Session as DbSession
from fastapi import HTTPException

from app.assessment.models import Assessment, AssessmentTask


def create_assessment(db: DbSession, candidate_id: str, session_id: str,
                      task_ids: List[str], org_id: str = None) -> Assessment:
    """Create an assessment and initialize its ordered task list."""
    assessment = Assessment(
        candidate_id=candidate_id,
        session_id=session_id,
        organization_id=org_id,
        status="created",
    )
    db.add(assessment)
    db.flush()  # get id

    for idx, task_id in enumerate(task_ids):
        db.add(AssessmentTask(
            assessment_id=assessment.id,
            task_id=task_id,
            order_index=idx,
            status="pending",
        ))

    db.commit()
    db.refresh(assessment)
    return assessment


def get_assessment(db: DbSession, assessment_id: str) -> Assessment:
    """Retrieve an assessment by ID."""
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment


def get_assessment_tasks(db: DbSession, assessment_id: str) -> List[AssessmentTask]:
    """Get all tasks for an assessment in order."""
    return (
        db.query(AssessmentTask)
        .filter(AssessmentTask.assessment_id == assessment_id)
        .order_by(AssessmentTask.order_index)
        .all()
    )


def get_current_task(db: DbSession, assessment_id: str) -> Optional[AssessmentTask]:
    """Get the currently running task."""
    return (
        db.query(AssessmentTask)
        .filter(
            AssessmentTask.assessment_id == assessment_id,
            AssessmentTask.status == "running",
        )
        .first()
    )


def get_next_pending_task(db: DbSession, assessment_id: str) -> Optional[AssessmentTask]:
    """Get the next pending task in order."""
    return (
        db.query(AssessmentTask)
        .filter(
            AssessmentTask.assessment_id == assessment_id,
            AssessmentTask.status == "pending",
        )
        .order_by(AssessmentTask.order_index)
        .first()
    )
