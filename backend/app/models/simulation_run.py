from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, BigInteger, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

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
        index=True,
        nullable=False,
    )
    candidate_id: Mapped[str] = mapped_column(
        ForeignKey("candidates.id"),
        index=True,
        nullable=False,
    )
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    retrieved_chunks: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    debug_logs: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    response_text: Mapped[str] = mapped_column(Text, nullable=False)
    output_quality: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    confidence_score: Mapped[float] = mapped_column(nullable=False, default=0.0)
    seed: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    task_run: Mapped["TaskRun"] = relationship(back_populates="simulation_runs")
