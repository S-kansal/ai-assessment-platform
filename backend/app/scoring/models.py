"""Database models for scoring engine."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from app.database import Base


class TaskScore(Base):
    """Stores the computed score for a single task run."""

    __tablename__ = "task_scores"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(
        String(36), ForeignKey("organizations.id"), nullable=True,
    )
    task_run_id = Column(
        String(36),
        ForeignKey("task_runs.id"),
        nullable=False,
    )
    task_id = Column(String(64), nullable=False)
    task_score = Column(Float, nullable=False, default=0.0)
    capability = Column(String(64), nullable=True)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class CandidateScore(Base):
    """Stores a single capability score for a candidate."""

    __tablename__ = "candidate_scores"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(
        String(36), ForeignKey("organizations.id"), nullable=True,
    )
    candidate_id = Column(
        String(36),
        ForeignKey("candidates.id"),
        nullable=False,
    )
    capability = Column(String(64), nullable=False)
    score = Column(Float, nullable=False, default=0.0)
    sample_size = Column(Integer, nullable=False, default=0)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

