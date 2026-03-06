"""Database models for assessment orchestrator."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from app.database import Base


class Assessment(Base):
    """Top-level multi-task assessment for a candidate."""

    __tablename__ = "assessments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(
        String(36), ForeignKey("organizations.id"), nullable=True,
    )
    candidate_id = Column(
        String(36), ForeignKey("candidates.id"), nullable=False,
    )
    session_id = Column(
        String(36), ForeignKey("sessions.id"), nullable=False,
    )
    status = Column(String(20), nullable=False, default="created")  # created | running | completed | failed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)


class AssessmentTask(Base):
    """Links an assessment to its ordered list of tasks."""

    __tablename__ = "assessment_tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id = Column(
        String(36), ForeignKey("assessments.id"), nullable=False,
    )
    task_id = Column(String(64), nullable=False)
    task_run_id = Column(String(36), nullable=True)       # set when task is started
    order_index = Column(Integer, nullable=False, default=0)
    status = Column(String(20), nullable=False, default="pending")  # pending | running | completed | failed
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
