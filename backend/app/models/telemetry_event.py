from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, BigInteger, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class TelemetryEvent(Base):
    __tablename__ = "telemetry_events"

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
    session_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    monotonic_timestamp_ms: Mapped[int] = mapped_column(BigInteger, nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    task_run: Mapped["TaskRun"] = relationship(back_populates="telemetry_events")
