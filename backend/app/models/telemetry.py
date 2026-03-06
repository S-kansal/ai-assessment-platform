import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from app.database import Base


class TelemetryEvent(Base):
    """A single telemetry event captured during an assessment session."""

    __tablename__ = "telemetry_events"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    organization_id = Column(
        String(36), ForeignKey("organizations.id"), nullable=True,
    )
    session_id = Column(
        String(36),
        ForeignKey("sessions.id"),
        nullable=False,
    )
    task_id = Column(String(64), nullable=False)
    event_type = Column(String(32), nullable=False)
    timestamp = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    payload_json = Column(JSON, nullable=False, default=dict)
