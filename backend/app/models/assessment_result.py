"""Database model for assessment result snapshots."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON
from app.database import Base


class AssessmentResult(Base):
    """Stores a complete assessment result snapshot per assessment."""

    __tablename__ = "assessment_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id = Column(
        String(36),
        ForeignKey("assessments.id"),
        nullable=True,
    )
    candidate_id = Column(
        String(36),
        ForeignKey("candidates.id"),
        nullable=False,
    )
    session_id = Column(
        String(36),
        ForeignKey("sessions.id"),
        nullable=False,
    )
    final_score = Column(Float, nullable=True)
    capability_profile = Column(JSON, nullable=True)
    evaluation_summary = Column(JSON, nullable=True)
    completed_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
