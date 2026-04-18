from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ScoringResult(Base):
    __tablename__ = "scoring_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id"),
        index=True,
        nullable=False,
    )
    assessment_id: Mapped[str] = mapped_column(
        ForeignKey("assessments.id"),
        unique=True,
        index=True,
        nullable=False,
    )
    candidate_id: Mapped[str] = mapped_column(
        ForeignKey("candidates.id"),
        index=True,
        nullable=False,
    )
    raw_scores: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    normalized_scores: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    aggregate_score: Mapped[float] = mapped_column(nullable=False, default=0.0)
    weighting_version: Mapped[str] = mapped_column(String(32), nullable=False, default="v1")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
