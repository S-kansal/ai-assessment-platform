from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class TaskRun(Base):
    __tablename__ = "task_runs"

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
    candidate_id: Mapped[str] = mapped_column(
        ForeignKey("candidates.id"),
        index=True,
        nullable=False,
    )
    task_id: Mapped[str] = mapped_column(
        ForeignKey("tasks.id"),
        index=True,
        nullable=False,
    )
    sequence_index: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    final_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    final_query: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_fix_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    assessment: Mapped["Assessment"] = relationship(back_populates="task_runs")
    task: Mapped["Task"] = relationship(back_populates="task_runs")
    simulation_runs: Mapped[list["SimulationRun"]] = relationship(back_populates="task_run")
    telemetry_events: Mapped[list["TelemetryEvent"]] = relationship(back_populates="task_run")
