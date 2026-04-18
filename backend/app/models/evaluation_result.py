from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id"),
        index=True,
        nullable=False,
    )
    assessment_id: Mapped[str] = mapped_column(
        ForeignKey("assessments.id"),
        index=True,
        nullable=False,
    )
    task_run_id: Mapped[str] = mapped_column(
        ForeignKey("task_runs.id"),
        unique=True,
        index=True,
        nullable=False,
    )
    candidate_id: Mapped[str] = mapped_column(
        ForeignKey("candidates.id"),
        index=True,
        nullable=False,
    )
    dimension_scores: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    formulas: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    evidence: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    total_score: Mapped[float] = mapped_column(nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
