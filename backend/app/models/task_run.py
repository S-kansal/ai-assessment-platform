import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer
from app.database import Base


class TaskRun(Base):
    """Tracks execution of a single task within an assessment session."""

    __tablename__ = "task_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(
        String(36), ForeignKey("organizations.id"), nullable=True,
    )
    session_id = Column(
        String(36),
        ForeignKey("sessions.id"),
        nullable=False,
    )
    task_id = Column(
        String(64),
        ForeignKey("tasks.id"),
        nullable=False,
    )
    attempt_number = Column(Integer, default=1, nullable=False)
    started_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(32), default="pending", nullable=False)
    solution = Column(Text, nullable=True)
